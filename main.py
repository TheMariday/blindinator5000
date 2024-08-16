import cv2
import numpy as np
import cv2 as cv

from camera import Camera

WINDOW_NAME = "main"
CALIB_FILE = "checker.png"
CALIB_COLS = 13
CALIB_ROWS = 6

#global
mouseX = None
mouseY = None

def click_event(event,x,y,flags,param):
    global mouseX,mouseY
    if event == cv.EVENT_LBUTTONDOWN:
        mouseX,mouseY = x,y

def checkerboard_to_projector(H, point):
    point_homogeneous = np.array([point[0], point[1], 1.0]).reshape((3, 1))
    mapped_point = np.dot(H, point_homogeneous)
    mapped_point /= mapped_point[2]  # Convert from homogeneous coordinates

    cx, cy = mapped_point[:2]

    cx += 2
    cy += 2

    cx /= CALIB_COLS + 3
    cy /= CALIB_ROWS + 3

    cx = 1 - cx
    cy = 1 - cy

    return cx, cy

def create_window():
    cv.namedWindow(WINDOW_NAME, cv.WINDOW_NORMAL)
    cv.setWindowProperty(WINDOW_NAME, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

def find_homography(cam):
    checkerboard_frame = cv.imread(CALIB_FILE)

    checkerboard_model = np.zeros((CALIB_COLS * CALIB_ROWS, 3), np.float32)
    checkerboard_model[:, :2] = np.mgrid[0:CALIB_COLS, 0:CALIB_ROWS].T.reshape(-1, 2)

    homography = None
    while True:
        cv.imshow(WINDOW_NAME, checkerboard_frame)
        key = cv.waitKey(1)

        img = cam.read(color=True)
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        checkerboard_success, checkerboard_corners = cv.findChessboardCorners(gray, (CALIB_COLS, CALIB_ROWS), None)

        if checkerboard_success:
            cv.drawChessboardCorners(img, (CALIB_ROWS, CALIB_COLS), checkerboard_corners, checkerboard_success)
            homography, _ = cv.findHomography(checkerboard_corners, checkerboard_model)
            return homography

        cv.imshow("cam", img)

        if key == 27:
            quit()
        if key == 13:
            return homography
        if key != -1:
            print(key)

def find_laser(img):
    red_blur = cv.blur(img[:, :, 2], [5, 5])
    minV, maxV, minL, maxL = cv.minMaxLoc(red_blur)
    return maxL


if __name__ == "__main__":
    cam = Camera(1)
    create_window()
    homography = find_homography(cam)
    print(homography)

    while True:
        cam_frame = cam.read(color=True)
        laser_pos = find_laser(cam_frame)

        checker_x, checker_y = checkerboard_to_projector(homography,laser_pos)

        window_frame = np.zeros((720, 1280, 3))
        pos = (int(checker_x*window_frame.shape[1]), int(checker_y*window_frame.shape[0]))

        cv.drawMarker(window_frame, pos, (0, 0.4, 0), markerSize=100, thickness=4)
        cv.circle(window_frame, pos, 100, (0,0.4,0), 4)

        cv.drawMarker(cam_frame, laser_pos, (0, 0.3, 0))

        cv2.imshow(WINDOW_NAME, window_frame)
        cv2.imshow("cam", cam_frame)
        k = cv2.waitKey(1)
        if k == 27:
            quit()



# display a checkerboard to screen
# open camera and look at checkerboard
# find the homography matrix
# track features
# reproject features

