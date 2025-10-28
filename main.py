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

    window_name = "VisionTouch - Fixed Draw Mode"
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    mode = "MOVE"
    draw_mode_start_time = 0
    can_draw = False
    moving_canvas = False

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        img = detector.find_hands(img)
        hands = detector.find_positions(img, draw=False)

        # Persist drawing when no hands are detected
        if not hands:
            img = drawer.overlay_on_frame(img)
            cv2.imshow(window_name, img)
            if cv2.waitKey(1) & 0xFF == 27:
                break
            continue

        right_hand = next((h for h in hands if h["label"] == "Right"), None)
        left_hand = next((h for h in hands if h["label"] == "Left"), None)

        # --- CLEAR GESTURE: both index fingers close ---
        if left_hand and right_hand:
            lx, ly = left_hand["landmarks"][8][1], left_hand["landmarks"][8][2]
            rx, ry = right_hand["landmarks"][8][1], right_hand["landmarks"][8][2]
            dist_lr = math.hypot(rx - lx, ry - ly)
            if dist_lr < 100:
                drawer.clear()
                cv2.putText(img, "🧼 Cleared!", (500, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)
                time.sleep(0.5)

        # --- LEFT HAND = ERASER ---
        if left_hand:
            fingers_left = detector.fingers_up(left_hand)
            lx, ly = left_hand["landmarks"][8][1], left_hand["landmarks"][8][2]
            if fingers_left[1] == 1 and sum(fingers_left) == 1:
                img = drawer.draw(img, lx, ly, "ERASE")
                cv2.circle(img, (lx, ly), 25, (0, 0, 255), 2)

        # --- RIGHT HAND = DRAW / MOVE / MOVE_CANVAS ---
        if right_hand:
            fingers_right = detector.fingers_up(right_hand)
            x1, y1 = right_hand["landmarks"][8][1], right_hand["landmarks"][8][2]
            x2, y2 = right_hand["landmarks"][4][1], right_hand["landmarks"][4][2]
            dist = math.hypot(x2 - x1, y2 - y1)

            # Detect gestures
            is_index_up = fingers_right[1] == 1 and sum(fingers_right) == 1
            is_pinch = dist < 40

            new_mode = mode
            if is_pinch:
                new_mode = "MOVE_CANVAS"
            elif is_index_up:
                new_mode = "DRAW"
            else:
                new_mode = "MOVE"

            # Handle mode transitions
            if new_mode != mode:
                mode = new_mode
                can_draw = False
                moving_canvas = False
                if mode == "DRAW":
                    draw_mode_start_time = time.time()

            # --- DRAW MODE ---
            if mode == "DRAW":
                elapsed = time.time() - draw_mode_start_time
                if elapsed >= 2.0:
                    can_draw = True
                    img = drawer.draw(img, x1, y1, "DRAW")
                else:
                    cv2.putText(img, "⏳ Hold steady... preparing to draw",
                                (400, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

            # --- MOVE CANVAS ---
            elif mode == "MOVE_CANVAS" and is_pinch:
                moving_canvas = True
                img = drawer.draw(img, x1, y1, "MOVE")
            else:
                moving_canvas = False
                drawer.prev_x, drawer.prev_y = 0, 0

            cv2.circle(img, (x1, y1), 8, (255, 255, 0), -1)
            cv2.putText(img, f"Mode: {mode}", (50, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)

        # Always overlay current canvas
        img = drawer.overlay_on_frame(img)
        cv2.imshow(window_name, img)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
