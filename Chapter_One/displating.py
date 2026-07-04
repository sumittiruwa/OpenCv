import cv2

# Read the image
image = cv2.imread("1.jpg")

# Check if the image was loaded successfully
if image is None:
    print("Error: Image not found.")
else:
    cv2.imshow("Image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()