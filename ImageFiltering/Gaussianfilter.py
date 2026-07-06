# remove the sharp image .. make it smooth 
#uses
 #   - remove the noise 
 #   - Smooth the image
 #   - Backgroud blur
 
 # syntax 
 # blurred = cv2.GaussianBlur(image, (kernal_size_x, Kernal_size_y), sigma)

import cv2 

image = cv2.imread("messi.jpg")

blurred = cv2.GaussianBlur(image, (91,91),0)


cv2.imshow("original Image", image)
cv2.imshow("Blureed Image", blurred)
cv2.waitKey(0)
cv2.destroyAllWindows()