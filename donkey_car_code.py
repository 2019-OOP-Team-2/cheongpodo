import math as m
import time

import cv2 as cv
import numpy as np

import bird_eye
import jetson_nano_move as jm
from connected_component import search_lane_center


def is_white(color_code: int) -> bool:
    return color_code == 255


def finish_program(video_capture: cv.VideoCapture) -> None:
    video_capture.release()
    jm.set_throttle(0)
    cv.destroyAllWindows()


def steer_dampener(val: float) -> float:  # high val = left.
    const = 0.8  # const
    return (2 * jm.MAX_STEER_DEV / m.pi) * m.atan(val * const) + jm.STRAIGHT_ANGLE


def set_angle_from(centers_up: list, centers_low: list) -> float:
    car_len = 18  # cm
    if len(centers_up) != 2:
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


debug = True
jm.set_throttle(0)
time.sleep(1)
# camera init
img = jm.cap
prev_turn = m.inf

try:
    while True:
        _, image_raw = img.read()
        image_raw = cv.resize(image_raw, (640, 360), interpolation=cv.INTER_AREA)

        image_bird = bird_eye.bird_eye_warp(image_raw)

        list_up_left, up_left_image = \
            search_lane_center(image_bird[:image_bird.shape[0] // 2, :image_bird.shape[1] // 2], 1)
        list_up_right, up_right_image = \
            search_lane_center(image_bird[:image_bird.shape[0] // 2, image_bird.shape[1] // 2:], 1)
        if len(list_up_right):
            list_up_right[0][0] += image_bird.shape[1] // 2
        list_up = list_up_left + list_up_right
        up_image = np.concatenate((up_left_image, up_right_image), axis=1)

        list_low_left, low_image_left = \
            search_lane_center(image_bird[image_bird.shape[0] // 2:, :image_bird.shape[1] // 2], 1)
        list_low_right, low_image_right = \
            search_lane_center(image_bird[image_bird.shape[0] // 2:, image_bird.shape[1] // 2:], 1)
        if len(list_low_right):
            list_low_right[0][0] += image_bird.shape[1] // 2
        list_low = list_low_left + list_low_right
        low_image = np.concatenate((low_image_left, low_image_right), axis=1)

        image_res_merge = np.concatenate((up_image, low_image), axis=0)

        if debug:
            for a in list_up:
                cv.circle(image_res_merge, (a[0], a[1]), 10, (63, 63, 63), 3)
            for a in list_low:
                cv.circle(image_res_merge, (a[0], a[1] + image_bird.shape[0] // 2), 10, (63, 63, 63), 3)

        debug_img_show(image_res_merge)

        if cv.waitKey(30) > 0:
            break

        prev_turn = set_angle_from(list_up, list_low)

        if debug:
            continue

        jm.set_throttle(0.14)
except KeyboardInterrupt:
    print('ctrl + C trapped')

finish_program(img)
