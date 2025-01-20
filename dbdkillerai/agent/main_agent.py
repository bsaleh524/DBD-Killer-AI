from typing import Protocol
from time import sleep
from ultralytics import YOLO
import torch
import cv2
import pyautogui
import time
import queue
import threading
from PIL import Image as pil
from pkg_resources import parse_version
if parse_version(pil.__version__)>=parse_version('10.0.0'):
    pil.ANTIALIAS=pil.LANCZOS

from dbdkillerai.agent.eyes.ocr.bottom_text_reader import (
    setup_reader_and_camera, get_state_commands,
    get_interaction_text, 
    )
from dbdkillerai.agent.arms.right_arm import right_arm_worker
from dbdkillerai.agent.legs.legs import vertical_legs_worker, horizontal_legs_worker
from dbdkillerai.agent.eyes.ocr.crop_images import crop_bottom_center, crop_top_right

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
    def __init__(self, yolo_model_path, test_image=False) -> None:
        # Setup initialization of models.
        self.obj_det = YOLO(yolo_model_path)
        self.test_image = test_image
        self.ocr_model, self.cap_device = \
            setup_reader_and_camera(test_image=self.test_image,
                                    device=0,
                                    height=720, #640  #TODO; make reduced and big sizes
                                    width=1280, #480
            )
        
        # Setup our queues for limbs
        self.right_arm_queue = queue.Queue()
        # self.left_arm_queue = queue.Queue()
        self.vertical_legs_queue = queue.Queue()
        self.horizontal_legs_queue = queue.Queue()

        # Setup threads of limbs
        self.right_arm_thread = threading.Thread(target=right_arm_worker,
                                                 args=(self.right_arm_queue,),
                                                 daemon=True)
        self.vertical_legs_thread = threading.Thread(target=vertical_legs_worker,
                                                 args=(self.vertical_legs_queue,),
                                                 daemon=True)
        self.horizontal_legs_thread = threading.Thread(target=horizontal_legs_worker,
                                                 args=(self.horizontal_legs_queue,),
                                                 daemon=True)

        # Start all threads
        self.right_arm_thread.start()
        self.vertical_legs_thread.start()
        self.horizontal_legs_thread.start()

        #TODO: To kick off the limbs(for the future brain), do
        ##arms:
            # self.arms_queue.put(command)  # `command` is anything
        # Legs:
        # if vertical_command:
        #     self.vertical_legs_queue.put(vertical_command) # "w" or "s"
        # if horizontal_command:
        #     self.horizontal_legs_queue.put(horizontal_command) # "a" or "d"

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

    def stop_all_threads(self):
        """Gracefully stop all threads."""
        self.arms_queue.put("STOP")
        self.vertical_legs_queue.put("STOP")
        self.horizontal_legs_queue.put("STOP")
        self.arms_thread.join()
        self.vertical_legs_thread.join()
        self.horizontal_legs_thread.join()

# implement this into camera
    def read_screen_input(self):
        last_key_command = None
        last_bbox = None

        fps = self.cap_device.get(cv2.CAP_PROP_FPS)
        frame_count = 0

        while True:
            # Capture the next frame
            ret, frame = self.cap_device.read()
            if not ret:
                print("Failed to grab frame.")
                break

            frame_count += 1

            # OCR processing at specific frame intervals
            if frame_count >= fps * self.frame_check_multiplier:
                frame_count = 0
                print("Performing OCR...")

                # Convert to grayscale for OCR
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Crop and perform OCR
                cropped_image_bottom = crop_bottom_center(gray_frame)
                cropped_image_topright = crop_top_right(gray_frame)

                key_command_bottom, bbox = get_interaction_text(
                    self.ocr_model, cropped_image_bottom, self.action_dict)
                reward_topright, _ = get_interaction_text(
                    self.ocr_model, cropped_image_topright, self.action_dict)

                #TODO: Send reward text to brain
                #TODO: send detected action text on bottom to brain

                # send command to "neck" module call. "neck" must be imported
                # the get interaction text should be strictly an "arms" piece, 
                # not an "eyes" piece. 

                if key_command_bottom:
                    last_key_command = key_command_bottom
                    last_bbox = bbox

                    # Simulate the keyboard command
                    print(f"Detected Command: {key_command_bottom}")
                    # pyautogui.keyDown(key_command_bottom)
                    time.sleep(2)
                    # pyautogui.keyUp(key_command_bottom)

            # YOLO detection
            yolo_results = self.obj_det.predict(source=frame, conf=0.2, show=False)

            # Send detections to Brain


            # Draw YOLO predictions on the frame
            for result in yolo_results[0].boxes:
                x1, y1, x2, y2 = map(int, result.xyxy[0])
                cls = int(result.cls)
                conf = float(result.conf)
                label = f"{self.obj_det.names[cls]} {conf:.2f}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Highlight OCR results if available
            if last_key_command and last_bbox:
                top_left = tuple(map(int, last_bbox[0]))
                bottom_right = tuple(map(int, last_bbox[2]))
                cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
                cv2.putText(frame, last_key_command, top_left, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            # Display the updated frame
            cv2.imshow('Camera Feed - Press q to exit', frame)

            # Exit loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release resources
        self.cap_device.release()
        cv2.destroyAllWindows()

def main() -> None:
    test_image = False
    killer = Agent(yolo_model_path="dbdkillerai/models/dataset/9/best.pt", test_image=test_image)
    killer.read_screen_input()
    
if __name__ == "__main__":
    main()
    #TODO: Then, ensure both OCR and YOLO are used here in the loop. Once both are done, THEN,
    # we can potentially follow states based upon what the model sees. 
    # THENN, Follow issue.