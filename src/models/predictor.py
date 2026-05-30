import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import os
import cv2
import numpy as np
from typing import Tuple

IMAGE_SIZE = 224
FACE_MIN_SIZE = 60
NONFACE_CONFIDENCE = 0.55


class FatigueClassifier:
    def __init__(self, model_path: str = None):
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), "..", "..", "models", "best_model.pth"
        )
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.face_cascade = None
        self.transform = transforms.Compose([
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def _init_face_detector(self):
        if self.face_cascade is not None:
            return
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        if os.path.exists(cascade_path):
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
        else:
            self.face_cascade = None
            print("Warning: Face cascade not found, skipping face detection")

    def _has_face(self, image: Image.Image) -> bool:
        self._init_face_detector()
        if self.face_cascade is None:
            return True
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(FACE_MIN_SIZE, FACE_MIN_SIZE)
        )
        if len(faces) > 0:
            return True
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.05, minNeighbors=3, minSize=(30, 30)
        )
        if len(faces) > 0:
            return True
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        lower_skin = np.array([0, 20, 50], dtype=np.uint8)
        upper_skin = np.array([50, 150, 255], dtype=np.uint8)
        skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
        skin_ratio = cv2.countNonZero(skin_mask) / (img_array.shape[0] * img_array.shape[1])
        return skin_ratio > 0.15

    def _check_ood(self, logits: torch.Tensor) -> bool:
        probs = torch.softmax(logits, dim=1)
        max_prob, _ = torch.max(probs, 1)
        entropy = -(probs * torch.log(probs + 1e-10)).sum(dim=1)
        max_logit, _ = torch.max(logits, 1)
        logit_margin = max_logit - torch.min(logits, 1)[0]
        is_overconfident = max_prob.item() > 0.99
        low_entropy = entropy.item() < 0.15
        high_margin = logit_margin.item() > 8.0
        return is_overconfident and (low_entropy or high_margin)

    def _create_model(self):
        model = models.resnet18(weights=None)
        num_features = model.fc.in_features
        model.fc = nn.Linear(num_features, 2)
        return model

    def load(self):
        self.model = self._create_model()
        self.model.load_state_dict(torch.load(self.model_path, map_location=self.device, weights_only=True))
        self.model.to(self.device)
        self.model.eval()
        print(f"Model loaded from {self.model_path}")

    def predict_image(self, image_path: str) -> Tuple[int, float]:
        if self.model is None:
            self.load()

        image = Image.open(image_path).convert('RGB')
        if not self._has_face(image):
            return 0, NONFACE_CONFIDENCE

        image_tensor = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(image_tensor)
            if self._check_ood(outputs):
                return 0, NONFACE_CONFIDENCE
            probs = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probs, 1)

        return predicted.item(), confidence.item()

    def predict_image_from_bytes(self, image_bytes) -> Tuple[int, float]:
        if self.model is None:
            self.load()

        image = Image.open(image_bytes).convert('RGB')
        if not self._has_face(image):
            return 0, NONFACE_CONFIDENCE

        image_tensor = self.transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(image_tensor)
            if self._check_ood(outputs):
                return 0, NONFACE_CONFIDENCE
            probs = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probs, 1)

        return predicted.item(), confidence.item()


if __name__ == "__main__":
    classifier = FatigueClassifier()
    try:
        classifier.load()
        
        test_path = r"C:\Users\kript\.cache\kagglehub\datasets\rihabkaci99\fatigue-dataset\versions\1\Data\Fatigue\0001.jpg"
        if os.path.exists(test_path):
            pred, conf = classifier.predict_image(test_path)
            label = "Fatigue" if pred == 1 else "NonFatigue"
            print(f"Prediction: {label}, Confidence: {conf:.2%}")
    except Exception as e:
        print(f"Error: {e}")
        print("Please run train_model.py first to train the model.")
