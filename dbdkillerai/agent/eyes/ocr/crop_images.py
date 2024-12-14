import cv2

def crop_bottom_center(image, width_fraction=0.3, height_fraction=0.1):
    """
    Crop the bottom center portion of the image.

    :param image: Input image
    :param width_fraction: Fraction of the image width for the crop (0-1)
    :param height_fraction: Fraction of the image height for the crop (0-1)
    :return: Cropped image
    """
    h, w = image.shape

    # Calculate crop dimensions
    crop_width = int(w * width_fraction)
    crop_height = int(h * height_fraction)

    # Calculate crop coordinates for bottom center
    x_start = (w - crop_width) // 2
    y_start = h - crop_height
    x_end = x_start + crop_width
    y_end = y_start + crop_height

    # Crop the image
    cropped_image = image[y_start:y_end, x_start:x_end]

    return cropped_image

if __name__ == "__main__":
    # Load an image (replace 'image.jpg' with your image path)
    image_path = '/Users/mreagles524/Documents/gitrepos/projects/DBD-Killer-AI/test/eyes/damage.png'
    image = cv2.imread(image_path)

    if image is None:
        print("Error: Could not load image. Check the path.")
        exit()

    # Crop the bottom center portion
    cropped_image = crop_bottom_center(image)

    # Display original and cropped images
    cv2.imshow("Original Image", image)
    cv2.imshow("Cropped Image - Bottom Center", cropped_image)

    # Wait for a key press and close windows
    cv2.waitKey(0)
    cv2.destroyAllWindows()
