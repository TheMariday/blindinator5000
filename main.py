import cv2
import numpy as np
import cv2 as cv

WINDOW_NAME = "main"
CALIB_FILE = "checker.png"
CALIB_COLS = 13
CALIB_ROWS = 6


def cam_to_projector(homo, point):
    point_homogeneous = np.array([point[0], point[1], 1.0]).reshape((3, 1))
    mapped_point = np.dot(homo, point_homogeneous)

    # This is based off of the relationship between the checkerboard and the full
    # screen size. Don't worry about it
    cx = 1 - (mapped_point[0] / mapped_point[2] + 2) / (CALIB_COLS + 3)
    cy = 1 - (mapped_point[1] / mapped_point[2] + 2) / (CALIB_ROWS + 3)

    return cx, cy


def find_homography(cam):
    checkerboard_frame = cv.imread(CALIB_FILE)

    _, _, screen_width, screen_height = cv2.getWindowImageRect(WINDOW_NAME)

    checkerboard_frame = cv.resize(checkerboard_frame, (screen_width, screen_height))

    checkerboard_model = np.zeros((CALIB_COLS * CALIB_ROWS, 3), np.float32)
    checkerboard_model[:, :2] = np.mgrid[0:CALIB_COLS, 0:CALIB_ROWS].T.reshape(-1, 2)

    homography = None
    while True:
        cv.imshow(WINDOW_NAME, checkerboard_frame)
        key = cv.waitKey(1)

        _, img = cam.read()
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        checkerboard_success, checkerboard_corners = cv.findChessboardCorners(
            gray, (CALIB_COLS, CALIB_ROWS), None
        )

        if checkerboard_success:
            cv.drawChessboardCorners(
                img,
                (CALIB_ROWS, CALIB_COLS),
                checkerboard_corners,
                checkerboard_success,
            )
            homography, _ = cv.findHomography(checkerboard_corners, checkerboard_model)

        cv.imshow("cam", img)

        if key == 27:
            quit()
        if key == 13:
            return homography


def find_laser(img):
    red_blur = cv.blur(img[:, :, 2], [5, 5])
    _, _, _, max_location = cv.minMaxLoc(red_blur)
    return max_location


if __name__ == "__main__":
    cam = cv.VideoCapture(1, cv2.CAP_DSHOW)

    cv.namedWindow(WINDOW_NAME, cv.WINDOW_NORMAL)
    cv.setWindowProperty(WINDOW_NAME, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

    homography = find_homography(cam)

    _, _, screen_width, screen_height = cv2.getWindowImageRect(WINDOW_NAME)

    while True:
        _, cam_frame = cam.read()
        camera_x, camera_y = find_laser(cam_frame)

        projector_x, projector_y = cam_to_projector(homography, (camera_x, camera_y))

        screen_frame = np.zeros((screen_height, screen_width, 3))
        screen_x = int(projector_x * screen_width)
        screen_y = int(projector_y * screen_height)

        cv.drawMarker(
            screen_frame, (screen_x, screen_y), (0, 0.4, 0), markerSize=100, thickness=4
        )
        cv.circle(screen_frame, (screen_x, screen_y), 100, (0, 0.4, 0), 4)

        cv.drawMarker(cam_frame, (camera_x, camera_y), (0, 0.3, 0))

        cv2.imshow(WINDOW_NAME, screen_frame)
        cv2.imshow("cam", cam_frame)
        k = cv2.waitKey(1)
        if k == 27:
            quit()
