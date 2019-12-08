import math as m

import cv2 as cv
import numpy as np

import bird_eye
import jetson_nano_move as jm
from connected_component import search_lane_center


def is_white(color_code: int) -> bool:
    return color_code == 255


def finish_program(video_capture: cv.VideoCapture) -> None:
    video_capture.release()
    cv.destroyAllWindows()


def steer_dampener(val: float) -> float:  # high val = left.
    const = 0.8
    return (2 * jm.MAX_STEER_DEV / m.pi) * m.atan(val * const) + jm.STRAIGHT_ANGLE


def set_angle_from(centers_up: list, centers_low: list) -> float:
    car_len = 18  # cm
    if len(centers_up) != 2 or len(centers_low) != 2:
        r = prev_turn
        if r == 0:
            r = 0.01 ** 4
        jm.set_angle(steer_dampener(180 / m.pi * m.atan(car_len / r)))
        return prev_turn

    left_coord = centers_up[0]
    right_coord = centers_up[1]

    const = 63000

    if 640 - left_coord[0] - right_coord[0] == 0:
        r = m.inf
    else:
        r = const / (640 - left_coord[0] - right_coord[0])

    print(r)
    jm.set_angle(steer_dampener(180 / m.pi * m.atan(car_len / r)))

    return r


def debug_img_show(image_in):
    if debug:
        cv.imshow('debug', image_in)
        cv.waitKey(1000)


debug = True

# camera init
img = jm.cap
prev_turn = m.inf

while True:
    _, image_raw = img.read()
    image_raw = cv.resize(image_raw, (640, 360), interpolation=cv.INTER_AREA)
    debug_img_show(image_raw)

    image_bird = bird_eye.bird_eye_warp(image_raw)
    debug_img_show(image_bird)

    list_up, up_image = search_lane_center(image_bird[:image_bird.shape[0] // 2, :])
    list_low, low_image = search_lane_center(image_bird[image_bird.shape[0] // 2:, :])
    image_res_merge = np.concatenate((up_image, low_image), axis=0)
    debug_img_show(image_res_merge)

    if debug:
        for a in list_up:
            cv.circle(image_bird, (a[0], a[1]), 10, (63, 63, 63), 3)
        for a in list_low:
            cv.circle(image_bird, (a[0], a[1] + image_bird.shape[0] // 2), 10, (63, 63, 63), 3)
    debug_img_show(image_bird)

    if cv.waitKey(30) > 0:
        break

    prev_turn = set_angle_from(list_up, list_low)

    if debug:
        continue

    jm.set_throttle(0.15)

finish_program(img)
