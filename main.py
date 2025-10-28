import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import cv2
import math
import time
from modules.hand_detector import HandDetector
from modules.cube_utils import CubeManager

def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    detector = HandDetector(detection_conf=0.7, track_conf=0.7)
    cubes = CubeManager(1280, 720, num_cubes=5)

    window_name = "VisionTouch - Virtual Cubes"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    grabbed = False

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        img = frame.copy()

        img = detector.find_hands(img, draw=False)
        hands = detector.find_positions(img, draw=False)

        right_hand = next((h for h in hands if h["label"] == "Right"), None)

        if right_hand:
            # Get index and thumb tips
            x1, y1 = right_hand["landmarks"][8][1], right_hand["landmarks"][8][2]
            x2, y2 = right_hand["landmarks"][4][1], right_hand["landmarks"][4][2]

            dist = math.hypot(x2 - x1, y2 - y1)
            center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2

            # Pinch detected
            if dist < 40:
                cv2.circle(img, (center_x, center_y), 12, (0, 255, 255), -1)

                if not grabbed:
                    cube = cubes.select_cube(center_x, center_y)
                    grabbed = cube is not None
                else:
                    cubes.move_selected_cube(center_x, center_y)
            else:
                if grabbed:
                    cubes.release_cube()
                    grabbed = False
        else:
            if grabbed:
                cubes.release_cube()
                grabbed = False

        img = cubes.draw_cubes(img)

        cv2.putText(img, "🤏 Pinch to grab and move cubes", (40, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow(window_name, img)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
