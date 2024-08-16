import cv2

cv2.namedWindow("t",cv2.WINDOW_NORMAL)
cv2.setWindowProperty("t",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

cam = cv2.VideoCapture(0)

while True:
    frame = cam.read()[1]
    frame = cv2.resize(frame, (1920,1080))
    cv2.imshow("t",frame)
    k = cv2.waitKey(1)
    if k == -1:
        continue
    if k == 27:
        break

    print(ord(k))