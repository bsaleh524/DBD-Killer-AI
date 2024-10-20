"""Reads Action text and responds with key upon detected text during desired states."""

import easyocr
import cv2
import yaml

def get_interaction_text(reader: easyocr.Reader, image, command_dict):
    """Read the text from the given screencapture frame/image and return key."""
    result = reader.readtext(image)

    # Detect text
    for (bbox, text, prob) in result:
        print(f"Detected Text: {text} (Confidence: {prob:.2f})")

        if text.lower() in command_dict.keys():
            print(f"{text.lower()} Detected!")  # Detected text matches command
            return command_dict[text.lower()] #TODO: Must be some sort way to send the command over. MQTT?
        else:
            pass

def setup_reader_and_camera(device=0, height=480, width=640):
    "Setups up EasyOCR screen reader for the webcam."
    reader = easyocr.Reader(['en'])

    # Initialize webcam
    cap = cv2.VideoCapture(device) 
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"FPS: {fps}")  #TODO: Logging
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return reader, cap


def read_commands(ocr_model, capture_device,
                  frame_check_multiplier=2, yaml_file="text_to_action.yaml"
                  ):

    # Read in command dictionary
    with open(yaml_file, 'r') as file:
        action_dict = yaml.safe_load(file)
    
    # Loop to continuously read the camera input
    fps = capture_device.get(cv2.CAP_PROP_FPS)
    i = 0
    while True:
        # Capture each frame from the camera
        ret, frame = capture_device.read()
        if not ret:
            print("Failed to grab frame")
            break
        
        i += 1
        # How many frames until a text check is done. Based on the frame multiplier.
        if i == fps*frame_check_multiplier: 
            print("index reached")  #TODO: add into logging
            i = 0
            # Convert frame to grayscale (optional but improves OCR performance)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Perform text detection
            key_command = get_interaction_text(ocr_model, gray)

        # Display the frame with detected text
        cv2.imshow('Camera Feed - Press q to exit', frame)

        # Press 'q' to break the loop and exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            # Release the camera and close all OpenCV windows
            capture_device.release()
            cv2.destroyAllWindows()
            break

    




if __name__ == "__main__":
    ocr_model, cap_device = setup_reader_and_camera(device=0, height=480, width=640)
    read_commands(ocr_model=ocr_model, capture_device=cap_device)


