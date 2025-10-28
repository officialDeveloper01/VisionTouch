import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import cv2
import math
import time
from modules.hand_detector import HandDetector
from modules.shape_utils import ShapeManager

def is_pinch(hand):
    x1, y1 = hand["landmarks"][8][1], hand["landmarks"][8][2]
    x2, y2 = hand["landmarks"][4][1], hand["landmarks"][4][2]
    dist = math.hypot(x2 - x1, y2 - y1)
    return dist < 40, (int((x1 + x2) // 2), int((y1 + y2) // 2))

def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    detector = HandDetector(detection_conf=0.7, track_conf=0.7)
    shapes = ShapeManager(1280, 720)

    window_name = "VisionTouch - Shape Sandbox"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    pinch_cooldown = 0
    draw_cooldown_start = None
    draw_cooldown_duration = 3  # seconds

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        img = detector.find_hands(frame, draw=False)
        hands = detector.find_positions(img, draw=False)

        # Fix mirroring issue
        for h in hands:
            h["label"] = "Right" if h["label"] == "Left" else "Left"

        current_time = time.time()

        # Handle draw cooldown countdown
        if draw_cooldown_start:
            elapsed = current_time - draw_cooldown_start
            if elapsed < draw_cooldown_duration:
                remaining = int(draw_cooldown_duration - elapsed + 1)
                cv2.putText(img, f"🖊️ Drawing starts in {remaining}s", (420, 360),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
            else:
                # Start drawing after cooldown completes
                shapes.drawing = True
                shapes.current_draw = {"type": "draw", "points": [], "color": shapes._random_color()}
                draw_cooldown_start = None

        for label, hand in [("left", next((h for h in hands if h["label"] == "Left"), None)),
                            ("right", next((h for h in hands if h["label"] == "Right"), None))]:
            if not hand:
                setattr(shapes, f"selected_{label}", None)
                continue

            pinch, center = is_pinch(hand)
            if pinch:
                cv2.circle(img, center, 12, (0, 255, 255), -1)

                # Drawing mode active
                if shapes.drawing:
                    shapes.current_draw["points"].append(center)
                    continue

                # Button click
                if pinch_cooldown <= 0 and not draw_cooldown_start:
                    clicked = shapes.check_button_click(*center)
                    if clicked:
                        if clicked == "draw":
                            draw_cooldown_start = time.time()  # start 3s countdown
                        else:
                            shapes.add_shape(clicked)
                        pinch_cooldown = 25

                # Move shapes
                selected = getattr(shapes, f"selected_{label}")
                last_pos = getattr(shapes, f"last_{label}_pos")
                if selected is None:
                    shape = shapes.select_shape(*center)
                    if shape:
                        setattr(shapes, f"selected_{label}", shape)
                        setattr(shapes, f"last_{label}_pos", center)
                else:
                    new_pos = shapes.move_shape(selected, *center, last_pos)
                    setattr(shapes, f"last_{label}_pos", new_pos)
                    if shapes.remove_shape_if_in_bin(selected):
                        setattr(shapes, f"selected_{label}", None)
            else:
                # If drawing and pinch released → finish
                if shapes.drawing:
                    shapes.finish_draw()
                setattr(shapes, f"selected_{label}", None)
                setattr(shapes, f"last_{label}_pos", None)

        pinch_cooldown = max(0, pinch_cooldown - 1)

        img = shapes.draw_ui(img)
        cv2.putText(img, "Pinch to Add / Move / Draw / Delete", (40, 700),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow(window_name, img)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
