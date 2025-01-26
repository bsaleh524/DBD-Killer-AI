from dbdkillerai.agent.eyes.device_reader.vid_show_and_tell import (
    VideoGet, VideoShow)
import platform
import cv2


def threadBoth(source=0):
    """
    Dedicated thread for grabbing video frames with VideoGet object.
    Dedicated thread for showing video frames with VideoShow object.
    Main thread serves only to pass frames between VideoGet and
    VideoShow objects/threads.
    """

    video_getter = VideoGet(source).start()
    video_shower = VideoShow(video_getter.frame).start()

    while True:
        if video_getter.stopped or video_shower.stopped:
            video_shower.stop()
            video_getter.stop()
            break

        frame = video_getter.frame
        video_shower.frame = frame

def threadVideoGet(source=0):
    """
    Dedicated thread for grabbing video frames with VideoGet object.
    Main thread shows video frames.
    """

    video_getter = VideoGet(source).start()

    while True:
        if (cv2.waitKey(1) == ord("q")) or video_getter.stopped:
            video_getter.stop()
            break

        frame = video_getter.frame
        cv2.imshow("Video", frame)



if __name__ == "__main__":
    device = 1
    if platform.system() != "Darwin":
        threadBoth(source=device)
    else:
        print("We on the bigMac now huh?")
        threadVideoGet(device)

