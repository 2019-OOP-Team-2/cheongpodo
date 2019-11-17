import cv2


def main():
    img = cv2.imread('wooki.jpg', cv2.IMREAD_COLOR)  # 이미지 불러오기
    canny_img = cv2.Canny(img, 50, 150)
    blur_img = cv2.GaussianBlur(img, (3, 3), 0)
    cv2.imshow('canny', canny_img)
    cv2.imshow('gaussian_blur', blur_img)
    k = cv2.waitKey(0)  # 키보드 눌림 대기
    cv2.destroyAllWindows()
