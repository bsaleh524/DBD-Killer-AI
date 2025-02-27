import multiprocessing
import multiprocessing.queues
from queue import Queue
import time
import pyautogui


class RightArmWorker_MP(multiprocessing.Process):
    """
    Class that functions as a thread to pull in
    commands from the right arm queue and execute
    them. Also allows graceful stopping."""

    def __init__(self, queue: multiprocessing.Queue):
        super().__init__()
        self.queue = queue
        self.stopped = multiprocessing.Event()

    def run(self, click_duration: float = 0.8):
        """Process method that continuously checks for new commands and executes them."""
        while not self.stopped.is_set():
            try:
                current_command = self.queue.get(timeout=1)  # Prevent blocking indefinitely
                if current_command:
                    print("R-ARM || Motor commanded me to do: ", current_command)
                    pyautogui.leftClick(duration=click_duration)
            except multiprocessing.queues.Empty:
                print("Right Arm Worker is waiting for a command...")
                pass
            except Exception as e:
                print("Right Arm Worker encountered an error: ", e)
                pass

    def stop(self):
        self.stopped.set()


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
