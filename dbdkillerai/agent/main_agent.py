from typing import Protocol
from time import sleep
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


    def switch_to_survey(self):
        self.state.switch_to_survey(self)

    def switch_to_chase(self):
        self.state.switch_to_chase(self)

    def switch_to_hook(self):
        self.state.switch_to_hook(self)

    def test_all_states(self):
        # survey
        self.switch_to_survey()
        self.state.activate()
        self.switch_to_chase()
        self.state.activate()

        # chase
        self.switch_to_survey()
        self.state.activate()

        # Survey
        self.switch_to_chase()
        self.state.activate()

        #chase
        self.switch_to_hook()
        self.state.activate()

        #hook
        self.switch_to_survey()
        self.state.activate()

def main() -> None:
    killer = Agent(yolo_model_path="notebooks/models/yolov8n.pt")
    killer.test_all_states()

if __name__ == "__main__":
    main()