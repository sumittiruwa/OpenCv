# cv2.filter2D(src, depth, kernal)

import cv2 
import numpy as np

image = cv2.imread("messi.jpg")

sharp_kernal = np.array([
    [0,-1,0],
    [-1,5,-1],
    [0,-1,0]
])

sharpened = cv2.filter2D(image, -1, sharp_kernal)
cv2.imshow("original image", image)
cv2.imshow("sharpened image", sharpened)
cv2.waitKey(0)
cv2.destroyAllWindows()


