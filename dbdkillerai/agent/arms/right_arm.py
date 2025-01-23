import threading
import queue
import time
import pyautogui

# Task 1: Arms (Continuously processes commands)
def right_arm_worker(arms_queue):
    """Swings the primary attack (Mouse 1)"""
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
