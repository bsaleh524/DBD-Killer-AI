from PIL import Image
import os

def calculate_aspect_ratio(width, height):
    return width / height

def calculate_area(width, height):
    return width * height

def process_images(directory):
    for filename in os.listdir(directory):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            file_path = os.path.join(directory, filename)

            # Open the image
            with Image.open(file_path) as img:
                # Get image size
                width, height = img.size

                # Calculate aspect ratio and area
                aspect_ratio = calculate_aspect_ratio(width, height)
                area = calculate_area(width, height)

                # Print or store the results
                print(f"Image: {filename}")
                print(f"Aspect Ratio: {aspect_ratio:.2f}")
                print(f"Area: {area} square pixels")
                print()