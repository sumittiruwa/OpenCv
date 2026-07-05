import cv2 

camera = cv2.VideoCapture(0)  # Initialize the camera (0 for default camera)
frame_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
# Define the codec and create VideoWriter object



codec  = cv2.VideoWriter_fourcc(*'XVID')  # You can change the codec as needed
out = cv2.VideoWriter('output.avi', codec, 20.0, (frame_width, frame_height))

while True:
    success, image = camera.read()  # Read a frame from the camera
    if not success:
        print("Error: Unable to read video frame.")
        break
    out.write(image)  # Write the frame to the output video
    cv2.imshow("Recording Video", image)  # Display the frame
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to stop recording
        print("Stopping video recording.")
        break

# Release the camera and the VideoWriter
camera.release()
out.release()
cv2.destroyAllWindows()