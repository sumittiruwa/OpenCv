# cap = cv2.VideoCapture(source)

import cv2


cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to read video frame.")
        break
    cv2.imshow("Video Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting video capture.")
        break
cap.release()
cv2.destroyAllWindows()