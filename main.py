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
    drawer = AirDrawer(1280, 720)

    window_name = "VisionTouch - Smart Gestures"
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    mode = "MOVE"
    draw_mode_start_time = 0
    can_draw = False

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        img = detector.find_hands(img)
        all_hands = detector.find_positions(img, draw=False)

        right_hand = None
        left_hand = None

        # Separate hands by side
        for hand in all_hands:
            cx = hand[0][1]
            if cx < 640:
                left_hand = hand
            else:
                right_hand = hand

        # --- CLEAR GESTURE: both index fingers close together ---
        if left_hand and right_hand:
            lx, ly = left_hand[8][1], left_hand[8][2]
            rx, ry = right_hand[8][1], right_hand[8][2]
            dist_lr = math.hypot(rx - lx, ry - ly)

            if dist_lr < 100:
                drawer.clear()
                cv2.putText(img, "🧼 Cleared!", (500, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)
                time.sleep(0.5)

        # --- LEFT HAND = ERASER ---
        if left_hand:
            fingers_left = detector.fingers_up(left_hand)
            lx, ly = left_hand[8][1], left_hand[8][2]
            if fingers_left[1] == 1 and sum(fingers_left) == 1:  # Only index up
                mode = "ERASE"
                img = drawer.draw(img, lx, ly, mode)
                cv2.circle(img, (lx, ly), 25, (0, 0, 255), 2)

        # --- RIGHT HAND = DRAW / MOVE ---
        if right_hand:
            fingers_right = detector.fingers_up(right_hand)
            x1, y1 = right_hand[8][1], right_hand[8][2]
            x2, y2 = right_hand[4][1], right_hand[4][2]
            dist = math.hypot(x2 - x1, y2 - y1)

            new_mode = "MOVE"

            if fingers_right[1] == 1 and fingers_right[2] == 0:
                new_mode = "DRAW"
            elif fingers_right[1] == 1 and fingers_right[2] == 1 and dist < 40:
                new_mode = "MOVE"
            elif sum(fingers_right) == 5:
                new_mode = "MOVE"

            # Detect mode change
            if new_mode != mode:
                mode = new_mode
                can_draw = False
                if mode == "DRAW":
                    draw_mode_start_time = time.time()

            # Handle draw delay
            if mode == "DRAW":
                elapsed = time.time() - draw_mode_start_time
                if elapsed >= 2.0:
                    can_draw = True
                    img = drawer.draw(img, x1, y1, mode)
                else:
                    cv2.putText(img, "⏳ Hold steady... starting draw", (420, 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
            elif mode == "MOVE":
                img = drawer.draw(img, x1, y1, mode)

            cv2.circle(img, (x1, y1), 8, (255, 255, 0), -1)
            cv2.putText(img, f"Mode: {mode}", (50, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)

        cv2.imshow(window_name, img)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
