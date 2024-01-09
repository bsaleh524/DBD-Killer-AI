import ultralytics
from ultralytics import YOLO

# ultralytics.checks()

# Create a new YOLO model from scratch
model = YOLO('models/yolov8n.pt')

# Train the model using the 'coco128.yaml' dataset for 3 epochs
results = model.train(data="data/external/data.yaml",
                      epochs=1,
                      imgsz=800,
                      plots=True,
                      workers=0)

# Evaluate the model's performance on the validation set
results = model.val()

# Perform object detection on an image using the model
# results = model('https://ultralytics.com/images/bus.jpg')

# Export the model to ONNX format
# success = model.export(format='onnx')