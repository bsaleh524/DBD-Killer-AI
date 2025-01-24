"""Reads Action text and responds with key upon detected text during desired states."""

import easyocr
import cv2
import yaml
import pyautogui
import time
from pathlib import Path
from PIL import Image as pil

from dbdkillerai.agent.eyes.ocr.crop_images import crop_bottom_center, crop_top_right
from dbdkillerai.agent.eyes.ocr.ocr_preproc import get_grayscale_image

# Update the PIL library to use the LANCZOS filter for better image resizing
from pkg_resources import parse_version
if parse_version(pil.__version__)>=parse_version('10.0.0'):
    pil.ANTIALIAS=pil.LANCZOS

def ocr_pipeline(
    ocr_queue,
    action_dict,
    ocr_model,
    right_arm_queue,
    debug=False):
    
    while True:
        """Multiprocessing function to read the screen capture and detect text."""
        #TODO: refer to todo.md for the next steps.

        # Convert to grayscale for better imaging
        frame = ocr_queue.get() # Get the frame from the queue.
        if frame == "STOP":  # Graceful exit condition
            print("ocr_pipeline stopping...")
            break
        gray = get_grayscale_image(frame)

        # Crop the images
        cropped_image_bottom = crop_bottom_center(gray)
        cropped_image_topright = crop_top_right(gray)

        # Use OCR to read the bottom command and reward text.
        command_text_bottom, bbox_bottom_text = get_interaction_text(
            ocr_model, cropped_image_bottom, action_dict)
        reward_text_topright, _ = get_interaction_text(
            ocr_model, cropped_image_topright, action_dict)


        # Place the detected commands into the right arm queue
        if command_text_bottom and debug:
            right_arm_queue.put(command_text_bottom)
            print(f"EYES|OCR\tCommand Detected: {command_text_bottom}")
        
        #TODO; instead of returning arms queue, add detected commands
        # to the brain queue ONLY to have the brain decide what to do.

        # return key_command_bottom, bbox_bottom_text, reward_text_topright

#TODO; we want to send the preproc to get_interaction text. 
# 

def get_interaction_text(reader: easyocr.Reader, image, command_dict):
    """Read the text from the given screencapture frame/image and return key."""
    result = reader.readtext(image)
    if result:
    # Detect text
        for (bbox, text, prob) in result:
            # print(f"Detected Text: {text} (Confidence: {prob:.2f})")

            if text.lower() in command_dict.keys():
                print(f"{text.lower()} Detected!")  # Detected text matches command
                return command_dict[text.lower()], bbox #TODO: Must be some sort way to send the command over. MQTT?
            else:
                continue
    return None, None

def setup_reader_and_camera(test_image=False, device=0, height=480, width=640):
    "Setups up EasyOCR model reader with screen capture of the webcam."
    reader = easyocr.Reader(['en'])

    # If testing, use an image
    if not test_image:
        # Initialize webcam
        cap = cv2.VideoCapture(device) 
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(f"FPS: {fps}")  #TODO: Logging
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    else:
        # Get the current script's directory
        script_dir = Path(__file__).resolve().parent

        # Navigate to the desired file relative to the script's directory
        file_path = script_dir.parents[3] / 'test' / 'eyes' / 'ocr_test.png'  # Adjust based on your repo structure

        cap = cv2.imread(file_path)
    return reader, cap

def get_state_commands(state: str = "SURVEY", path_to_yaml: str = "text_to_action.yaml"):
    # Read in command dictionary for the given state
    with open(path_to_yaml, 'r') as file:
        action_dict = yaml.safe_load(file)
    return action_dict['states'][state]['action_commands']

def read_commands(ocr_model, capture_device, action_dict,
                  frame_check_multiplier=2):
    
    last_key_command = None
    last_bbox = None

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
            key_command, bbox = get_interaction_text(ocr_model, gray, action_dict)

            # DEBUG: Display results on the frame (Optional: for debugging/visualization)
            # for (bbox, text, prob) in results:
            # Draw bounding box around detected text
            if key_command:
                last_key_command = key_command
                last_bbox = bbox
                # Log detected text to a file
                # log_to_file(text)

                print(f"Final Command: {key_command}")
                # Do the command
                print('\nKey Down')
                pyautogui.keyDown(key_command)
                time.sleep(2)
                pyautogui.keyUp(key_command)
                print('\nKey Up')

        # Overlay the last detected information on the frame
        if last_key_command and last_bbox:
            top_left = tuple(map(int, last_bbox[0]))
            bottom_right = tuple(map(int, last_bbox[2]))
            cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

            # Put the detected text on the frame
            cv2.putText(frame, last_key_command, top_left,
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        # Display the frame (with or without overlays) in a single window
        cv2.imshow('Camera Feed - Press q to exit', frame)

        # Press 'q' to break the loop and exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            # Release the camera and close all OpenCV windows
            capture_device.release()
            cv2.destroyAllWindows()
            break

# To test, place the bottom code where you desire for a live feed.
if __name__ == "__main__":
    ocr_model, cap_device = setup_reader_and_camera(device=0, height=480, width=640)
    action_dict = get_state_commands(state="SURVEY",
                                     path_to_yaml="dbdkillerai/agent/eyes/ocr/text_to_action.yaml")
    read_commands(ocr_model=ocr_model, capture_device=cap_device, action_dict=action_dict)


