# cv2.rectangle(img, pt1, pt2, color, thickness)


# to higlhight the rectangle we can use thickness = -1 to fill the rectangle with color
# eg: face, animal, and other objects in the image can be highlighted using rectangle function

import cv2

image = cv2.imread("spidermen.jpg")

if image is None:
    print("Error: Image not found.")
else:
  print("Image Loaded Successfully")
  pt1 = (100, 100)
  pt2 = (200, 200)
  color = (0, 0, 255)  # Red color in BGR
  cv2.rectangle(image, pt1, pt2, color, thickness=5)  # Draw rectangle with thickness 5
  cv2.imshow("Image with Rectangle", image)
  cv2.waitKey(0)
  cv2.destroyAllWindows()