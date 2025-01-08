Dead By Daylight Killer AI
==============================

<img src="references/figures/yolov8_train8.gif" width=700>


An Object detection and tracking model for a killer in Dead by Daylight. This repo's goal is stand up an AI that will hunt, chase, kill, and hook survivors that are identified while navigating between generators without any human input. 

Object detection is done using a [Yolov8](https://docs.ultralytics.com/) model. Labeling was done manually through [Roboflow](roboflow.com). Text detection is accomplished using [EasyOCR](https://github.com/JaidedAI/EasyOCR).


## Milestones

1. Chase one survivor, hit them twice, and hook the survivor (no RL).
2. Determine how far objects are. Make a minimap
2. Train a model to navigate using RL. It should use our distances.
4. Setup continuous RL training.
5. Have it win against bots. At least 2-3 kills.
6. Face off against Twitch Streamers.

## System Diagram:

<img src="references/figures/architecture.jpg" height=400>

### State Diagram:

<img src="references/figures/StateSpace.jpg" height=400>

## What this repository does:

- [ ] Object Detection
    - [x] Generators
    - [X] Pallets
    - [x] Hooks
    - [X] Survivors
    - [X] Downed Survivors
    - [X] Activity
    - [X] Exit Gate
    - [ ] Hatchets (Huntress)
    - [ ] Traps (Trapper)
- [ ] Track Survivors that actively move in the environment using DeepSORT.
- [ ] Build a map from stationary, key generators and hooks.
- [ ] Navigate to generators and survey them for survivors.
- [ ] Chase and hit survivors until they are down.
- [ ] Pickup a survivor, navigate to a hook, and hook a survivor.
- [ ] Be able to switch between states:
    - [ ] Survey (Generators, Activity)
    - [ ] Chase
    - [ ] Hook
- [ ] Include a priority queue for switching between states and performing certain actions.
- [ ] **TBD**

## How the Killer actually moves

**TBD**
The killer moves through `pyautogui` to issue commands in order to move about the environment.

## Setup Guide

**Work in Progress**

### ENvironment

If you are on a Mac, run:

```bash
conda env create -f env_mac.yml
```

If you are on the WSL2 Ubuntu machine(or any other linux), run:

```bash
# Run these bottom three if you don't have an ~/.Xauthority file
touch ~/.Xauthority
xauth add ${HOST}:0 . $(xxd -l 16 -p /dev/urandom)
xauth list

conda env create -f env_linux.yml
```

Then, for both machines, run: 

```bash
conda activate dbd_ai
pip install .
```

### Testing the Agent

This portion will cover the instructions for running the agent. Two portions need to be accomplished before running: Rebuilding the WSL2 image(kernel?) to include the ability to register USB video capture devices and then attaching the device to your WSL2 instance. If you've already done these steps prior, you can skip to the code execution section.

#### Rebuilding the kernel.

The WSL2 Ubuntu image, out of the box(aka from Microsoft), does not include the ability to register USB video capture devices to WSL2. In order to get it in, you need to rebuild the WSL2 image.

Follow all instructions from this: https://www.youtube.com/watch?v=t_YnACEPmrM

These same instructions were placed in the `references` folder in a bit more detail.

#### Attaching the Video Capture Device

After rebuilding it and reloading the image, we now need to attach it to WSL2. 

1. First, plug in your device. Be it webcam or USB video capture.
2. (Windows): Run `usbipd list` in a Windows Admin Command Line/Terminal. You'll get something similar to this:
  - ```
    C:\Windows\System32>usbipd list
    Connected:
    BUSID  VID:PID    DEVICE                                                        STATE
    1-4    048d:8297  USB Input Device                                              Not shared
    2-5    8087:0aa7  Intel(R) Wireless Bluetooth(R)                                Not shared
    3-1    046d:082d  HD Pro Webcam C920                                            Not shared
    3-2    17a0:0241  Samson G-Track Pro                                            Not shared
    7-1    046d:c539  LIGHTSPEED Receiver, USB Input Device                         Not shared
    8-2    04d8:eed2  USB Input Device                                              Not shared
    10-1   264a:2267  USB Input Device                                              Not shared
    ```

3. (Windows): Bind it if it's not already been binded before using `usbipd bind --busid=<BUSID>`. Example: the `usbipd bind --busid=3-1` is referencing the webcam BUSID
4. (Windows): Attach it to WSL2 using `usbipd attach --wsl --busid=<BUSID>`
5. (WSL2): Give it a few seconds. Then run the `detect_devices.py` script to check if it exists.

If you run `detect_devices.py` and it doesn't show up, it more than likely is because the feed coming in isn't proper. Sometimes you'll see a device listed in the script as an output, but when opencv loads it, it errors out, something about CVT color being empty or something similar. I would unattach/unbind/unplug and then redo all the steps again. Also make sure you are on a windows admin terminal. 

### Running the Code

#### Test the Agent can see

Use the `test_ocr.py` script located in the `test/` folder to ensure the agent properly starts. It should output a few pictures detailing what the YOLO model sees on screen.

And, now that you have the camera module, the Agent relies entirely on the fact that you should have only one camera/capture card connected, which is what you just attached and tested. 

Connect the Macbook to the PC using the USB capture card as a device input. Load the game on the Mac's newest screen. Then, run `main_agent.py`. An easy test before running the game on NVIDIA GeForce NOW is to use a Youtube video.

-----------
Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
