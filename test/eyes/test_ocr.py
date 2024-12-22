###TBD read the text from a picture###
import torch
import cv2
from PIL import Image as pil
from pkg_resources import parse_version
from dbdkillerai.agent.eyes.ocr import crop_images, bottom_text_reader
from dbdkillerai.agent.main_agent import Agent


if parse_version(pil.__version__)>=parse_version('10.0.0'):
    pil.ANTIALIAS=pil.LANCZOS
if torch.cuda.is_available():
    Device = torch.device("cuda")
elif torch.backends.mps.is_available():
    Device = torch.device("mps")
else:
    Device = torch.device("cpu")
print(Device)

def read_stream_input(killer_ai: Agent):
        # Determine if we want to test on an image first
        last_key_command = None
        last_bbox = None
        # Convert frame to grayscale (optional but improves OCR performance)
        gray = cv2.cvtColor(killer_ai.cap_device, cv2.COLOR_BGR2GRAY)
        
        # Requires cropped bottom section
        cropped_image_bottom = crop_images.crop_bottom_center(gray)
        cropped_image_topright = crop_images.crop_top_right(gray)

        # Perform text detection
        key_command_bottom, bbox = bottom_text_reader.get_interaction_text(killer_ai.ocr_model, cropped_image_bottom, killer_ai.action_dict)
        reward_topright, _ = bottom_text_reader.get_interaction_text(killer_ai.ocr_model, cropped_image_topright, killer_ai.action_dict)
        
        # Check if a key was pressed
        if key_command_bottom:
            last_key_command = key_command_bottom
            last_bbox = bbox
            # Log detected text to a file
            # log_to_file(text)

            print(f"Final Command: {key_command_bottom}")
            # Do the command
            print('\nKey Down')
            print('\nKey Up')

        # YOLO inference on the current frame
        yolo_results = killer_ai.obj_det.predict(
            source=killer_ai.cap_device, conf=0.2, show=False)

        # Overlay YOLO predictions on the frame
        for result in yolo_results[0].boxes:
            # Extract coordinates, class, and confidence
            x1, y1, x2, y2 = map(int, result.xyxy[0])
            cls = int(result.cls)
            conf = float(result.conf)
            label = f"{killer_ai.obj_det.names[cls]} {conf:.2f}"

            # Draw bounding box and label on the frame
            cv2.rectangle(killer_ai.cap_device, (x1, y1), (x2, y2), (255, 255, 255), 2)
            cv2.putText(killer_ai.cap_device, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Overlay the last detected information on the frame
        if last_key_command and last_bbox:
            top_left = tuple(map(int, last_bbox[0]))
            bottom_right = tuple(map(int, last_bbox[2]))
            cv2.rectangle(cropped_image_bottom, top_left, bottom_right, (0, 255, 0), 2)

            # Put the detected text on the frame
            cv2.putText(cropped_image_bottom, last_key_command, top_left,
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

            # Display the frame (with or without overlays) in a single window
            cv2.imshow("Original Image", killer_ai.cap_device)
            cv2.imshow("Cropped Bottom Image", cropped_image_bottom)
            cv2.imshow("Cropped TopRight Image", cropped_image_topright)
        else:
            print(f"No key command found. Unrecognized text")
            cv2.imshow("Original Image", killer_ai.cap_device)
            cv2.imshow("Cropped Bottom Image", cropped_image_bottom)
            cv2.imshow("Cropped TopRight Image", cropped_image_topright)
        
        cv2.waitKey(0)  # Wait indefinitely for a key press
        cv2.destroyAllWindows()

def test_screen_input_with_image():
    ## Test the inputs to the screen, focusing on the cropping
    # and text returns.
    Killer = Agent("models/yolov8n.pt", test_image=True)
    read_stream_input(Killer)

test_screen_input_with_image()