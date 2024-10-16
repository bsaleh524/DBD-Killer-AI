import cv2

# Function to check available camera devices
def list_cameras(max_devices=10):
    available_devices = []
    for i in range(max_devices):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_devices.append(i)
            cap.release()
    return available_devices

# List available camera devices
cameras = list_cameras()
if cameras:
    print(f"Available camera devices: {cameras}")
else:
    print("No camera devices found.")