import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import cv2
import math
import time
from modules.hand_detector import HandDetector
from modules.draw_utils import AirDrawer

def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    detector = HandDetector(detection_conf=0.7, track_conf=0.7)

    window_name = "VisionTouch - Air Drawing"
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    drawer = AirDrawer(1280, 720)
    mode = "MOVE"

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        img = detector.find_hands(img)
        all_hands = detector.find_positions(img, draw=False)

        if all_hands:
            hand = all_hands[0]
            fingers = detector.fingers_up(hand)

            x1, y1 = hand[8][1], hand[8][2]  # Index tip
            x2, y2 = hand[12][1], hand[12][2]  # Middle tip

            # Determine mode
            if fingers[1] == 1 and fingers[2] == 0:
                mode = "DRAW"
            elif fingers[1] == 1 and fingers[2] == 1:
                mode = "MOVE"
            elif sum(fingers) == 5:
                drawer.clear()
                mode = "CLEAR"

            # Draw or move
            draw_mode = (mode == "DRAW")
            img = drawer.draw(img, x1, y1, draw_mode)

            # Display mode
            cv2.putText(img, f"Mode: {mode}", (50, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)
            cv2.circle(img, (x1, y1), 10, (255, 255, 0), cv2.FILLED)

        cv2.imshow(window_name, img)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
