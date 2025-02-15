from threading import Thread
from queue import Queue
import pyautogui

class MotorWorker:
    """
    Class that functions as a thread to send brain
    commands to the different limb queues based upon
    the decision it ends up making. Also allows
    graceful stopping."""

    def __init__(self,):
        self.stopped = False

    def start(self,
              brain_queue: Queue,
              right_arm_queue: Queue,):
        "Start the thread"
        self.thread = Thread(target=self.get, args=(brain_queue, right_arm_queue,)).start()

    def get(self, brain_queue, right_arm_queue):
        "Do actions from queue, given by brain."
        while not self.stopped:
            current_command = brain_queue.get()
            if current_command:
                if current_command[0] == "RIGHT_ARM":
                    right_arm_queue.put("SWING")
        print("Motor Worker stopped.")

    def stop(self):
        self.stopped = True
        # if self.thread is not None:
        #     self.thread.join()  # Ensure thread joins before exiting


# Task 1: Motor (Continuously processes commands)
def motor_worker(arms_queue):
    """Swings the primary attack (Mouse 1). Use any command that comes in."""
    while True:
        command = arms_queue.get()  # Blocks until a command is available
        if command == "STOP":  # Graceful exit condition
            print("ARMS stopping...")
            break
        print(f"ARMS|RIGHT(M!): Executing")
        pyautogui.leftClick(duration=0.8)
        arms_queue.task_done()