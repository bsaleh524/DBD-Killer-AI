## TODO

1. Make the env file for storing keys
2. Use `make_dataset.py` with the first part of the notebok
3. Make a pipeline that ingests recorded video data and automatically begin labeling data for the dataset
    - Requires you to still look at stuff. So, maybe not until stuff happen.
4. Determine if the other latop can run DBD
5. How to determine how far an object is before interacting with it(survivor, generator, pallet, etc).
6. How to determine what map is in place right now?
    - Database of maps to pull from. There is a list of maps and variations on wiki
    - How can we determine what map we are on using the text on the bottom left?
7. How to determine what path can the agent travel in?
    - Maybe this relates to the map?
8. Create a virtual view for the user
    - Create a minimap for the engineer to see. It should be topdown.
    - When the agent sees a minimap, maybe it should be saved on a location.
    - FOV triangle on another minimap display.
    - 


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


# Optimizations

Multiprocessing for OCR can help, but if multiprocessing is needed, you must initialize the OCR model within the `ocr_pipeline` because the model uses CUDA(apparently) and it's trying to initialize ocr again, but since we are already using the YOLO for cuda in the main loop, it dumps this error:

    ```(dbd_ai) (base) mreag@DESKTOP-TOE9IUK:~/repos/DBD-Killer-AI$ /home/mreag/miniconda3/envs/dbd_ai/bin/python /home/mreag/repos/DBD-Killer-AI/dbdkillerai/agent/main_agent.py
    /home/mreag/repos/DBD-Killer-AI/dbdkillerai/agent/main_agent.py:12: DeprecationWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html
    from pkg_resources import parse_version
    cuda
    FPS: 30.0
    Starting all threads and processes...
    Agent is Ready!
    frame added to ocr queue. new size: 1
    Process Process-1:
    Traceback (most recent call last):
    File "/home/mreag/miniconda3/envs/dbd_ai/lib/python3.11/multiprocessing/process.py", line 314, in _bootstrap
        self.run()
    File "/home/mreag/miniconda3/envs/dbd_ai/lib/python3.11/multiprocessing/process.py", line 108, in run
        self._target(*self._args, **self._kwargs)
    File "/home/mreag/miniconda3/envs/dbd_ai/lib/python3.11/site-packages/dbdkillerai/agent/eyes/ocr/text_reader.py", line 33, in ocr_pipeline
        key_command_bottom, bbox_bottom_text = get_interaction_text(
                                            ^^^^^^^^^^^^^^^^^^^^^
    File "/home/mreag/miniconda3/envs/dbd_ai/lib/python3.11/site-packages/dbdkillerai/agent/eyes/ocr/text_reader.py", line 53, in get_interaction_text
        result = reader.readtext(image)
                ^^^^^^^^^^^^^^^^^^^^^^
    File "/home/mreag/miniconda3/envs/dbd_ai/lib/python3.11/site-packages/easyocr/easyocr.py", line 456, in readtext
        horizontal_list, free_list = self.detect(img,
                                    ^^^^^^^^^^^^^^^^
    File "/home/mreag/miniconda3/envs/dbd_ai/lib/python3.11/site-packages/easyocr/easyocr.py", line 321, in detect
        text_box_list = self.get_textbox(self.detector,
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "/home/mreag/miniconda3/envs/dbd_ai/lib/python3.11/site-packages/easyocr/detection.py", line 95, in get_textbox
        bboxes_list, polys_list = test_net(canvas_size, mag_ratio, detector,
                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    File "/home/mreag/miniconda3/envs/dbd_ai/lib/python3.11/site-packages/easyocr/detection.py", line 42, in test_net
        x = x.to(device)
            ^^^^^^^^^^^^
    File "/home/mreag/miniconda3/envs/dbd_ai/lib/python3.11/site-packages/torch/cuda/__init__.py", line 305, in _lazy_init
        raise RuntimeError(
    RuntimeError: Cannot re-initialize CUDA in forked subprocess. To use CUDA with multiprocessing, you must use the 'spawn' start method
    ```