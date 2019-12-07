import math as m

import cv2 as cv

import jetson_nano_move as jm


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


def erode_dilate(threshold_input, kernel_input):
    threshold_input = cv.erode(threshold_input, kernel_input, iterations=1)
    threshold_input = cv.dilate(threshold_input, kernel_input, iterations=1)
    return threshold_input


def set_angle_from(ratio_input):
    ANGLE_STRAIGHT = 90
    ANGLE_RANGE = 40
    ANGLE_MAX = ANGLE_STRAIGHT + ANGLE_RANGE
    ANGLE_MIN = ANGLE_STRAIGHT - ANGLE_RANGE
    RATIO_MODIFIER = 20

    angle_destination = min(ANGLE_MAX, 90.0 + ratio_input * RATIO_MODIFIER) if ratio_input > 0 \
        else max(ANGLE_MIN, 90.0 + ratio_input * RATIO_MODIFIER)
    print(ratio_input, angle_destination, 0.2 - abs(ratio_input / 100))
    jm.set_angle(angle_destination)


# initial condition
img = setup_camera()

while True:
    ret, image_raw = img.read()

    image_binary = cv.cvtColor(image_raw, cv.COLOR_BGR2GRAY)
    # _, thr = cv.threshold(thr, 190, 255, cv.THRESH_BINARY)
    image_binary = cv.adaptiveThreshold(image_binary, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 15, 20)
    image_binary = cv.morphologyEx(image_binary, cv.MORPH_CLOSE, cv.getStructuringElement(cv.MORPH_ELLIPSE, (3, 3)))

    cv.imshow("VideoFrame", image_raw)
    cv.imshow('Binary', image_binary)
    if cv.waitKey(30) > 0:
        break

    height, width = image_binary.shape
    left_average_result, right_average_result = white_dispersion_average(image_binary, height, width)

    ratio = m.log2(right_average_result / left_average_result)
    set_angle_from(ratio)
    jm.set_throttle(0.3 - abs(ratio / 100))

cv.waitKey(0)
finish_program(img)
