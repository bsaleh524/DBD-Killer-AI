import threading
from threading import Thread
from queue import Queue
import time
import pyautogui


class RightArmWorker:
    """
    Class that functions as a thread to pull in
    commands from the right arm queue and execute
    them. Also allows graceful stopping."""

    def __init__(self,):
        self.stopped = False

    def start(self, queue: Queue):
        "Start the thread"
        self.thread = Thread(target=self.get, args=(queue,)).start()

    def get(self, queue, click_duration: float = 0.8):
        "Do actions from queue, given by brain."
        while not self.stopped:
            current_command = queue.get()
            if current_command:
                print("R-ARM || Motor commanded me to do: ", current_command)
                pyautogui.leftClick(duration=click_duration)
        print("Right Arm Worker stopped.")

    def stop(self):
        self.stopped = True
        # if self.thread is not None:
        #     self.thread.join()  # Ensure thread joins before exiting


# Task 1: Arms (Continuously processes commands)
def right_arm_worker(arms_queue):
    """Swings the primary attack (Mouse 1). Use any command that comes in."""
    while True:
        command = arms_queue.get()  # Blocks until a command is available
        if command == "STOP":  # Graceful exit condition
            print("ARMS stopping...")
            break
        print(f"ARMS|RIGHT(M!): Executing")
        pyautogui.leftClick(duration=0.8)
        arms_queue.task_done()

#TODO: Make test for these

if __name__ == "__main__":
    # Test out the arm swing
    # Create queues for Arms and Legs commands
    arms_queue = queue.Queue()

    # Create threads for Arms and Legs
    arms_thread = threading.Thread(target=right_arm_worker,
                                args=(arms_queue, ),
                                daemon=True
    )

    # Start the threads
    arms_thread.start()

    # Simulate sending commands to Arms and Legs
    time.sleep(5)  # Delay to simulate runtime
    arms_queue.put("Swing")
    time.sleep(5)
    arms_queue.put("Raise Shield")

    # Gracefully stop the threads
    arms_queue.put("STOP")

    # Wait for threads to finish
    arms_thread.join()

    print("All threads have finished.")
