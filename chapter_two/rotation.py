# roatating the image ..

import cv2

# syntax for rotation

# M = cv2.getRotationMatrix2D(center, angle, scale)
# rotation_image = cv2.warpAffine(image, M, (width, height))


image = cv2.imread("spidermen.jpg")

if image is  None:
    print("could not find the image.")
    
else:
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, 90, 1.0) # 1.0 is a scale factor
    rotated_image = cv2.warpAffine(image, M, (w, h))
    rotated = cv2.warpAffine(image, M, (w, h))
    
    cv2.imshow("Original Image", image)
    cv2.imshow("Rotated Image", rotated_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows