import os
import torch
import torchvision
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import torch.optim as optim
from model import SimpleCNN  # Ensure this import matches the file name and class name
import torch.nn as nn  # Added to ensure nn is recognized for CrossEntropyLoss

NUM_EPOCHS = 140

def train():
    # Define transformations
    transform = transforms.Compose([
        transforms.Grayscale(),  # Converts images to grayscale
        transforms.Resize((28, 28)),  # Resizes images to 28x28 pixels
        transforms.ToTensor(),  # Converts images to Tensor format
        transforms.Normalize((0.5,), (0.5,))  # Normalizes the tensor
    ])

    # Load training data from specified path
    train_dataset = datasets.ImageFolder(r'C:/Users/ltper/OneDrive/Desktop/cnn/train', transform=transform)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

    # Set up the model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SimpleCNN().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Training loop
    for epoch in range(NUM_EPOCHS):  # You might want to adjust the number of epochs
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
        print(f'Epoch {epoch+1}, Loss: {loss.item()}')

    # Ensure the directory exists before saving the model
    save_path = r'C:/Users/ltper/OneDrive/Desktop/cnn/models'
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Save the trained model to a specified path
    torch.save(model.state_dict(), save_path)

if __name__ == "__main__":
    train()
