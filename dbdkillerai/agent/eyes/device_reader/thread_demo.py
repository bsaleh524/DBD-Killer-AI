from dbdkillerai.agent.eyes.device_reader.vid_show_and_tell import (
    VideoGet, VideoShow)
import platform
import cv2


def customthreadBoth(source=0):
    """
    Dedicated thread for grabbing video frames with VideoGet object.
    Dedicated thread for showing video frames with VideoShow object.
    """
    pass

def threadVideoShow(source=0, yolo_results=None, class_labels=None):
    """
    Dedicated thread for showing video frames with VideoShow object.
    Main thread grabs video frames.
    """

    cap = cv2.VideoCapture(source)
    (grabbed, frame) = cap.read()
    video_shower = VideoShow(frame).start()

    while True:
        (grabbed, frame) = cap.read()
        if not grabbed or video_shower.stopped:
            video_shower.stop()
            break
        
        if yolo_results:
            for result in yolo_results[0].boxes:
                    x1, y1, x2, y2 = map(int, result.xyxy[0])
                    cls = int(result.cls)
                    conf = float(result.conf)
                    label = f"{class_labels[cls]} {conf:.2f}"
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        video_shower.frame = frame

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
    # Runs on PC only. So, this logic does a smaller test on Mac.
    if platform.system() != "Darwin":
        threadBoth(source=device)
    else:
        print("We on the bigMac now huh?")
        threadVideoGet(device)

