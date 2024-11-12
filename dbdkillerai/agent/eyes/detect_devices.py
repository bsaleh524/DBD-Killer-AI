import cv2

# Function to list available camera devices and their properties
def list_cameras_info(max_devices=10):
    available_devices_info = {}
    for i in range(max_devices):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            # Get device properties
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            available_devices_info[i] = {
                'Width': width,
                'Height': height,
                'FPS': fps,
            }
            cap.release()
    
    return available_devices_info

# List and print camera device info
cameras_info = list_cameras_info()
if cameras_info:
    for device, info in cameras_info.items():
        print(f"Camera {device}:")
        for key, value in info.items():
            print(f"  {key}: {value}")
else:
    print("No camera devices found.")
