import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import cv2
import math
import time
from modules.hand_detector import HandDetector
from modules.virtual_mouse import VirtualMouse

def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    detector = HandDetector(detection_conf=0.7, track_conf=0.7)
    mouse = VirtualMouse(smoothening=3)

    window_name = "VisionTouch - Virtual Mouse"
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    click_feedback = False
    click_start = 0
    click_x, click_y = 0, 0

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        img = detector.find_hands(img)
        all_hands = detector.find_positions(img, draw=False)

        if all_hands:
            hand = all_hands[0]
            h, w, _ = img.shape
            x1, y1 = hand[8][1], hand[8][2]  # index tip
            x2, y2 = hand[4][1], hand[4][2]  # thumb tip

            # Move cursor
            cursor_x, cursor_y = mouse.move_cursor(x1, y1, w, h)

            # Distance between thumb and index for pinch
            dist = math.hypot(x2 - x1, y2 - y1)
            clicked = mouse.click_if_pinch(dist)

            # Click feedback animation
            if clicked:
                click_feedback = True
                click_start = time.time()
                click_x, click_y = x1, y1

            # Draw feedback circle (pulse for ~200ms)
            if click_feedback:
                elapsed = time.time() - click_start
                if elapsed < 0.25:
                    radius = int(25 + 30 * math.sin(elapsed * 10))  # pulsing effect
                    cv2.circle(img, (click_x, click_y), radius, (0, 0, 255), 2)
                else:
                    click_feedback = False

            # Optional visual: small dot at fingertip for clarity
            cv2.circle(img, (x1, y1), 10, (255, 255, 0), cv2.FILLED)

        cv2.imshow(window_name, img)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
