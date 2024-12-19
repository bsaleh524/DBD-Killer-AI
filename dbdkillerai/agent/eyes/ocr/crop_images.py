import cv2

def crop_bottom_center(image, width_fraction=0.3, height_fraction=0.15):
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

def crop_top_right(image, width_fraction=0.15, height_fraction=0.33):
    """
    Crop the top-right portion of the image.

    :param image: Input image
    :param width_fraction: Fraction of the image width for the crop (0-1)
    :param height_fraction: Fraction of the image height for the crop (0-1)
    :return: Cropped image
    """
    h, w = image.shape

    # Calculate crop dimensions
    crop_width = int(w * width_fraction)
    crop_height = int(h * height_fraction)

    # Calculate crop coordinates for top right
    x_start = w - crop_width
    y_start = 0
    x_end = w
    y_end = crop_height

    # Crop the image
    cropped_image = image[y_start:y_end, x_start:x_end]

    return cropped_image


if __name__ == "__main__":
    # Load an image (replace 'image.jpg' with your image path)
    image_path = '/Users/mreagles524/Documents/gitrepos/projects/DBD-Killer-AI/test/eyes/ocr_test.png'
    image = cv2.imread(image_path)

    # Convert to grayscale for better imaging
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Crop the images
    cropped_image_bottom = crop_bottom_center(gray)
    cropped_image_topright = crop_top_right(gray)

    # Display original and cropped images
    cv2.imshow("Original Image", image)
    cv2.imshow("Cropped Image - Bottom Center", cropped_image_bottom)
    cv2.imshow("Cropped Image - Top Right", cropped_image_topright)

    # Wait for a key press and close windows
    cv2.waitKey(0)
    cv2.destroyAllWindows()
