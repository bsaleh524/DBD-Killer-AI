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

# Function to start live video stream from a selected camera
def start_camera_stream(device_index):
    cap = cv2.VideoCapture(device_index)
    if not cap.isOpened():
        print(f"Unable to open camera {device_index}.")
        return
    
    print(f"Streaming from camera {device_index}. Press 'q' to quit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame. Exiting.")
            break
        
        cv2.imshow(f"Camera {device_index}", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
            break
    
    cap.release()
    cv2.destroyAllWindows()

# Main function
def main():
    cameras_info = list_cameras_info()
    if not cameras_info:
        print("No camera devices found.")
        return
    
    print("\nAvailable Camera Devices:")
    for device, info in cameras_info.items():
        print(f"\nCamera {device}:")
        for key, value in info.items():
            print(f"  {key}: {value}")
    
    try:
        selected_device = int(input("\nEnter the device index to start streaming (e.g., 0, 1): "))
        if selected_device in cameras_info:
            start_camera_stream(selected_device)
        else:
            print("Invalid device index. Exiting.")
    except ValueError:
        print("Invalid input. Please enter a numeric device index.")

if __name__ == "__main__":
    main()
