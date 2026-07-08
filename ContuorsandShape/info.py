import cv2


img = cv2.imread("messi.jpg")

if img is None:
    print("Image not found!")
    exit()


gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


blur = cv2.GaussianBlur(gray, (5, 5), 0)

# Edge detection
edges = cv2.Canny(blur, 50, 150)

# Find contours
contours, hierarchy = cv2.findContours(
    edges,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)

for cnt in contours:

    area = cv2.contourArea(cnt)

    # Ignore small contours
    if area < 500:
        continue

    perimeter = cv2.arcLength(cnt, True)

    approx = cv2.approxPolyDP(cnt, 0.02 * perimeter, True)

    # Bounding rectangle
    x, y, w, h = cv2.boundingRect(approx)
    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Detect shape
    sides = len(approx)

    if sides == 3:
        shape = "Triangle"
    elif sides == 4:
        ratio = w / float(h)
        if 0.95 <= ratio <= 1.05:
            shape = "Square"
        else:
            shape = "Rectangle"
    elif sides == 5:
        shape = "Pentagon"
    elif sides == 6:
        shape = "Hexagon"
    else:
        shape = "Circle"


    cv2.putText(img, shape, (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (255, 0, 0), 2)

    print("--------------------")
    print("Shape :", shape)
    print("Area :", area)
    print("Perimeter :", perimeter)

cv2.imshow("Edges", edges)
cv2.imshow("Detected Shapes", img)

cv2.waitKey(0)
cv2.destroyAllWindows()