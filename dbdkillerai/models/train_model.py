from ultralytics import YOLO
from typing import Any
import os
# ultralytics.checks()

def train_yolo(yolo_model: YOLO, data_yml: str, epochs: int = 150, imgsz: int=800,
               plots: bool = True, workers: int = 0, device: Any = 0):
    # Create a new YOLO model from scratch
    # model = YOLO(model=yolo_model)

    # Train the model using the dataset for all loaded parameters
    results_train = yolo_model.train(data=data_yml,
                        epochs=epochs,
                        imgsz=imgsz,
                        plots=plots,
                        workers=workers,
                        device=device)

    return yolo_model, results_train

def validate_yolo(yolo_model: YOLO, data_yml: str, plots: bool = True):
    # Evaluate the model's performance on the validation set
    
    results_val = yolo_model.val(data=data_yml,
                                 plots=plots)
    
    return results_val