import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, random_split
from torchvision import transforms, models
from PIL import Image
import numpy as np
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

DATASET_PATH = r"C:\Users\kript\.cache\kagglehub\datasets\rihabkaci99\fatigue-dataset\versions\1\Data"
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")
os.makedirs(MODEL_DIR, exist_ok=True)

IMAGE_SIZE = 224
BATCH_SIZE = 32
NUM_EPOCHS = 10
LEARNING_RATE = 0.001


class FatigueDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.fatigue_dir = os.path.join(root_dir, "Fatigue")
        self.nonfatigue_dir = os.path.join(root_dir, "NonFatigue")
        
        self.fatigue_images = [os.path.join(self.fatigue_dir, f) 
                               for f in os.listdir(self.fatigue_dir) 
                               if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        self.nonfatigue_images = [os.path.join(self.nonfatigue_dir, f) 
                                  for f in os.listdir(self.nonfatigue_dir) 
                                  if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        self.image_paths = self.fatigue_images + self.nonfatigue_images
        self.labels = [1] * len(self.fatigue_images) + [0] * len(self.nonfatigue_images)
        
        print(f"Dataset loaded: {len(self.fatigue_images)} Fatigue, {len(self.nonfatigue_images)} NonFatigue")

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert('RGB')
        label = self.labels[idx]

        if self.transform:
            image = self.transform(image)

        return image, label


def get_transforms():
    train_transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    return train_transform, val_transform


def create_model():
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, 2)
    return model


def train_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in tqdm(dataloader, desc="Training"):
        images, labels = images.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

    return running_loss / len(dataloader), 100. * correct / total


def evaluate(model, dataloader, criterion, device):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in tqdm(dataloader, desc="Evaluating"):
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

    return running_loss / len(dataloader), 100. * correct / total


def train_model():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    train_transform, val_transform = get_transforms()
    dataset = FatigueDataset(DATASET_PATH, transform=train_transform)
    
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    
    val_dataset.dataset.transform = val_transform

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    model = create_model().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    best_acc = 0.0
    
    for epoch in range(NUM_EPOCHS):
        print(f"\nEpoch {epoch+1}/{NUM_EPOCHS}")
        print("-" * 30)
        
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = evaluate(model, val_loader, criterion, device)

        print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
        print(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")

        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), os.path.join(MODEL_DIR, "best_model.pth"))
            print(f"Model saved with best accuracy: {best_acc:.2f}%")

    print(f"\n{'='*50}")
    print(f"Training completed! Best Val Accuracy: {best_acc:.2f}%")
    
    torch.save({
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'best_acc': best_acc,
    }, os.path.join(MODEL_DIR, "full_model.pth"))
    
    return model, best_acc


if __name__ == "__main__":
    train_model()
