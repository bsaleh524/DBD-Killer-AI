## TODO

1. Make the env file for storing keys
2. Use `make_dataset.py` with the first part of the notebok
3. 


- notebook is for exploring data, not training it.

- the `best.pt` is based on mAP during training agaisnt validation set

https://github.com/ultralytics/ultralytics/issues/4096
"Absolutely, you are welcome to ask questions here, and we're here to help!

In YOLOv8, the best.pt file is determined by monitoring a specific metric during the validation phase after each training epoch. By default, this metric is the mean Average Precision (mAP) at different IoU thresholds, as it provides a balanced view of the model's precision and recall across all classes and object sizes.

The calculation of mAP involves predicting bounding boxes on the validation set and comparing these with the ground truth annotations. For each class, precision-recall curves are generated based on the model predictions at varying confidence thresholds. The area under these curves is averaged over all classes and IoU thresholds to produce the final mAP score.

During training, after each epoch, the model is evaluated on the validation set, and the mAP is calculated. **The weights from the epoch which achieve the highest mAP score are saved as best.pt**. This means that the model saved in best.pt is the one that had the best balance of precision and recall on your validation dataset, according to the mAP metric.

Please note that if you're interested in prioritizing a different metric for performance evaluation, such as validation box loss, this can often be configured in the training script or via the command line arguments when initiating your training run. This will allow you to save the best.pt according to your preferred metric.

Hope this clarifies the process for determining the best.pt weights in YOLOv8. If you have more questions or need further assistance, feel free to reach out.

Best regards,
Glenn Jocher"