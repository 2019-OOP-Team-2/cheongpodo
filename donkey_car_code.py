import math as m

import cv2 as cv

import jetson_nano_move as jm
from connected_component import search_lane_center


def is_white(color_code: int) -> bool:
    return color_code == 255


def finish_program(video_capture: cv.VideoCapture) -> None:
    video_capture.release()
    cv.destroyAllWindows()


def steer_dampener(val: float) -> float:  # high val = left.
    const = 1
    return (2 * jm.MAX_STEER_DEV / m.pi) * m.atan(val * const) + jm.STRAIGHT_ANGLE


def set_angle_from(centers: list) -> float:
    car_len = 18  # cm
    if len(centers) != 2:
        r = prev_turn
        if r == 0:
            r = 0.01 ** 4
        jm.set_angle(steer_dampener(180 / m.pi * m.atan(car_len / r)))
        return prev_turn

    left_coord = centers[0]
    right_coord = centers[1]

    const = 63000

    if 640 - left_coord[0] - right_coord[0] == 0:
        r = m.inf
    else:
        r = const / (640 - left_coord[0] - right_coord[0])
    print(r)
    jm.set_angle(steer_dampener(180 / m.pi * m.atan(car_len / r)))

    return r


debug = False

# camera init
img = jm.cap
prev_turn = m.inf

while True:
    _, image_raw = img.read()
    image_raw = cv.resize(image_raw, (640, 360), interpolation=cv.INTER_AREA)
    image_search = image_raw.copy()
    center_list, image_res = search_lane_center(image_search[image_search.shape[0] // 2:, :])
    for a in center_list:
        cv.circle(image_res, (a[0], a[1]), 10, (0, 0, 0), 3)
    if debug:
        cv.imshow("Searched", image_res)

    if cv.waitKey(30) > 0:
        break

    prev_turn = set_angle_from(center_list)
    if debug:
        continue
    jm.set_throttle(0.15)

finish_program(img)
