from threading import Thread
from queue import Queue
from dbdkillerai.agent.eyes.ocr.text_reader import setup_camera
import cv2

class VideoGetter:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self,
                 device=0,
                 test_image=False,
                 vid_preset=0):
        
        # Get presets for video quality. Small or Large
        if vid_preset == 0:
            height=640
            width=480
        elif vid_preset == 1:
            height=720
            width=1280
        
        # Setup the camera
        self.stream = setup_camera(test_image=test_image,
                                    device=device,
                                    height=height,
                                    width=width,
            )
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        self.queue = Queue()

    def start(self):    
        self.thread = Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                (self.grabbed, self.frame) = self.stream.read()
                self.queue.put(self.frame)
        print(f"Video getter stopped. finish yolo?")

    def stop(self):
        self.stopped = True
        self.stream.release()
        self.thread.join()
    
    def get_fps(self):
        return self.stream.get(cv2.CAP_PROP_FPS)
