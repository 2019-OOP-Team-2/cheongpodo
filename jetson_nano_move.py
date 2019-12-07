import cv2
from adafruit_servokit import ServoKit


def gstreamer_pipeline(
        capture_width=1280,
        capture_height=720,
        display_width=1280,
        display_height=720,
        framerate=60,
        flip_method=0,
):
    return (
            "nvarguscamerasrc ! "
            "video/x-raw(memory:NVMM), "
            "width=(int)%d, height=(int)%d, "
            "format=(string)NV12, framerate=(fraction)%d/1 ! "
            "nvvidconv flip-method=%d ! "
            "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
            "videoconvert ! "
            "video/x-raw, format=(string)BGR ! appsink"
            % (
                capture_width,
                capture_height,
                framerate,
                flip_method,
                display_width,
                display_height,
            )
    )


def set_throttle(val: float) -> None:
    if val < MIN_THROTTLE_VAL or val > MAX_THROTTLE_VAL:
        raise ValueError('throttle must be a number of [%.1f, %.1f] !' % (MIN_THROTTLE_VAL, MAX_THROTTLE_VAL))
    __servo_kit.continuous_servo[0].throttle = val


def get_throttle() -> float:
    return __servo_kit.continuous_servo[0].throttle


def set_angle(val: float) -> None:
    MIN_VAL = STRAIGHT_ANGLE - MAX_STEER_DEV
    MAX_VAL = STRAIGHT_ANGLE + MAX_STEER_DEV
    if val < MIN_VAL or val > MAX_VAL:
        raise ValueError('angle must be a number of [%.1f, %.1f] !' % (MIN_VAL, MAX_VAL))
    __servo_kit.servo[1].angle = val


def get_angle() -> float:
    return __servo_kit.servo[1].angle


MIN_THROTTLE_VAL = 0.0
MAX_THROTTLE_VAL = 1.0
STRAIGHT_ANGLE = 90.0
MAX_STEER_DEV = 40.0

cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)

__servo_kit = ServoKit(channels=16)
