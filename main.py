import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import cv2
import math
from modules.hand_detector import HandDetector
from modules.virtual_mouse import VirtualMouse

def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    detector = HandDetector(detection_conf=0.7, track_conf=0.7)
    mouse = VirtualMouse(smoothening=4)

    window_name = "VisionTouch - Virtual Mouse"
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        img = detector.find_hands(img)
        all_hands = detector.find_positions(img, draw=True)

        if all_hands:
            hand = all_hands[0]  # track only the first detected hand
            h, w, _ = img.shape

            # Get coordinates of index tip (8) and thumb tip (4)
            x1, y1 = hand[8][1], hand[8][2]
            x2, y2 = hand[4][1], hand[4][2]

            # Move cursor based on index finger
            mouse.move_cursor(x1, y1, w, h)

            # Draw visual line between thumb and index
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 2)

            # Calculate distance for pinch detection
            dist = math.hypot(x2 - x1, y2 - y1)

            # Click if pinch detected
            mouse.click_if_pinch(dist)

            # Show distance on screen
            cv2.putText(img, f"Dist: {int(dist)}", (x1 - 50, y1 - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        cv2.imshow(window_name, img)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
