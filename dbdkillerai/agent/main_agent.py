from typing import Protocol
from ultralytics import YOLO
import torch
from eyes.ocr.bottom_text_reader import (
    setup_reader_and_camera, get_state_commands, read_commands
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
    def switch(self, agent): ...

    def review(self): ...

    def finalize(self): ...
##

class SurveyState:
    '''Survey generators for Survivors.
    
    Check all generators within the map for survivors that
    are repairing them. If they are, chase the survivor that 
    is found. If no survivors found when next to a generator,
    then damage it if possible'''
    def switch(self, agent):
        # if model.detects survivor:
        agent.switch = ChaseState()
    
    def survey(self, agent):
        pass

class ChaseState: 
    '''Survivor is found. Down Survivor, then pick them up.
    
    The Chase state will have activated after a survivor from
    the Survey state, causing a switch here. The Chase state 
    shall follow the identified survivor and attempt to land
    multiple hits. Once a Downed survivor has been '''
    def switch(self, agent):
        # if pickup survivor.
        print("Switching to HOOK state...")
        agent.switch = HookState()

class HookState:
    '''Downed survivor is picked up. Hang at nearest hook.
    
    The Hook state will assume is survivor is currently
    being held. After picked them up, the agent will look
    for a hook to complete a hook action on, then switch states.
    YOLO: (hook). TODO: expand to other labels'''
    def switch_to_survey(self, agent):
        # if hook=True(no hook icon)
        print("Switching to SURVEY state...")
        agent.switch = SurveyState()
        
class Agent:
    '''Killer AI Agent.
    
    This is the agent itself. YOLO model and the OCR model
    should be initialized here and then '''
    def __init__(self,
                 yolo_model_path,
                 ) -> None:
        # Setup initialization of models.
        self.obj_det = YOLO(yolo_model_path)
        self.ocr_model, self.cap_device = \
            setup_reader_and_camera(device=0, height=480, width=640)
        
        # Setup SURVEY values since SURVEY is first state.
        self.state = SurveyState()
        self.state_name = "SURVEY"
        self.action_dict = get_state_commands(
            state=self.state_name,
            path_to_yaml="dbdkillerai/agent/eyes/ocr/text_to_action.yaml")

    def switch(self):
        #TODO. it switches itself only one way, which we dont want.
        # This came from the bulb example, so we should rework it to
        # switch between all states. Could instead be
        # self.state.switch_to_survey()
        # self.state.switch_to_chase()
        # self.state.switch_to_hook()
        self.state.switch(self)

    def read_text(self):
        read_commands(
            ocr_model=self.ocr_model,
            capture_device=self.cap_device,
            action_dict=self.action_dict
        )

def main() -> None:
    
    killer = Agent(yolo_model_path="DBD-Killer-AI/notebooks/models/yolov8n.pt")

if __name__ == "__main__":
    main()