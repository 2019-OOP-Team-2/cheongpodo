import math as m

import cv2 as cv

import jetson_nano_move as jm


def is_white(color_code: int) -> bool:
    return color_code == 255


def white_dispersion_average(image_input) -> (float, float):  # TODO: make this faster
    height_input, width_input = image_input.shape
    right_average = 0
    left_average = 0
    for i in range(height_input // 2, height_input):
        right_dispersion = width_input // 2
        left_dispersion = width_input // 2
        for j in range(width_input // 2, -1, -1):
            if is_white(image_input[i][j]):
                left_dispersion = 1 - j / (width_input // 2)
                break
        for j in range(width_input // 2, width_input):
            if is_white(image_input[i][j]):
                right_dispersion = j / (width_input // 2) - 1
                break
        right_average += right_dispersion
        left_average += left_dispersion
    left_average /= width_input / 2
    right_average /= width_input / 2
    return left_average, right_average


def finish_program(video_capture: cv.VideoCapture) -> None:
    video_capture.release()
    cv.destroyAllWindows()


def steer_dampener(val: float) -> float:
    return (2 * jm.MAX_STEER_DEV / m.pi) * m.atan(val) + jm.STRAIGHT_ANGLE


def set_angle_from(left: float, right: float) -> None:
    c1 = 1
    c2 = 10
    val = c1 * (m.e ** (c2 * left) - m.e ** (c2 * right))
    print(left, right, val)
    jm.set_angle(steer_dampener(val))


# camera init
img = jm.cap

while True:
    _, image_raw = img.read()
    # image_binary = cv.cvtColor(image_raw, cv.COLOR_BGR2GRAY)
    _, image_binary = cv.threshold(image_raw, 190, 255, cv.THRESH_BINARY)
    image_binary = cv.adaptiveThreshold(image_binary, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 15, 20)
    image_binary = cv.morphologyEx(image_binary, cv.MORPH_CLOSE, cv.getStructuringElement(cv.MORPH_ELLIPSE, (3, 3)))

    cv.imshow("VideoFrame", image_raw)
    cv.imshow("Binary", image_binary)
    if cv.waitKey(30) > 0:
        break

    height, width = image_binary.shape
    left_average_result, right_average_result = white_dispersion_average(
        cv.resize(image_binary, None, fx=0.5, fy=0.5, interpolation=cv.INTER_AREA))
    set_angle_from(left_average_result, right_average_result)
    jm.set_throttle(0.15)

finish_program(img)
