# NOTE: Please create virtual environment variable in your VS code (.venv). Then install the following libraries



# pip install opencv-contrib-python (for camera)
# pip install cvzone (for hand tracking) also install this pip install mediapipe
# pip install pyautogui (To interact with mouse)

import cv2
import pyautogui
import numpy as np
from cvzone.HandTrackingModule import HandDetector


detector = HandDetector(detectionCon=0.9, maxHands=1)

cap = cv2.VideoCapture(0)
cam_w, cam_h = 640, 480

cap.set(3, cam_w)
cap.set(4, cam_h)

frame_R = 100


while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    hands, img = detector.findHands(img, flipType=False)
    cv2.rectangle(img,(frame_R,frame_R), (cam_w-frame_R, cam_h-frame_R), (255,0,255),2)
    if hands:
        # landmark = lm
        lmList = hands[0]['lmList']
        ind_x, ind_y = lmList[8][0], lmList[8][1]
        mid_x, mid_y = lmList[12][0], lmList[12][1]
        # draw a circle on index finger
        cv2.circle(img, (ind_x, ind_y), 5, (0,255,255), 2)

        fingers = detector.fingersUp(hands[0])
        print(fingers)

        # Move mouse

        if fingers[1] == 1 and fingers[2] == 0 and fingers[0] == 1:
            conv_x = int(np.interp(ind_x, (frame_R,cam_w-frame_R),(0,1439)))
            conv_y = int(np.interp(ind_y, (frame_R,cam_h-frame_R),(0,899)))
            pyautogui.moveTo(conv_x, conv_y)

        # Mouse click events

        if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 1:
            if abs(ind_x-mid_x) < 25: 

                if fingers[4] == 0:
                    pyautogui.leftClick()
                    pyautogui.sleep(1)
                    print("Left")

                if fingers[4] == 1:
                    pyautogui.rightClick()
                    pyautogui.sleep(1)
                    print("Right")

        # Mouse scrolling

        # Negative number indicates scrolling down
        # Positive number indicates scrolling up

        if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0 and fingers[4] == 0:
             if abs(ind_x-mid_x) < 25:
                 pyautogui.scroll(-1)
                 print("down")

        if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0 and fingers[4] == 1:
             if abs(ind_x-mid_x) < 25:
                 pyautogui.scroll(1)
                 print("UP")


        
    cv2.imshow("Camera Feed", img)
    cv2.waitKey(1)



    