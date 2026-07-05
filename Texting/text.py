import cv2

image = cv2.imread("spidermen.jpg")
if image is None:
    print("Error: Image not found.")
else:
    print("Image Loaded Successfully")
    cv2.putText(image, "Hello, OpenCV!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.imshow("Original Image", image)

    
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()