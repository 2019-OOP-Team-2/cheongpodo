import math as m

import cv2 as cv

import jetson_nano_move as jm
from connected_component import search_lane_center


def is_white(color_code: int) -> bool:
    return color_code == 255


def white_dispersion_average(image_input) -> (float, float):
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


def steer_dampener(val: float) -> float:  # high val = left.
    return (2 * jm.MAX_STEER_DEV / m.pi) * m.atan(val) + jm.STRAIGHT_ANGLE


def set_angle_from(centers: list) -> None:
    left_coord = tuple(centers[0, :2])
    right_coord = tuple(centers[1, :2])


# camera init
img = jm.cap

while True:
    _, image_raw = img.read()
    image_raw = cv.resize(image_raw, (640, 360), interpolation=cv.INTER_AREA)
    image_search = image_raw.clone()
    center_list = search_lane_center(image_search)
    for a in center_list:
        cv.circle(image_search, (a[0], a[1]), 5, (255, 255, 255), 1)
    cv.imshow("Searched", image_search)

    if cv.waitKey(30) > 0:
        break

    set_angle_from(center_list)
    jm.set_throttle(0.15)

finish_program(img)
