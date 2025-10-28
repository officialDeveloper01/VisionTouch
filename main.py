import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import cv2
import math
import time
from modules.hand_detector import HandDetector
from modules.virtual_mouse import VirtualMouse

# Load custom cursor image
cursor_img = cv2.imread("assets/cursor.png", cv2.IMREAD_UNCHANGED)

def overlay_cursor(frame, cursor, x, y):
    """Overlay the cursor image on frame at (x, y) safely within bounds."""
    if cursor is None:
        return frame

    h, w = cursor.shape[:2]
    y1, y2 = y - h // 2, y + h // 2
    x1, x2 = x - w // 2, x + w // 2

    # Clip overlay area to frame boundaries
    y1_clipped, y2_clipped = max(0, y1), min(frame.shape[0], y2)
    x1_clipped, x2_clipped = max(0, x1), min(frame.shape[1], x2)

    # Compute cropping ranges for cursor image
    cursor_y1 = y1_clipped - y1
    cursor_y2 = h - (y2 - y2_clipped)
    cursor_x1 = x1_clipped - x1
    cursor_x2 = w - (x2 - x2_clipped)

    # Final overlay if both have valid area
    if cursor_y2 > cursor_y1 and cursor_x2 > cursor_x1:
        alpha = cursor[cursor_y1:cursor_y2, cursor_x1:cursor_x2, 3] / 255.0
        for c in range(3):
            frame[y1_clipped:y2_clipped, x1_clipped:x2_clipped, c] = (
                (1 - alpha) * frame[y1_clipped:y2_clipped, x1_clipped:x2_clipped, c]
                + alpha * cursor[cursor_y1:cursor_y2, cursor_x1:cursor_x2, c]
            )

    return frame



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

            # Check for click
            dist = math.hypot(x2 - x1, y2 - y1)
            clicked = mouse.click_if_pinch(dist)

            # Click feedback circle
            if clicked:
                click_feedback = True
                click_start = time.time()

            if click_feedback:
                if time.time() - click_start < 0.2:  # visible for 200ms
                    cv2.circle(img, (x1, y1), 20, (0, 0, 255), 3)
                else:
                    click_feedback = False

            # Overlay the custom cursor
            img = overlay_cursor(img, cursor_img, x1, y1)

        cv2.imshow(window_name, img)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
