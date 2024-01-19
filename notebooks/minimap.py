import cv2
import supervision as sv
import numpy as np
from ultralytics import YOLO
from dbdkillerai.utils.utils import find_best_model

# Function to get object coordinates and classes
def get_object_info(model, frame):
    # Replace this with your actual object detection code
    # Return a list of tuples (x, y, area, class) for each detected object
    # Example: [(x1, y1, area1, class1), (x2, y2, area2, class2), ...]
    all_detections = {}
    results = model(frame)
    for idx, result in enumerate(results):
        # Pick out all boxes
        boxes = result.boxes

        # Grab class boxes and their labels
        for box in boxes:
            detection_class = box.cls
            detection_x_corr = box.xywhn[0][0]  # Center?
            detection_y_corr = box.xywhn[0][1]  # Center?
            detection_width = box.xywhn[0][2]
            detection_height = box.xywhn[0][3]
            detection_area = detection_width * detection_height
        all_detections[idx] = {'class': detection_class,
                               'x': detection_x_corr,
                               'y': detection_y_corr,
                               'w': detection_width,
                               'h': detection_height,
                               'area': detection_area}
    
    return all_detections

# Function to draw markers on the minimap with symbols or emojis
def draw_minimap(minimap, detections):
    for detection in detections:
        # x, y, area, obj_class = info

        # Assign symbols or emojis based on object class
        if detection['class'] == "0":  # Generator
            symbol = "⚡"
        elif detection['class'] == "1":  # Hook
            symbol = "🪝" 
        else:
            symbol = "🟥"
        # Finish here! How do you plot the "y"" on there? Maybe area * the height value?
        # Draw the symbol at the object's position
        cv2.putText(minimap, symbol, (detection['x'], detection['y']), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.circle(minimap, (x, y), 5, (0, 255, 0), -1)  # Draw a green circle at the object's position









# Main loop
VIDEO_PATH = f"/home/mreag/repos/DBD-Killer-AI/data/raw/huntress_chase.mp4"
cap = cv2.VideoCapture(VIDEO_PATH)
video_info = sv.VideoInfo.from_video_path(VIDEO_PATH)

# Grab the best model from the runs directory, only validation(train) runs
# target_data_value is the desired dataset to filter runs from.
best_model_info = find_best_model(runs_directory="/home/mreag/repos/DBD-Killer-AI/notebooks/runs/detect/",
                                   folder_type="train", # train = "val" mAP
                                   target_data_value=f"deadbydaylightkillerai/killer_ai_object_detection/{5}")
if best_model_info is not None:
    run_folder = best_model_info["model_folder"]
    model = YOLO(model=best_model_info["weights_path"])

while True:
    # Get frame from your camera or video stream
    ret, frame = cap.read()

    # Get object coordinates and classes from the frame
    detections = get_object_info(model, frame)

    # Create a minimap of the same size as the frame
    minimap = frame.copy()

    # Draw markers on the minimap with symbols or emojis
    draw_minimap(minimap, detections)

    # Display the frame and minimap
    cv2.imshow("Frame", frame)
    cv2.imshow("Minimap", minimap)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close windows
cap.release()
cv2.destroyAllWindows()