import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import os
from typing import Tuple

IMAGE_SIZE = 224


class FatigueClassifier:
    def __init__(self, model_path: str = None):
        self.model_path = model_path or os.path.join(
            os.path.dirname(__file__), "..", "..", "models", "best_model.pth"
        )
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.transform = transforms.Compose([
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

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
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(image_tensor)
            probs = torch.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probs, 1)
        
        return predicted.item(), confidence.item()

    def predict_image_from_bytes(self, image_bytes) -> Tuple[int, float]:
        if self.model is None:
            self.load()
        
        image = Image.open(image_bytes).convert('RGB')
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(image_tensor)
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
