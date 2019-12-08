import cv2
import numpy as np


def bird_eye_warp(img):
    height, width = img.shape[:2]

    dispersion_from_center = 1.9  # higher val makes a whole image narrower width
    angle_mod = 0.6  # higher val makes upper wider

    # ========== do not modify below ========== #
    angle_mod *= width / 1280
    cam_height = 0.80692 * height
    height_const = 250 * dispersion_from_center * width / 1280
    angle_const = cam_height * 2 / width + angle_mod * dispersion_from_center
    # ========== do not modify above ========== #

    p1 = [(1 - dispersion_from_center) * width / 2, height]
    p2 = [(1 + dispersion_from_center) * width / 2, height]
    p3 = [(1 + dispersion_from_center) * width / 2 - angle_const * height_const, height - height_const / angle_const]
    p4 = [(1 - dispersion_from_center) * width / 2 + angle_const * height_const, height - height_const / angle_const]
    pts1 = np.float32([p1, p2, p3, p4])
    pts2 = np.float32([[0, height], [width, height], [width, 0], [0, 0]])
    m = cv2.getPerspectiveTransform(pts1, pts2)
    return cv2.warpPerspective(img, m, (width, height))
