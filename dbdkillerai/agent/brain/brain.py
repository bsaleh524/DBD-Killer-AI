"""This brain file is the main decision making model."""
from threading import Thread
from queue import Queue

def reward_function():
    pass

def decision_making():
    pass

def send_to_right_arm():
    """Send the decision to the right arm."""
    pass

class BrainWorker:
    """
    Class that functions as a thread to send brain
    commands to the MotorWoker based upon
    the decision it ends up making. Also allows
    graceful stopping."""

    def __init__(self,):
        self.stopped = False

    def start(self,
              brain_queue: Queue,
              motor_queue: Queue,):
        "Start the thread"
        self.thread = Thread(target=self.get,
                             args=(brain_queue, motor_queue,)
                             ).start()

    def get(self, brain_queue, motor_queue):
        "Do actions from queue, given by brain."
        while not self.stopped:
            current_command = brain_queue.get()
            if current_command:
                print("BRAIN || Brain processing goes here.")
                motor_queue.put("SWING")
                print("BRAIN || Brain says to SWING.")
        print("Brain Worker stopped.")

    def stop(self):
        self.stopped = True
        # if self.thread is not None:
        #     self.thread.join()  # Ensure thread joins before exiting