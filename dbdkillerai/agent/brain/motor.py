from threading import Thread
from queue import Queue

class MotorWorker:
    """
    Class that functions as a thread to send brain
    commands to the different limb queues based upon
    the decision it ends up making. Also allows
    graceful stopping."""

    def __init__(self,):
        self.stopped = False

    def start(self,
              motor_queue: Queue,
              right_arm_queue: Queue,):
        #TODO: Put in other limb queues

        "Start the thread"
        self.thread = Thread(target=self.get,
                             args=(motor_queue, right_arm_queue,)
                             ).start()

    def get(self, motor_queue, right_arm_queue):
        "Do actions from queue, given by brain."
        while not self.stopped:
            current_command = motor_queue.get()
            if current_command:
                if current_command == "SWING":
                    print("MOTOR || Brain commanded me to do: ", current_command)
                    right_arm_queue.put("SWING")
        print("Motor Worker stopped.")

    def stop(self):
        self.stopped = True
        # if self.thread is not None:
        #     self.thread.join()  # Ensure thread joins before exiting