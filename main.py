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


def distance(p1, p2):
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


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

    # Zoom state
    zoom_active = False
    zoom_start_dist = None
    zoom_shape = None
    original_size = None

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

        # Detect left and right hand
        left_hand = next((h for h in hands if h["label"] == "Left"), None)
        right_hand = next((h for h in hands if h["label"] == "Right"), None)

        # Detect pinch for each hand
        left_pinch, left_center = is_pinch(left_hand) if left_hand else (False, None)
        right_pinch, right_center = is_pinch(right_hand) if right_hand else (False, None)

        # -------------------------
        # ✅ FIXED ZOOM BEHAVIOUR
        # -------------------------
        # Two-hand pinch only triggers zoom if both hands are pinching *the same shape*
        if left_pinch and right_pinch:
            shape_left = shapes.selected_left
            shape_right = shapes.selected_right

            if shape_left is not None and shape_left is shape_right:
                # Zoom on the same shape
                cv2.line(img, left_center, right_center, (255, 255, 0), 3)
                dist_now = distance(left_center, right_center)

                if not zoom_active:
                    zoom_active = True
                    zoom_start_dist = dist_now
                    zoom_shape = shape_left
                    if zoom_shape:
                        original_size = zoom_shape["size"]
                else:
                    if zoom_shape:
                        scale = dist_now / zoom_start_dist
                        new_size = int(original_size * scale)
                        zoom_shape["size"] = max(30, min(new_size, 400))  # clamp
                        cv2.putText(img, f"Zoom: {int(scale * 100)}%", (40, 120),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
            else:
                # If both hands are pinching different shapes → move independently
                zoom_active = False
                zoom_shape = None
                zoom_start_dist = None
        else:
            zoom_active = False
            zoom_start_dist = None
            zoom_shape = None
            original_size = None

        # --- NORMAL INTERACTIONS --- #
        for label, hand in [("left", left_hand), ("right", right_hand)]:
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
        cv2.putText(img, "Pinch to Add / Move / Draw / Delete | Two-Hand Pinch = Resize", (40, 700),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow(window_name, img)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()