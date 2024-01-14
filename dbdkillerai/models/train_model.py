from ultralytics import YOLO

# ultralytics.checks()

def train_yolo(yolo_model: str, data_yml: str, epochs: int = 150, imgsz: int=800,
               plots: bool = True, workers: int = 0):
    # Create a new YOLO model from scratch
    model = YOLO(model=yolo_model)

    # Train the model using the 'coco128.yaml' dataset for 3 epochs
    results_train = model.train(data=data_yml,
                        epochs=epochs,
                        imgsz=imgsz,
                        plots=plots,
                        workers=workers)

    # Evaluate the model's performance on the validation set
    results_val = model.val()

    return model, results_train, results_val