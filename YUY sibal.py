import math as m

import cv2 as cv
import jetson_nano_move as jm
import numpy as np


#
# import modules


def is_white(color_code: int):
    return color_code == 255


def white_dispersion_average(image_input, height_input, width_input):
    if type(height_input) is not int or type(width_input) is not int:
        raise TypeError('height_input and width_input must be an int!')
    right_average = 0
    left_average = 0
    for i in range(height_input // 2, height_input):
        right_dispersion = width_input // 2
        left_dispersion = width_input // 2
        # range -> white check
        for j in range(width_input // 2, -1, -1):
            if is_white(image_input[i][j]):
                left_dispersion = width_input // 2 - j
                break
        for j in range(width_input // 2, width_input):
            if is_white(image_input[i][j]):
                right_dispersion = j - width_input // 2
                break
        right_average += right_dispersion
        left_average += left_dispersion
    return left_average, right_average


def finish_program(video_capture):
    video_capture.release()
    cv.destroyAllWindows()


def setup_camera():
    image = jm.cap
    image.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
    image.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
    return image


# initial condition
img = setup_camera()


def erode_dilate(threshold, kernel_input):
    threshold = cv.erode(threshold, kernel_input, iterations=1)
    threshold = cv.dilate(threshold, kernel_input, iterations=1)
    return threshold


def set_angle_from(ratio_input):
    ANGLE_MAX = 130
    ANGLE_MIN = 50
    RATIO_MODIFIER = 20

    if ratio_input > 0:
        angle_destination = min(ANGLE_MAX, 90.0 + ratio_input * RATIO_MODIFIER)
        print(ratio_input, angle_destination, 0.2 - abs(ratio_input / 100))
        jm.set_angle(angle_destination)
    else:
        angle_destination = max(ANGLE_MIN, 90.0 + ratio_input * RATIO_MODIFIER)
        print(ratio_input, angle_destination, 0.2 - abs(ratio_input / 100))
        jm.set_angle(angle_destination)


while True:
    ret, frame = img.read()

    if cv.waitKey(1) > 0:
        break

    cv.imshow("VideoFrame", frame)

    _, thr = cv.threshold(frame, 240, 255, cv.THRESH_BINARY)
    thr = cv.cvtColor(thr, cv.COLOR_BGR2GRAY)
    kernel = np.ones((10, 10), np.uint8)
    thr = erode_dilate(thr, kernel)

    cv.imshow('Binary', thr)

    height, width = thr.shape
    left_average_result, right_average_result = white_dispersion_average(thr, height, width)

    ratio = m.log2(right_average_result / left_average_result)
    set_angle_from(ratio)
    jm.set_throttle(0.3 - abs(ratio / 100))

cv.waitKey(0)
finish_program(img)
