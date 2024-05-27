import torch
import torchvision
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from model import SimpleCNN  # Ensure this import matches the file name and class name
import os

def evaluate():
    # Define transformations
    transform = transforms.Compose([
        transforms.Grayscale(),  # Converts images to grayscale
        transforms.Resize((28, 28)),  # Resizes images to 28x28 pixels
        transforms.ToTensor(),  # Converts images to Tensor format
        transforms.Normalize((0.5,), (0.5,))  # Normalizes the tensor
    ])

    # Load validation data from specified path
    val_dataset = datasets.ImageFolder(r'C:/Users/ltper/OneDrive/Desktop/cnn/val', transform=transform)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

    # Load model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SimpleCNN().to(device)
    
    # Ensure the directory exists and the model path is correct
    model_path = r'C:/Users/ltper/OneDrive/Desktop/cnn/models'
    if os.path.isfile(model_path):
        model.load_state_dict(torch.load(model_path))
        model.eval()

        # Evaluate the model
        correct = 0
        total = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        print(f'Accuracy of the network on the validation images: {100 * correct / total}%')
    else:
        print("Model file not found. Please check the path.")

if __name__ == "__main__":
    evaluate()
