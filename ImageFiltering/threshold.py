import cv2


image = cv2.imread("messi.jpg",cv2.IMREAD_GRAYSCALE)

ret, thres_img = cv2.threshold(image, 120 , 277, cv2.THRESH_BINARY)

cv2.imshow("original image", image)
cv2.imshow("after", thres_img)

cv2.waitKey(0)
cv2.destroyAllWindows()