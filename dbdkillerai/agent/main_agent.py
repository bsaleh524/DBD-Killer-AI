from typing import Protocol
from time import sleep
from ultralytics import YOLO
import torch
import cv2
import pyautogui
import time
from PIL import Image as pil
from pkg_resources import parse_version
if parse_version(pil.__version__)>=parse_version('10.0.0'):
    pil.ANTIALIAS=pil.LANCZOS
from eyes.ocr.bottom_text_reader import (
    setup_reader_and_camera, get_state_commands,
    get_interaction_text, 
    )
if torch.cuda.is_available():
    Device = torch.device("cuda")
elif torch.backends.mps.is_available():
    Device = torch.device("mps")
else:
    Device = torch.device("cpu")
print(Device)

# Switch interface first.

class KillerState(Protocol):
    def switch_to_survey(self, agent): ...

    def switch_to_chase(self, agent): ...

    def switch_to_hook(self, agent): ...

    def activate(self): ... #do we need 'agent' here?

##

class SurveyState:
    '''Survey generators for Survivors.
    
    Check all generators within the map for survivors that
    are repairing them. If they are, chase the survivor that 
    is found. If no survivors found when next to a generator,
    then damage it if possible'''

    def switch_to_survey(self, agent):
        print("Switch attempt to SURVEY failed. Already SURVEY")

    def switch_to_chase(self, agent):
        # if model.detects survivor:
        print("Switching to CHASE State...")
        agent.state_name = "CHASE"
        agent.action_dict = get_state_commands(
            state=agent.state_name,
            path_to_yaml="dbdkillerai/agent/eyes/ocr/text_to_action.yaml"
        )
        agent.state = ChaseState()
    
    def switch_to_hook(self, agent):
        # if detect downed_survivor AND picked them up.
        print("Switching to HOOK state...")
        agent.state_name = "HOOK"
        agent.action_dict = get_state_commands(
            state=agent.state_name,
            path_to_yaml="dbdkillerai/agent/eyes/ocr/text_to_action.yaml"
        )
        agent.state = HookState()
    
    def activate(self):
        # Go to each generator, start from center and go right
        # if more generators are on right side. Else, go left.
        # Survey_direction = Left OR survey_direction = Right
        print("Entered SURVEY State. Checking Generators.")
        sleep(1)
        pass

class ChaseState: 
    '''Survivor is found. Down Survivor, then pick them up.
    
    The Chase state will have activated after a survivor from
    the Survey state, causing a switch here. The Chase state
    shall follow the identified survivor and attempt to land
    multiple hits. Once a Downed survivor has been '''
    def switch_to_survey(self, agent):
        # if hook_icon=False(no hook icon)
        print("Switching to SURVEY state...")
        agent.state_name = "SURVEY"
        agent.action_dict = get_state_commands(
            state=agent.state_name,
            path_to_yaml="dbdkillerai/agent/eyes/ocr/text_to_action.yaml"
        )
        agent.state = SurveyState()
    
    def switch_to_chase(self, agent):
        # if model.detects survivor:
        print("Switch attempt to CHASE failed. Already CHASE")

    def switch_to_hook(self, agent):
        # if pickup survivor.
        print("Switching to HOOK state...")
        agent.state_name = "HOOK"
        agent.action_dict = get_state_commands(
            state=agent.state_name,
            path_to_yaml="dbdkillerai/agent/eyes/ocr/text_to_action.yaml"
        )
        agent.state = HookState()
    
    def activate(self):
        print("Entered CHASE State. Attacking Survivor.")
        sleep(1)
        pass

class HookState:
    '''Downed survivor is picked up. Hang at nearest hook.
    
    The Hook state will assume is survivor is currently
    being held. After picked them up, the agent will look
    for a hook to complete a hook action on, then switch states.
    YOLO: (hook). TODO: expand to other labels'''

    def switch_to_survey(self, agent):
        # if hook_icon=False(no hook icon)
        print("Hooked/Dropped Survivor. Switching to SURVEY state...")
        agent.state_name = "SURVEY"
        agent.action_dict = get_state_commands(
            state=agent.state_name,
            path_to_yaml="dbdkillerai/agent/eyes/ocr/text_to_action.yaml"
        )
        agent.state = SurveyState()
    
    def switch_to_chase(self, agent):
        print("Can't switch to CHASE. Currently holding survivor!")
    
    def switch_to_hook(self, agent):
        print("Can't switch to HOOK. Currently holding survivor!")
    
    def activate(self):
        print("Entered HOOK State. Locating Hook for Survivor.")
        sleep(1)
        pass

class Agent:
    '''Killer AI Agent.
    
    This is the agent itself. YOLO model and the OCR model
    should be initialized here and then '''
    def __init__(self, yolo_model_path) -> None:
        # Setup initialization of models.
        self.obj_det = YOLO(yolo_model_path)
        self.ocr_model, self.cap_device = \
            setup_reader_and_camera(device=0, height=480, width=640)
        
        # Setup SURVEY values since SURVEY is first state.
        self.state_name = "SURVEY"
        self.action_dict = get_state_commands(
            state=self.state_name,
            path_to_yaml="dbdkillerai/agent/eyes/ocr/text_to_action.yaml"
        )
        self.state = SurveyState()
        self.frame_check_multiplier = 2


    def switch_to_survey(self):
        self.state.switch_to_survey(self)

    def switch_to_chase(self):
        self.state.switch_to_chase(self)

    def switch_to_hook(self):
        self.state.switch_to_hook(self)

    # def test_all_states(self):
    #     # survey
    #     self.switch_to_survey()
    #     self.state.activate()
    #     self.switch_to_chase()
    #     self.state.activate()

    #     # chase
    #     self.switch_to_survey()
    #     self.state.activate()

    #     # Survey
    #     self.switch_to_chase()
    #     self.state.activate()

    #     #chase
    #     self.switch_to_hook()
    #     self.state.activate()

    #     #hook
    #     self.switch_to_survey()
    #     self.state.activate()
        # return None

# implement this into camera
    def read_screen_input(self):
        
        last_key_command = None
        last_bbox = None

        # Loop to continuously read the camera input
        fps = self.cap_device.get(cv2.CAP_PROP_FPS)
        i = 0

        while True:
            # Capture each frame from the camera
            ret, frame = self.cap_device.read()
            if not ret:
                print("Failed to grab frame.")
                break
            
            i += 1
            # How many frames until a text check is done. Based on the frame multiplier.
            if i == fps*self.frame_check_multiplier: 
                print("OCR processing interval reached.")  #TODO: add into logging
                i = 0
                # Convert frame to grayscale (optional but improves OCR performance)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Perform text detection
                key_command, bbox = get_interaction_text(self.ocr_model, gray, self.action_dict)

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

            # YOLO inference on the current frame
            yolo_results = self.obj_det.predict(
                source=frame, conf=0.2, show=False)

            # Overlay YOLO predictions on the frame
            for result in yolo_results[0].boxes:
                # Extract coordinates, class, and confidence
                x1, y1, x2, y2 = map(int, result.xyxy[0])
                cls = int(result.cls)
                conf = float(result.conf)
                label = f"{self.obj_det.names[cls]} {conf:.2f}"

                # Draw bounding box and label on the frame
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

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
                self.cap_device.release()
                cv2.destroyAllWindows()
                break

def main() -> None:
    killer = Agent(yolo_model_path="models/yolov8n.pt")
    killer.read_screen_input()
    
if __name__ == "__main__":
    main()
    #TODO: Follow issue.