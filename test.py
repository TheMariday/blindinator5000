# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)  #
gridx = 13
gridy = 6

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)


cam = Camera(1)
cam.set_exposure(-8)
mouseX = 0
mouseY = 0


# cv2.namedWindow('img')
# cv2.setMouseCallback('img',draw_circle)

H = None
while True:

    img = cam.read(color=True)
    checker = np.zeros(((gridy + 4) * 10, (gridx + 4) * 10, 3))
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    if H is None:

        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv.findChessboardCorners(gray, (gridx, gridy), None)

        # If found, add object points, image points (after refining them)
        if not ret:
            continue

        corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        # corners2 = corners

        # Draw and display the corners
        cv.drawChessboardCorners(img, (gridx, gridy), corners2, ret)

        H, a = cv.findHomography(corners, objp)

    else:

        # image_point = (mouseX,mouseY)
        red_blur = cv.blur(img[:, :, 2], [5, 5])
        minV, maxV, minL, maxL = cv.minMaxLoc(red_blur)
        image_point = maxL
        cx, cy = map_point_to_checkerboard_frame(H, image_point)

        # cv2.drawMarker(img, image_point, (128,0,0))

        cv.drawMarker(
            checker,
            (int((gridx - cx + 1) * 10.7), int((gridy - cy + 1) * 11.2)),
            (0, 255, 0),
        )

    # cv.imshow('img', img)
    checker_full = cv.resize(checker, (1280, 720))
    checker_full = checker_full[29:, :]

    cv.imshow("checker", checker_full)
    cv.waitKey(1)

cv.destroyAllWindows()
