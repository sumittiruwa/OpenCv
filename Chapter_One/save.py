import cv2

# Read the image
image = cv2.imread("1.jpg")

if image is not None:
    success = cv2.imwrite("sve.jpg", image)

    if success:
        print("Image saved successfully.")
    else:
        print("Error: Could not save the image.")
else:
    print("Error: Image not found.")