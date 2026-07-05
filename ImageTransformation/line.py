import cv2 

image = cv2.imread("spidermen.jpg")

if image is None:
    print("Error: Image not found.")

else:
    print("Image Loaded Successfully")
    pt1 = (100, 100)
    pt2 = (200, 200)
    color = (0, 255, 0)  # Green color in BGR
    thickness = 10  # Thickness of the rectangle border
    cv2.line(image, pt1, pt2, color, thickness)
    cv2.imshow("Image with Line", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    