import cv2
import supervision as sv
import numpy as np
from ultralytics import YOLO
from dbdkillerai.utils.utils import find_best_model

# Function to get object coordinates and classes
def get_object_info(model, frame):
    all_detections = {}
    results = model(frame)
    for idx, result in enumerate(results):
        # Pick out all boxes
        boxes = result.boxes

        # Grab class boxes and their labels
        for box in boxes:
            detection_class = box.cls            
            detection_width = box.xywhn[0][2]
            detection_height = box.xywhn[0][3]
            detection_x_corr = box.xywhn[0][0] #+ 0.5 * detection_width  # Top Left conv to center
            detection_y_corr = box.xywhn[0][1] #+ 0.5 * detection_height  # Top Left conv to center
            detection_area = detection_width * detection_height
        if len(boxes) == 0:
            continue
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

        # Assign symbols or emojis based on object class
        if detections[detection]['class'][0] == 0:  # Generator
            symbol = "G" #"⚡"
        elif detections[detection]['class'][0] == 1:  # Hook
            symbol = "H" #"🪝" 
        else:
            symbol = "?"
       
        # Draw the symbol at the object's position
        # cv2.putText(minimap, symbol, (detections[detection]['x'].item(), detections[detection]['y'].item()), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Draw the symbol at the object's position on the minimap
        minimap_x = int(detections[detection]['x'].item() * minimap.shape[1])  # Scale to minimap width
        minimap_y = int(detections[detection]['y'].item() * minimap.shape[0])  # Scale to minimap height
        cv2.putText(minimap, symbol, (minimap_x, minimap_y), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)


# Function to draw markers on the minimap with symbols or emojis
def draw_minimap_on_frame(frame, minimap, x_offset, y_offset):
    # Get the height and width of the minimap
    minimap_height, minimap_width, _ = minimap.shape

    # Extract the region of interest (ROI) from the original frame
    roi = frame[y_offset:y_offset+minimap_height, x_offset:x_offset+minimap_width]

    # Create a mask for the minimap
    minimap_gray = cv2.cvtColor(minimap, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(minimap_gray, 1, 255, cv2.THRESH_BINARY_INV)

    # Apply the minimap on the ROI
    roi = cv2.bitwise_and(roi, roi, mask=cv2.bitwise_not(mask))
    minimap = cv2.bitwise_and(minimap, minimap, mask=mask)
    roi = cv2.add(roi, minimap)

    # Put the modified ROI back into the original frame
    frame[y_offset:y_offset+minimap_height, x_offset:x_offset+minimap_width] = roi

# Function to draw a triangle on the minimap
def draw_triangle(minimap):
    # Get the center coordinates of the minimap
    center_x = int(minimap.shape[1] / 2)
    center_y = int(minimap.shape[0] / 2)

    # Define the vertices of the triangle
    #(centerx, centery), topleft: (0, minimap_shape0), topright:(minimap)
    vertices = np.array([[center_x, center_y], [0, 0], [minimap.shape[1], 0]], np.int32)

    # Reshape the vertices to form a triangle
    vertices = vertices.reshape((-1, 1, 2))

    # Draw the triangle on the minimap
    cv2.polylines(minimap, [vertices], isClosed=True, color=(255, 255, 255), thickness=2)


# Main loop
VIDEO_PATH = f"/home/mreag/repos/DBD-Killer-AI/data/raw/huntress_chase.mp4"
cap = cv2.VideoCapture(VIDEO_PATH)
video_info = sv.VideoInfo.from_video_path(VIDEO_PATH)

# Output video file
output_path = "output_video.mp4"
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, 15.0, (int(cap.get(3)), int(cap.get(4))))


# Grab the best model from the runs directory, only validation(train) runs
# target_data_value is the desired dataset to filter runs from.
best_model_info = find_best_model(runs_directory="/home/mreag/repos/DBD-Killer-AI/notebooks/runs/detect/",
                                   folder_type="train", # train = "val" mAP
                                   target_data_value=f"deadbydaylightkillerai/killer_ai_object_detection/{5}")
if best_model_info is not None:
    run_folder = best_model_info["model_folder"]
    model = YOLO(model=best_model_info["weights_path"])
else:
    raise('no model found')


while True:
    # Get frame from your camera or video stream
    ret, frame = cap.read()

    if not ret:
        break

    # Get object coordinates and classes from the frame
    detections = get_object_info(model, frame)

    # Create a minimap of the same size as the frame
    minimap = frame.copy()

    # Calculate the size of the minimap based on frame dimensions
    minimap_width = int(frame.shape[1] / 4)
    minimap_height = int(frame.shape[0] / 3)

    # Create a minimap of dynamically calculated size
    minimap = np.zeros((minimap_height, minimap_width, 3), dtype=np.uint8)

    # Draw markers on the minimap with symbols or emojis
    draw_minimap(minimap, detections)

    # Draw a triangle on the minimap
    draw_triangle(minimap)

    # Draw the minimap on the original frame
    draw_minimap_on_frame(frame, minimap, x_offset=0, y_offset=0)

    # Save the frame with minimap to the output video
    out.write(frame)
    print('wrote frame')

# Release the camera and close windows
cap.release()
out.release()
# cv2.destroyAllWindows()