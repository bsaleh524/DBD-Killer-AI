## Upfront

`sudo apt update && sudo apt upgrade -y && sudo apt install -y build-essential flex bison dwarves libssl-dev libelf-dev libncurses-dev pkg-config`

https://www.youtube.com/watch?v=t_YnACEPmrM

`uname-a` gave me --> `5.15.153.1-microsoft-standard-WSL2`

1. `usbipd list` to list devices

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

2. Bind it

`usbipd bind --busid 3-1`

3. Attach it

`usbipd attach --wsl --busid=3-1`
usbipd: info: Using WSL distribution 'Ubuntu' to attach; the device will be available in all WSL 2 distributions.
usbipd: info: Using IP address [REDACTED] to reach the host.

-----------------

How to use
Share Devices

By default devices are not shared with USBIP clients. To lookup and share devices, run the following commands with administrator privileges:

```bash
usbipd --help
usbipd list
usbipd bind --busid=<BUSID>
```

Sharing a device is persistent; it survives reboots.

Tip

See the wiki for a list of tested devices.
Connecting Devices

Attaching devices to a client is non-persistent. You will have to re-attach after a reboot, or when the device resets or is physically unplugged/replugged.
Non-WSL 2

From another (possibly virtual) machine running Linux, use the usbip client-side tool:

```bash
usbip list --remote=<HOST>
sudo usbip attach --remote=<HOST> --busid=<BUSID>
```

# WSL 2

Tip

In case you have used usbipd with WSL 2 before, the following has changed since version 4.0.0:

    You have to share the device using usbipd bind first.
    You no longer have to install any client-side tooling.
    You no longer have to specify a specific distribution.
    The syntax for the command to attach has changed slightly.

You can attach the device from within Windows with the following command, which does not require administrator privileges:

```bash
usbipd attach --wsl --busid=<BUSID>
```
