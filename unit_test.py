if __name__ == '__main__':
    import cv2

    import bird_eye
    import connected_component

    a = cv2.imread('lane.jpeg')
    a = cv2.resize(a, (640, 360), interpolation=cv2.INTER_AREA)

    a = bird_eye.bird_eye_warp(a)
    cv2.imshow('a', a)
    cv2.waitKey(0)
    b, _ = connected_component.search_lane_center(a[:a.shape[0] // 2, :])
    cv2.imshow('_', _)
    for q in b:
        cv2.circle(a, (q[0], q[1]), 10, (0, 0, 0), 3)
    b, _ = connected_component.search_lane_center(a[a.shape[0] // 2:, :])
    cv2.imshow('_2', _)
    for q in b:
        cv2.circle(a, (q[0], q[1] + a.shape[0] // 2), 10, (0, 0, 0), 3)

    cv2.imshow('a', a)
    cv2.waitKey(0)
