import numpy as np
import cv2 as cv
import math as m
import time
import jetson_nano_move as jm
##import modules

# initial condition
img = jm.cap
# img = cv.VideoCapture(0)
img.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
img.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
# lol
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
    Rave = 0
    Lave = 0
    Ltemp = 0
    Rtemp = 0
    temp = 0

    # until (2/3, 1)
    for i in range(2 * height // 3, height):
        Ridx = int(width)
        Lidx = int(0)
        # range -> white check
        for j in range(width // 2, 0, -1):
            if thr[i][j] == 255:
                Lidx = j
                temp = 1
                break
        if temp == 1:
            Ltemp = 1
        temp = 0
        for j in range(width // 2, width, 1):
            if thr[i][j] == 255:
                Ridx = j
                temp = 1
                break
        if temp == 1:
            Rtemp = 1
        temp = 0
        Lidx = float(width // 2 - Lidx)
        Ridx = float(Ridx - width // 2)
        Rave += Ridx
        Lave += Lidx
        # x = Lidx / Ridx
        # print(i, Lidx, Ridx, x)
    # 만약 검출되지 않았다면 break -> 종료
    # Ltemp, Rtemp -> 한번이라도 흰색이 검출되면 1, 한번도 검출이 안되면 0, temp -> 각각의 줄에서 흰색이 검출되면 1, 검출이 되지 않으면 0
    if Ltemp == 0 or Rtemp == 0:
        jm.set_angle(90)
        jm.set_throttle(0)
        break

    #case 1
    ratio = Rave / Lave
    print(ratio)
    ratio = m.log2(ratio)
    jm.set_angle(90+ratio*2.5)
    jm.set_throttle(0.3-m.fabs(ratio/100))

    # 시간 delay (0.1초단위)
    time.sleep(0.1)

    #case 2
    #ratio = Rave - Lave
    #print(ratio)

    #case 3
    #ratio (already defined)
    #if ratio>0: 90+alpha
    #else: 90-alpha

    #case 4


    # default : 양수 -> 오른쪽, 음수 -> 왼쪽, ratio = 0 -> 90도


# img = cv.imread('sample1.jpg', cv.IMREAD_GRAYSCALE)
# cv.imshow('xxx', img) // 담 작성 - 샘플 이미지 입출력 코드

cv.waitKey(0)

img.release()

cv.destroyAllWindows()
