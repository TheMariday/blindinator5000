import cv2
import numpy as np
import cv2 as cv
import sdl2.ext

WINDOW_NAME = "main"
CALIB_FILE = "resources/checker.png"
CALIB_COLS = 13
CALIB_ROWS = 6

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720


def cam_to_projector(homo, point):
    point_homogeneous = np.array([point[0], point[1], 1.0]).reshape((3, 1))
    mapped_point = np.dot(homo, point_homogeneous)

    # This is based off of the relationship between the checkerboard and the
    # full screen size. Don't worry about it
    cx = 1 - (mapped_point[0] / mapped_point[2] + 2) / (CALIB_COLS + 3)
    cy = 1 - (mapped_point[1] / mapped_point[2] + 2) / (CALIB_ROWS + 3)

    return cx, cy


def find_homography(cam, renderer):

    checkerboard_img = sdl2.ext.load_img(CALIB_FILE)
    checkerboard_texture = sdl2.ext.Texture(renderer, checkerboard_img)

    renderer.clear()
    renderer.copy(checkerboard_texture, dstrect=(0, 0, 1280, 720))
    renderer.present()

    checkerboard_model = np.zeros((CALIB_COLS * CALIB_ROWS, 3), np.float32)
    checkerboard_model[:, :2] = np.mgrid[0:CALIB_COLS, 0:CALIB_ROWS].T.reshape(-1, 2)

    homography = None
    while True:

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
        key = cv.waitKey(1)

        if key == 27:
            quit()
        if key == 13:
            return homography


def find_laser(img):
    red_blur = cv.blur(img[:, :, 2], [5, 5])
    _, _, _, max_location = cv.minMaxLoc(red_blur)
    return max_location


if __name__ == "__main__":

    sdl2.ext.init()

    cam = cv.VideoCapture(0, cv2.CAP_DSHOW)

    window = sdl2.ext.Window(WINDOW_NAME, size=(SCREEN_WIDTH, SCREEN_HEIGHT))
    window.show()

    renderer = sdl2.ext.Renderer(
        window, flags=sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC
    )

    homography = find_homography(cam, renderer)

    target_img = sdl2.ext.load_img("resources/target.jpg")
    target_texture = sdl2.ext.Texture(renderer, target_img)

    #sdl2.SDL_SetTextureAlphaMod(target_texture, 128)


    while True:
        _, cam_frame = cam.read()
        camera_x, camera_y = find_laser(cam_frame)

        projector_x, projector_y = cam_to_projector(homography, (camera_x, camera_y))

        screen_x = int(projector_x * SCREEN_WIDTH)
        screen_y = int(projector_y * SCREEN_HEIGHT)

        renderer.clear()
        renderer.copy(target_texture, dstrect=(screen_x-50, screen_y-50, 100, 100))
        renderer.present()

        #cv.drawMarker(cam_frame, (camera_x, camera_y), (0, 0.3, 0))

        #cv2.imshow("cam", cam_frame)
        #k = cv2.waitKey(1)
        #if k == 27:
        #    quit()
