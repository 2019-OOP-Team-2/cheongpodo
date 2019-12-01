import math as m

import cv2 as cv
import jetson_nano_move as jm
import numpy as np


##import modules

def check_location(thr, height, width):
    Rave = 0
    Lave = 0
    for i in range(height//2, height):
        Ridx = int(width)
        Lidx = int(0)
        # range -> white check
        for j in range(width // 2, 0, -1):
            if thr[i][j] == 255:
                Lidx = j
                break
        for j in range(width // 2, width, 1):
            if thr[i][j] == 255:
                Ridx = j
                break
        Lidx = float(width // 2 - Lidx)
        Ridx = float(Ridx - width // 2)
        Rave += Ridx
        Lave += Lidx
    return Lave, Rave

# initial condition
img = jm.cap
# img = cv.VideoCapture(0)
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
    Lave, Rave = check_location(thr, height, width)

    # case 1
    ratio = Rave / Lave
    ratio = m.log2(ratio)
    if ratio>0:
        print(ratio, min(120.0, 90.0 + ratio * 20.0), 0.2 - m.fabs(ratio / 100))
        jm.set_angle(min(120.0, 90.0 + ratio * 20.0))
    else:
        print(ratio, max(60.0, 90.0 + ratio * 20.0), 0.2 - m.fabs(ratio / 100))
        jm.set_angle(max(60.0, 90.0 + ratio * 20.0))
    jm.set_throttle(0.3-m.fabs(ratio/100))

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

img.release()

cv.destroyAllWindows()
