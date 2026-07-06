# synatx
# bluered = cv2.medianBlur(image, kernal_size)


import cv2
image = cv2.imread("messi.jpg")

blurred = cv2.medianBlur(image, 5)
cv2.imshow("Original", image)
cv2.imshow("clean Image", blurred)
cv2.waitKey(0)
cv2.destroyAllWindows()