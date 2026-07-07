import cv2

# used to detect the border
# seperate the object s 
# edges = cv2.Canny(image, thresold1, threshold2)
# threshold - setup the cut ot poiint for the pixels


image = cv2.imread("flower.jpg",cv2.IMREAD_GRAYSCALE)

edges = cv2.Canny(image, 50 , 150)
cv2.imshow("original image", image)
cv2.imshow("after", edges)

cv2.waitKey(0)
cv2.destroyAllWindows()