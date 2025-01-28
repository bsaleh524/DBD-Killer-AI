from threading import Thread
from queue import Queue
import cv2
from dbdkillerai.agent.eyes.ocr.text_reader import setup_camera

class VideoGet:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self,
                 queue: Queue,
                 device=0,
                 test_image=False,
                 vid_preset=0):
        
        # Get presets for video quality. Small or Large
        if vid_preset == 0:
            height=640,
            width=480
        elif vid_preset == 1:
            height=720,
            width=1280
        
        # Setup the camera
        self.stream = setup_camera(test_image=test_image,
                                    device=device,
                                    height=height,
                                    width=width,
            )
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        self.queue = queue

    def start(self):    
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                (self.grabbed, self.frame) = self.stream.read()
                self.queue.put(self.frame)

    def stop(self):
        self.stopped = True


class VideoShow:
    """
    Class that continuously shows a frame using a dedicated thread.
    """

    def __init__(self, frame=None):
        self.frame = frame
        self.stopped = False

    def start(self):
        Thread(target=self.show, args=()).start()
        return self

    def show(self):
        while not self.stopped:
            cv2.imshow("Video", self.frame)
            if cv2.waitKey(1) == ord("q"):
                self.stopped = True

    def stop(self):
        self.stopped = True
