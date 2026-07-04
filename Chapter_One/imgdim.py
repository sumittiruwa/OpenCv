import cv2 

image = cv2.imread("1.jpg")

if image is not None:
    h, w, c = image.shape
    print(f"Image Loades: \nHeight: {h}\nWidth: {w}\nChannels: {c}")
else:
    print("Error: Image not found.")