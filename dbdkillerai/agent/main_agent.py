from typing import Protocol
from time import sleep
from ultralytics import YOLO
import torch
import cv2
import queue
import threading
from PIL import Image as pil
from pkg_resources import parse_version
if parse_version(pil.__version__)>=parse_version('10.0.0'):
    pil.ANTIALIAS=pil.LANCZOS

from dbdkillerai.agent.eyes.ocr.text_reader import (
    setup_camera, setup_reader, get_state_commands,
    )
from dbdkillerai.agent.arms.right_arm import right_arm_worker, RightArmWorker
from dbdkillerai.agent.legs.legs import vertical_legs_worker, horizontal_legs_worker, VerticalLegsWorker, HorizontalLegsWorker
from dbdkillerai.agent.eyes.ocr.text_reader import ocr_pipeline, OCRPipelineWorker
from dbdkillerai.agent.eyes.device_reader.videogetter import VideoGetter
import faulthandler
faulthandler.enable()

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
    def __init__(self,
                 yolo_model_path,
                 test_image=False,
                 device_index=0,
                 quality_preset=0,
                 frame_check_multiplier=2) -> None:
        
        # Setup initialization of models.
        self.obj_det = YOLO(yolo_model_path)
        self.test_image = test_image
        self.device_index = device_index
        self.quality_preset = quality_preset
        self.frame_check_multiplier = frame_check_multiplier


        # Setup SURVEY values since SURVEY is first state.
        self.state_name = "SURVEY"
        self.action_dict = get_state_commands(
            state=self.state_name,
            path_to_yaml="dbdkillerai/agent/eyes/ocr/text_to_action.yaml"
        )
        self.state = SurveyState()

        # Setup our queues and threads for limbs
        self.right_arm_queue = queue.Queue()
        self.right_arm_thread = RightArmWorker()
        
        self.vertical_legs_queue = queue.Queue()
        self.vertical_legs_thread = VerticalLegsWorker()
    
        self.horizontal_legs_queue = queue.Queue()
        self.horizontal_legs_thread = HorizontalLegsWorker()
        
        self.ocr_queue = queue.Queue()
        self.ocr_multiproc_thread = OCRPipelineWorker(
            self.ocr_queue,
            self.action_dict,
            self.right_arm_queue)

    def switch_to_survey(self):
        self.state.switch_to_survey(self)

    def switch_to_chase(self):
        self.state.switch_to_chase(self)

    def switch_to_hook(self):
        self.state.switch_to_hook(self)

    def stop_all_threads(self):
        """Gracefully stop all threads."""
        print("Stopping all threads...")
        self.right_arm_thread.stop()
        self.vertical_legs_thread.stop()
        self.horizontal_legs_thread.stop()
        self.ocr_multiproc_thread.stop()
        print("Stopped all threads!")
        

    # implement this into camera
    def run_agent(self):
        frame_count = 0

        # Setup thread for reading input and only start it when
        # the agent itself starts operating
        video_getter = VideoGetter(device=self.device_index,
                                test_image=self.test_image,
                                vid_preset=self.quality_preset
        )
        self.fps = video_getter.get_fps()

        # Start all threads
        print("Starting all threads and processes...")
        self.right_arm_thread.start(self.right_arm_queue)  # Start Right Arm/Main Attack/M1
        self.vertical_legs_thread.start(self.vertical_legs_queue)  # Start Vertical Legs/ "w" and "s"
        self.horizontal_legs_thread.start(self.horizontal_legs_queue)  # Start Horizontal Legs/ "a" and "d"
        # self.read_input_thread.start()  # Start Screen Capture for YOLO and OCR Queueing
        video_getter.start()

        # Start off multiprocessing
        self.ocr_multiproc_thread.start()  # Start OCR Processing for text detection
        
        sleep(3)
        print("Agent is Ready!")

        ## Possible race condition. queues empty before while loop

        while True:
            # Capture the next frame n the screen queue
            # print(f"tryin to get frame from screen_queue of size {self.screen_queue.qsize()}")
            frame = video_getter.queue.get() 
            frame_count += 1
            # print(f"frame_count: {frame_count}")
            # OCR processing at specific frame intervals
            if frame_count >= self.fps * self.frame_check_multiplier:
                frame_count = 0
                self.ocr_queue.put(frame)
                print(f"frame added to ocr queue. new size: {self.ocr_queue.qsize()}")

            # YOLO detection
            yolo_results = self.obj_det.predict(source=frame,
                                                conf=0.2,
                                                show=False,
                                                verbose=False)
            #TODO: Send detections to Brain

            # Draw YOLO predictions on the frame
            for result in yolo_results[0].boxes:
                x1, y1, x2, y2 = map(int, result.xyxy[0])
                cls = int(result.cls)
                conf = float(result.conf)
                label = f"{self.obj_det.names[cls]} {conf:.2f}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            # Display the updated frame
            cv2.imshow('Camera Feed - Press q to exit', frame)

            # Exit loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                video_getter.stop()
                self.stop_all_threads()
                # self.read_input_thread.join()
                break

        # Release resources
        cv2.destroyAllWindows()

def main() -> None:
    test_image = False
    killer = Agent(yolo_model_path="dbdkillerai/models/dataset/9/best.pt",
                   test_image=test_image,
                   device_index=0,
                   quality_preset=1)
    killer.run_agent()
    
if __name__ == "__main__":
    main()
    #TODO: Then, ensure both OCR and YOLO are used here in the loop. Once both are done, THEN,
    # we can potentially follow states based upon what the model sees. 
    # THENN, Follow issue.