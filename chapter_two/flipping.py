#syntax
# flipped = cv2.flip(image, flipCode)
#cv2.flip - direct fucntion to flip the image/ mirror the image
# flipcode = tell the how to flip the image (0 - vertical, 1 - horizontal, -1 - both)

# roatating the image ..

import cv2

image = cv2.imread("spidermen.jpg")

if image is  None:
    print("could not find the image.")
    
else:
    flipped_horizontally = cv2.flip(image, 1) # flip horizontally
    flipped_vertically = cv2.flip(image, 0) # flip vertically
    flipped_both = cv2.flip(image, -1) # flip both horizontally and vertically
   
   
    cv2.imshow("Original Image", image)
    cv2.imshow("Flipped Horizontally", flipped_horizontally)
    cv2.imshow("Flipped Vertically", flipped_vertically)
    cv2.imshow("Flipped Both", flipped_both)
    
    cv2.waitKey(0)
    cv2.destroyAllWindows