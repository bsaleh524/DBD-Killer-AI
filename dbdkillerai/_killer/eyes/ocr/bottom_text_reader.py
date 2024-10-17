import easyocr
import cv2

# Can we instead have an option, where every few seconds, we would read the text? That worked!
# So, we added a frame delay AND we should only include this in the survey state.
# TODO: Add above notes to script. Make another issue to include the OCR in the SURVEY> state only
    # This will move to a pickup action for a CHASE state, but make another issue for that and tackle it later

def setup_reader():
    reader = easyocr.Reader(['en'])
    return reader

def get_interaction_text(reader: easyocr.Reader, image):
    # result = reader.readtext("dbdkillerai/_killer/eyes/ocr/sample_text.png")
    result = reader.readtext(image)

    # Input proper buttons
    for (bbox, text, prob) in result:
        if "DAMAGE" in result:
            print("Damage Detected! Pressing SPACE...")

current_reader = setup_reader()

# Initialize webcam
cap = cv2.VideoCapture(0)  # Change '0' if using an external camera
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# cap.set(CV_CAP_PROP_FOURCC, CV_FOURCC('H', '2', '6', '4')) # Tell it its H264

# Loop to continuously read the camera input
i = 0
while True:
    # Capture each frame from the camera
    ret, frame = cap.read()
    
    if not ret:
        print("Failed to grab frame")
        break
    i += 1

    if i == 50:
        print("index reached")
        i = 0
        # Convert frame to grayscale (optional but improves OCR performance)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # get_interaction_text(current_reader, gray)

        # Perform text detection
        results = current_reader.readtext(gray)

        # Loop through detected text and print it
        for (bbox, text, prob) in results:
            # Bounding box coordinates
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))

            # Draw rectangle around the detected text
            cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

            # Put the detected text on the frame
            cv2.putText(frame, text, top_left, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Print text to console
            print(f"Detected Text: {text} (Confidence: {prob:.2f})")

    # Display the frame with detected text
    cv2.imshow('Camera Feed - Press q to exit', frame)

    # Press 'q' to break the loop and exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()