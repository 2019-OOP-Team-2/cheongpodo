# -*- coding: utf-8 -*-
import cv2
import numpy as np

image = cv2.imread("lane.jpeg", cv2.IMREAD_COLOR)
blurred = cv2.GaussianBlur(image, (5, 5), 0)
gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
_, edge = cv2.threshold(gray, 252, 255, cv2.THRESH_BINARY)
edge = cv2.morphologyEx(edge, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))


nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(edge)

# Map component labels to hue val
label_hue = np.uint8(179 * labels / np.max(labels))
blank_ch = 255 * np.ones_like(label_hue)
labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])

# cvt to BGR for display
labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)

# set bg label to black
labeled_img[label_hue == 0] = 0
cv2.imshow("result", labeled_img)
cv2.waitKey(0)

for i in range(nlabels):
    if i < 2:
        continue
    area = stats[i, cv2.CC_STAT_AREA]
    center_x = int(centroids[i ,0])
    center_y = int(centroids[i ,1])
    left = stats[i, cv2.CC_STAT_LEFT]
    top = stats[i, cv2.CC_STAT_TOP]
    width = stats[i, cv2.CC_STAT_WIDTH]
    height = stats[i, cv2.CC_STAT_HEIGHT]

    if area > 10000:
        cv2.circle(labeled_img, (center_x, center_y), 5, (255, 255, 255), 1)

cv2.imshow("result", labeled_img)
cv2.waitKey(0)
