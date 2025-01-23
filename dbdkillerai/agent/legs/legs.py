import threading
import queue
import pyautogui
import time


def vertical_legs_worker(vertical_legs_queue):
    """Processes vertical movement commands (W and S keys)."""
    current_key = None
    while True:
        command = vertical_legs_queue.get()  # Blocks until a command is available
        if command == "STOP":  # Graceful exit condition
            print("Vertical LEGS stopping...")
            if current_key:
                pyautogui.keyUp(current_key)  # Release the current key
            break
        if command in ["w", "s"]:  # Valid movement commands
            if current_key and current_key != command:  # Switch keys
                pyautogui.keyUp(current_key)  # Release previous key
            current_key = command
            pyautogui.keyDown(command)  # Hold the new key
            print(f"Vertical Legs: Holding {command.upper()}")
        else:
            print(f"Vertical Legs: Unknown command '{command}' received.")
        vertical_legs_queue.task_done()  # Signal the task is done


def horizontal_legs_worker(horizontal_legs_queue):
    """Processes horizontal movement commands (A and D keys)."""
    current_key = None
    while True:
        command = horizontal_legs_queue.get()  # Blocks until a command is available
        if command == "STOP":  # Graceful exit condition
            print("Horizontal LEGS stopping...")
            if current_key:
                pyautogui.keyUp(current_key)  # Release the current key
            break
        if command in ["a", "d"]:  # Valid movement commands
            if current_key and current_key != command:  # Switch keys
                pyautogui.keyUp(current_key)  # Release previous key
            current_key = command
            pyautogui.keyDown(command)  # Hold the new key
            print(f"Horizontal Legs: Holding {command.upper()}")
        else:
            print(f"Horizontal Legs: Unknown command '{command}' received.")
        horizontal_legs_queue.task_done()  # Signal the task is done

# Legs:
        # if vertical_command:
        #     self.vertical_legs_queue.put(vertical_command) # "w" or "s"
        # if horizontal_command:
        #     self.horizontal_legs_queue.put(horizontal_command) # "a" or "d"

if __name__ == "__main__":
    # Queues for vertical and horizontal movement
    vertical_legs_queue = queue.Queue()
    horizontal_legs_queue = queue.Queue()

    # Create threads for vertical and horizontal movement
    vertical_thread = threading.Thread(target=vertical_legs_worker, args=(vertical_legs_queue,), daemon=True)
    horizontal_thread = threading.Thread(target=horizontal_legs_worker, args=(horizontal_legs_queue,), daemon=True)

    # Start the threads
    vertical_thread.start()
    horizontal_thread.start()

    # Simulate sending commands to the threads
    time.sleep(1)  # Delay to simulate runtime
    vertical_legs_queue.put("w")  # Move forward
    horizontal_legs_queue.put("a")  # Move left
    time.sleep(2)  # Hold both keys

    vertical_legs_queue.put("s")  # Switch to moving backward
    horizontal_legs_queue.put("d")  # Switch to moving right
    time.sleep(2)

    # Stop the threads
    vertical_legs_queue.put("STOP")
    horizontal_legs_queue.put("STOP")

    # Wait for threads to finish
    vertical_thread.join()
    horizontal_thread.join()

    print("All threads have finished.")
