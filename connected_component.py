import cv2
import numpy as np


def search_lane_center(image):
    image = image[image.shape[0] // 2:, :]  # bottom half
    b, g, r = cv2.split(cv2.GaussianBlur(image, (5, 5), 0))
    _, edge = cv2.threshold(cv2.bitwise_and(cv2.bitwise_and(b, g), r), 217, 255, cv2.THRESH_BINARY)
    edge = cv2.morphologyEx(edge, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(edge)
    # Map component labels to hue val
    label_hue = np.uint8(179 * labels / np.max(labels))
    blank_ch = 255 * np.ones_like(label_hue)
    labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])
    # cvt to BGR for display
    labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)
    # set bg label to black
    labeled_img[label_hue == 0] = 0
    center_list = []
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        center_point = centroids[i].astype(int)
        center_coord = [center_point[0], center_point[1], area]
        center_list.append(center_coord)
    center_list.sort(key=lambda e: -e[2])
    center_list = center_list[:2]
    center_list.sort(key=lambda e: e[0])
    return center_list
