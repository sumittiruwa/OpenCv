#syntax
#cv2.circle(img, center, radius, color, thickness)


import cv2

image = cv2.imread("spidermen.jpg")
if image is None:
    print("Error: Image not found.")    
else:
    print("Image Loaded Successfully")
    center = (250, 250)  
    radius = 50 
    color = (255, 0, 0)  
    thickness = 5  
    cv2.circle(image, center, radius, color, thickness)
    cv2.imshow("Image with Circle", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
