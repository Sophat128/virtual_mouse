from flask import Flask, render_template, Response, request
import cv2
import pyautogui
import numpy as np
from cvzone.HandTrackingModule import HandDetector

app = Flask(__name__)

# Initialize the hand detector
detector = HandDetector(detectionCon=0.9, maxHands=1)
cap = None
cam_w, cam_h = 640, 480
frame_R = 100

def generate_frames():
    global cap
    while cap.isOpened():
        success, img = cap.read()
        if not success:
            break
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, flipType=False)
        cv2.rectangle(img, (frame_R, frame_R), (cam_w - frame_R, cam_h - frame_R), (255, 0, 255), 2)

        if hands:
            lmList = hands[0]['lmList']
            ind_x, ind_y = lmList[8][0], lmList[8][1]
            mid_x, mid_y = lmList[12][0], lmList[12][1]
            cv2.circle(img, (ind_x, ind_y), 5, (0, 255, 255), 2)
            fingers = detector.fingersUp(hands[0])

            # Move mouse
            if fingers[1] == 1 and fingers[2] == 0 and fingers[0] == 1:
                conv_x = int(np.interp(ind_x, (frame_R, cam_w - frame_R), (0, 1439)))
                conv_y = int(np.interp(ind_y, (frame_R, cam_h - frame_R), (0, 899)))
                pyautogui.moveTo(conv_x, conv_y)

            # Mouse click events
            if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 1:
                if abs(ind_x - mid_x) < 25:
                    if fingers[4] == 0:
                        pyautogui.leftClick()
                        pyautogui.sleep(1)
                    if fingers[4] == 1:
                        pyautogui.rightClick()
                        pyautogui.sleep(1)

            # Mouse scrolling
            if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0 and fingers[4] == 0:
                if abs(ind_x - mid_x) < 25:
                    pyautogui.scroll(-1)

            if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0 and fingers[4] == 1:
                if abs(ind_x - mid_x) < 25:
                    pyautogui.scroll(1)

        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start')
def start():
    global cap
    webcam_index = int(request.args.get('webcam', 0))
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(webcam_index)
        cap.set(3, cam_w)
        cap.set(4, cam_h)
    return '', 204

@app.route('/stop')
def stop():
    global cap
    if cap is not None and cap.isOpened():
        cap.release()
    return '', 204

if __name__ == "__main__":
    app.run(debug=True)
