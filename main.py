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

    window_name = "VisionTouch - Fixed Right-Hand"
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    mode = "MOVE"
    draw_mode_start_time = 0
    can_draw = False
    moving_canvas = False

    # safety inits
    new_mode = mode
    mode_switch_time = time.time()
    last_right_pos = None
    last_right_time = 0
    last_left_pos = None
    last_left_time = 0

    while True:
        success, frame = cap.read()   # raw frame (not flipped)
        if not success:
            break

        h, w = frame.shape[:2]

        # --- Process on raw frame so Mediapipe handedness is correct ---
        detector.find_hands(frame, draw=False)
        hands = detector.find_positions(frame, draw=False)

        # --- Create display image by flipping (so user sees mirror) ---
        img = cv2.flip(frame, 1)  # this is what we will show
        # When mapping coordinates computed on `frame` to `img` (flipped), do:
        # display_x = w - raw_x

        current_time = time.time()

        # find right/left by label from detector (labels correspond to raw frame)
        right_hand = next((h for h in hands if h["label"] == "Right"), None)
        left_hand = next((h for h in hands if h["label"] == "Left"), None)

        # --- CLEAR GESTURE (both index tips close) ---
        if left_hand and right_hand:
            lx_raw, ly_raw = left_hand["landmarks"][8][1], left_hand["landmarks"][8][2]
            rx_raw, ry_raw = right_hand["landmarks"][8][1], right_hand["landmarks"][8][2]
            if math.hypot(rx_raw - lx_raw, ry_raw - ly_raw) < 100:
                drawer.clear()
                cv2.putText(img, "🧼 Cleared!", (500, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)
                time.sleep(0.25)

        # --- LEFT HAND (eraser). Map raw -> display coords for overlay and ERASER usage ---
        if left_hand:
            fingers_left = detector.fingers_up(left_hand)
            lx_raw, ly_raw = left_hand["landmarks"][8][1], left_hand["landmarks"][8][2]
            # map to display coordinates (mirror)
            lx, ly = w - lx_raw, ly_raw
            last_left_pos = (lx, ly)
            last_left_time = current_time

            # Erase if only index up
            if fingers_left[1] == 1 and sum(fingers_left) == 1:
                img = drawer.draw(img, lx, ly, "ERASE")
                cv2.circle(img, (lx, ly), 25, (0, 0, 255), 2)
            else:
                # pinch with left raw coords?
                thumb_x_raw, thumb_y_raw = left_hand["landmarks"][4][1], left_hand["landmarks"][4][2]
                if math.hypot(lx_raw - thumb_x_raw, ly_raw - thumb_y_raw) < 40:
                    img = drawer.draw(img, lx, ly, "MOVE")
        else:
            if last_left_pos and (current_time - last_left_time) < 0.2:
                lx, ly = last_left_pos
                img = drawer.draw(img, lx, ly, "ERASE")

        # --- RIGHT HAND (DRAW / MOVE_CANVAS). Similar mapping raw->display ---
        if right_hand:
            fingers_right = detector.fingers_up(right_hand)
            rx_raw, ry_raw = right_hand["landmarks"][8][1], right_hand["landmarks"][8][2]
            thumb_x_raw, thumb_y_raw = right_hand["landmarks"][4][1], right_hand["landmarks"][4][2]
            # map to display coords
            x1, y1 = w - rx_raw, ry_raw
            x2, y2 = w - thumb_x_raw, thumb_y_raw

            last_right_pos = (x1, y1)
            last_right_time = current_time

            dist = math.hypot((thumb_x_raw - rx_raw), (thumb_y_raw - ry_raw))  # use raw distance for pinch

            is_index_up = (fingers_right[1] == 1 and sum(fingers_right) == 1)
            is_pinch = dist < 40

            new_mode = mode
            if is_pinch:
                new_mode = "MOVE_CANVAS"
            elif is_index_up:
                new_mode = "DRAW"
            else:
                new_mode = "MOVE"

            # Switch mode with a small debounce
            if new_mode != mode and (current_time - mode_switch_time) > 0.25:
                mode = new_mode
                mode_switch_time = current_time
                if mode == "DRAW":
                    draw_mode_start_time = current_time
                    can_draw = False

            # DRAW mode (with a short stabilization delay)
            if mode == "DRAW":
                if not can_draw and (current_time - draw_mode_start_time) > 1.0:
                    can_draw = True
                if can_draw:
                    img = drawer.draw(img, x1, y1, "DRAW")
                    cv2.circle(img, (x1, y1), 6, (0, 255, 255), -1)
                else:
                    cv2.putText(img, "⏳ Hold steady...", (420, 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            elif mode == "MOVE_CANVAS" and is_pinch:
                img = drawer.draw(img, x1, y1, "MOVE")
                cv2.circle(img, (x1, y1), 6, (255, 255, 0), -1)

            cv2.putText(img, f"Mode: {mode}", (50, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2)

        else:
            # If right hand briefly disappears, persist last point
            if last_right_pos and (current_time - last_right_time) < 0.2:
                x1, y1 = last_right_pos
                img = drawer.draw(img, x1, y1, "DRAW")

        # Always overlay the canvas for display
        img = drawer.overlay_on_frame(img)
        cv2.imshow(window_name, img)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
