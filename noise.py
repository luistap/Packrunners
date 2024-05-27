# MAIN UTILITIES MODULE
# UTILITIES: NOISE REDUCTION, CONTRAST ENHANCEMENT, AND IMAGE INVERSION

import cv2

def apply_bilateral_filter(image_path, d, sigma_color, sigma_space, save_path):
    """
    Apply bilateral filtering to an image and save it.

    Args:
    image_path (str): Path to the input image.
    d (int): Diameter of each pixel neighborhood.
    sigma_color (float): Filter sigma in the color space.
    sigma_space (float): Filter sigma in the coordinate space.
    save_path (str): Path to save the filtered image.
    """
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image not found, check the path.")

    # Apply bilateral filter
    output_image = cv2.bilateralFilter(image, d=d, sigmaColor=sigma_color, sigmaSpace=sigma_space)

    # Save the filtered image
    cv2.imwrite(save_path, output_image)
    print(f"Filtered image saved to {save_path}")

# Usage
image_path = "C:/Users/ltper/PCKSTATS/chars_cropped/row_5_char_2.png"  
# Update this to the path of your image
save_path = 'path_to_save_filtered_image.png'  # Update this to where you want to save the filtered image

# Parameters for bilateral filter
diameter = 9  # Diameter of each pixel neighborhood
sigma_color = 75  # Filter sigma in the color space
sigma_space = 75  # Filter sigma in the coordinate space

# Apply the filter and save the output
apply_bilateral_filter(image_path, diameter, sigma_color, sigma_space, save_path)
