# Testing the Agent

This portion will cover the instructions for running the agent. Two portions need to be accomplished before running: Rebuilding the WSL2 image(kernel?) to include the ability to register USB video capture devices and then attaching the device to your WSL2 instance. If you've already done these steps prior, you can skip to the code execution section.

## Rebuilding the kernel.

The WSL2 Ubuntu image, out of the box(aka from Microsoft), does not include the ability to register USB video capture devices to WSL2. In order to get it in, you need to rebuild the WSL2 image.

Follow all instructions from this: https://www.youtube.com/watch?v=t_YnACEPmrM

These same instructions were placed in the `references` folder in a bit more detail.

## Attaching the Video Capture Device

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

# Running the Code

## Test the Agent can see

Use the `test_ocr.py` script located in the `test/` folder to ensure the agent properly starts. It should output a few pictures detailing what the YOLO model sees on screen.

And, now that you have the camera module, the Agent relies entirely on the fact that you should have only one camera/capture card connected, which is what you just attached and tested. 

Simply run `main_agent.py`. Have you connected camera device play a youtube video to see detections.