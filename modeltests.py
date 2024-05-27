import cv2
import io
import os
import torch
import torchvision.transforms as transforms
from PIL import Image  # Importing PIL
from model import SimpleCNN
import utilities

def process_stats(image_path, model_path):
    # Load the image
    img = cv2.imread(image_path)
    # Assuming img is already preprocessed (cropped to stats area, thresholded, etc.)

    # Height of each row
    row_height = img.shape[0] // 5

    # Create directory for cropped character images
    cropped_dir = 'chars_cropped'
    if not os.path.exists(cropped_dir):
        os.makedirs(cropped_dir)

    # Load the trained model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SimpleCNN().to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    # Define the transformation for the character images
    transform = transforms.Compose([
        transforms.Grayscale(),  # Convert to grayscale
        transforms.Resize((28, 28)),  # Resize to 28x28 pixels
        transforms.ToTensor(),  # Convert to tensor
        transforms.Normalize((0.5,), (0.5,))  # Normalize the tensor
    ])

    stats = []
    for i in range(5):  # Assuming 5 rows of players
        row_img = img[i*row_height:(i+1)*row_height, :]

        # Assuming there are 3 numbers per row and calculating the approximate width of each number
        char_width = row_img.shape[1] // 3

        row_stats = []  # Temporary list to hold stats for a single row
        for j in range(3):  # Assuming 3 characters per row
            # Crop the character more tightly
            # Adjust margins to zoom closer
            margin_w = int(0.1 * char_width)  # Adjust margin as needed
            margin_h = int(0.1 * row_height)  # Adjust margin as needed

            char_img = row_img[margin_h:-margin_h, (j*char_width+margin_w):((j+1)*char_width-margin_w)]

            # Save the cropped character image as PNG
            char_path = os.path.join(cropped_dir, f'row_{i+1}_char_{j+1}.png')
            cv2.imwrite(char_path, char_img)

            # Convert the character image to bytes for PNG
            _, buffer = cv2.imencode('.png', char_img)
            byte_img = io.BytesIO(buffer).getvalue()

            # Use the detect_text function to OCR the character
            char_text = utilities.detect_text_byte(byte_img)

            # Convert NumPy array to PIL image
            char_img_pil = Image.fromarray(cv2.cvtColor(char_img, cv2.COLOR_BGR2RGB))

            # Preprocess the character image for model prediction
            char_tensor = transform(char_img_pil)
            char_tensor = char_tensor.unsqueeze(0).to(device)  # Add batch dimension and move to device

            # Model prediction
            with torch.no_grad():
                output = model(char_tensor)
                _, predicted = torch.max(output, 1)
                predicted_char = str(predicted.item())

                # Print raw output probabilities/logits
                print(f'Raw model output: {output}')
                print(f'Predicted class: {predicted_char}')

                # Use OCR output for characters other than '9' or '6'
                if predicted_char in ['9', '6']:
                    row_stats.append(predicted_char)
                else:
                    row_stats.append(char_text)

            print(f'OCR output: {char_text}, Model prediction: {predicted_char}')

        stats.append(row_stats)  # Add the completed row to the overall stats

    return stats

def convert_path(path):
    return path.replace("\\", "/")

# Example usage:
image_path = convert_path(r"C:\Users\ltper\Downloads\image (32).png")
model_path = 'C:/Users/ltper/OneDrive/Desktop/cnn/models'
stats = process_stats(image_path, model_path)
print(stats)
