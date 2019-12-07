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


def set_throttle(val):
    if val < 0 or val > 1:
        raise ValueError('throttle must be a number of [0,1] !')
    __servo_kit.continuous_servo[0].throttle = val


def get_throttle():
    return __servo_kit.continuous_servo[0].throttle


def set_angle(val):
    if val < 50 or val > 130:
        raise ValueError('angle must be a number of [50,130] !')
    __servo_kit.servo[1].angle = val


def get_angle():
    return __servo_kit.servo[1].angle


cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)

__servo_kit = ServoKit(channels=16)
