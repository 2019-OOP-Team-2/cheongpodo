import  numpy as np  #numpy를 불러옴
import cv2 #openCV를 불러옴
import glob #glob를 불러옴 glob는 파일을 경로에 맞게 불어올 때 사용한다

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
#코너별로 요소들의 좌표를 저장하는 곳 (0,0,0), (1,0,0), ....,(4,4,0)
objp = np.zeros((5*5,3), np.float32) #체스보드에 대해 처리한 정보를 저장하는 곳
objp[:,:2] = np.mgrid[0:5,0:5].T.reshape(-1,2) #행렬뻥튀기->transpose->행렬재설정

objpoints = [] #3d사진(찍힌 사진)의 코너위치를 저장하는 곳
imgpoints = [] #2d실제 사진의 코너위치를 저장하는 곳

images = glob.glob('./*.jpg') #체스판을 찍은 이미지를 받아온다.

for filename in images:
    img = cv2.imread(filename) #사진파일을 읽어와서 저장한다
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) #사진파일을 흑백으로 변환하는 함수

  #체스보드의 코너들을 찾는다.
    ret, corners = cv2.findChessboardCorners(gray, (5,5), None)

    #코너를 찾았다면 objpoint와 imgpoint에 추가한다.
    if ret == True:
        objpoints.append(objp) #코너를 찾은 경우 해당하는 값을 넣는다

        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2) #흑백으로 변환한 값을 넣는다

        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, (5, 5), corners2, ret)
        cv2.imshow('img', img) #코너가 체크된 이미지 파일을 보여준다
        cv2.waitKey(500) #키보드 입력을 대기
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None) #결과값들을 알맞은 변수(카메라매트릭스, 왜곡 계수 등)에 저장한다.
cv2.destroyAllWindows()#모든 창 닫기

img = cv2.imread('./chessimg12.jpg') #실제로 찍은 이미지들 중 하나를 가져온다.
h,  w = img.shape[:2]
newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h)) #가져온 이미지 파일을 통해 카메라 매트릭스를 개선하여 저장한다. 이때 매개변수 중 1이 의미하는 바는 모든 픽셀을 유지한다 것이다.왜곡을 개선하는데 사용할 수 있는 이미지를 roi에 저장
#undistort함수를 통해서 왜곡을 제거한다. 이때 매개변수들의 연산을 통해 얻은 것(개선된 카메라 매트릭스, 왜곡 계수 등)을 집어 넣는다.
dst = cv2.undistort(img, mtx, dist, None, newcameramtx) #왜곡이 개선된 이미지는 dst에 저장
x, y, w, h = roi
dst = dst[y:y + h, x:x + w]
cv2.imwrite('oop2_calibration.png', dst) #결과 이미지를 저장한다
