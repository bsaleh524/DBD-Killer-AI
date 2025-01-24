import cv2

def read_screen_capture(capture_device, vision_queue):
    """Read the input device's screen. Output frame and return value"""
    while True:
        ret, frame = capture_device.read()
        vision_queue.put(frame)
        if not ret:
            raise("Failed to grab frame. Check devices!")
        # return frame

if __name__ == "__main__":
    pass