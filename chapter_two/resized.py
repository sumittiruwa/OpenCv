# resized = cv2.resize(src, desize, fx, fy, interpolation)
import cv2

image = cv2.imread("sve.jpg")

if image is None:
    print("Error: Image not found.")
else:
    print("Select a choice:\n1.Resize Image \n2.Save Image")
    
    resized = cv2.resize(image, (400, 400), interpolation=cv2.INTER_AREA)
    cv2.imshow("original Image", image)
    cv2.imshow("Resized Image", resized)
    
    cv2.imwrite("resized_output.png", resized)
    
    cv2.waitKey(0)
    
    cv2.destroyAllWindows()

        