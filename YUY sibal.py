import math as m

import cv2 as cv
import jetson_nano_move as jm
import numpy as np


# import modules


def is_white(color_code):
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


# initial condition
img = jm.cap
img.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
img.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

while True:
    # read image
    ret, frame = img.read()
    cv.imshow("VideoFrame", frame)
    if cv.waitKey(1) > 0:
        break
    # 일정 크기 이상 밝기 -> 255로 일정하게
    _, thr = cv.threshold(frame, 240, 255, cv.THRESH_BINARY)

    # color -> gray
    thr = cv.cvtColor(thr, cv.COLOR_BGR2GRAY)

    # erosion, dilation
    kernel = np.ones((10, 10), np.uint8)
    thr = cv.erode(thr, kernel, iterations=1)
    thr = cv.dilate(thr, kernel, iterations=1)

    # show image
    cv.imshow('Binary', thr)

    # setup values
    height, width = thr.shape
    Lave, Rave = white_dispersion_average(thr, height, width)

    # case 1
    ratio = Rave / Lave
    ratio = m.log2(ratio)
    if ratio > 0:
        print(ratio, min(120.0, 90.0 + ratio * 20.0), 0.2 - m.fabs(ratio / 100))
        jm.set_angle(min(120.0, 90.0 + ratio * 20.0))
    else:
        print(ratio, max(60.0, 90.0 + ratio * 20.0), 0.2 - m.fabs(ratio / 100))
        jm.set_angle(max(60.0, 90.0 + ratio * 20.0))
    jm.set_throttle(0.3 - m.fabs(ratio / 100))

    # case 2
    # ratio = Rave - Lave
    # print(ratio)

    # case 3
    # ratio (already defined)
    # if ratio>0: 90+alpha
    # else: 90-alpha

    # case 4

    # default : 양수 -> 오른쪽, 음수 -> 왼쪽, ratio = 0 -> 90도

# img = cv.imread('sample1.jpg', cv.IMREAD_GRAYSCALE)
# cv.imshow('xxx', img) // 담 작성 - 샘플 이미지 입출력 코드

cv.waitKey(0)

finish_program(img)
