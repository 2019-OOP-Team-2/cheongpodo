# -*- coding: utf-8 -*-
import cv2
import numpy as np


def roi(img, vertices):
    #blank mask:
    mask = np.zeros_like(img)
    # fill the mask
    cv2.fillPoly(mask, vertices, 255)
    # now only show the area that is the mask
    masked = cv2.bitwise_and(img, mask)
    return masked

def process_img(original_image):
    resized_image = cv2.resize(original_image, dsize=(600, 800))
    hsv = cv2.cvtColor(resized_image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    vertices = np.array([[0, 800], [50, 150], [300, 80], [550, 150], [600, 800],
                         ], np.int32) # 좌표는 나중에 ^-^
    processed_img = roi(h, [vertices])
    return processed_img



img = cv2.imread('lane.jpeg', cv2.IMREAD_COLOR) # 이미지 불러오기
new_img = process_img(img)
cv2.imshow("new_img", new_img)
k = cv2.waitKey(0)  # 키보드 눌림 대기
cv2.destroyAllWindows()


