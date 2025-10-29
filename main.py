import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import cv2
import math
import time
from modules.hand_detector import HandDetector
from modules.shape_utils import ShapeManager
from modules.shape_3d import Shape3D


def is_pinch(hand):
    """Check if thumb and index are close enough to be a pinch."""
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
    shape3d = Shape3D("cube", 120)

    window_name = "VisionTouch - 2D + 3D Sandbox"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    pinch_cooldown = 0
    draw_cooldown_start = None
    draw_cooldown_duration = 3  # seconds

    # Zoom & rotation states
    zoom_active = False
    zoom_start_dist = None
    zoom_shape = None
    original_size = None
    start_angle_z = 0

    mode_3d = True  # Toggle between 2D and 3D modes

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        img = detector.find_hands(frame, draw=False)
        hands = detector.find_positions(img, draw=False)

        # Fix mirrored hand labels
        for h in hands:
            h["label"] = "Right" if h["label"] == "Left" else "Left"

        current_time = time.time()

        # --- DRAWING MODE COUNTDOWN ---
        if draw_cooldown_start:
            elapsed = current_time - draw_cooldown_start
            if elapsed < draw_cooldown_duration:
                remaining = int(draw_cooldown_duration - elapsed + 1)
                cv2.putText(img, f"🖊️ Drawing starts in {remaining}s", (420, 360),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
            else:
                shapes.drawing = True
                shapes.current_draw = {"type": "draw", "points": [], "color": shapes._random_color()}
                draw_cooldown_start = None

        # --- HAND DETECTION ---
        left_hand = next((h for h in hands if h["label"] == "Left"), None)
        right_hand = next((h for h in hands if h["label"] == "Right"), None)

        left_pinch, left_center = is_pinch(left_hand) if left_hand else (False, None)
        right_pinch, right_center = is_pinch(right_hand) if right_hand else (False, None)

        # --- 3D ZOOM + ROTATION CONTROL ---
        if mode_3d and left_pinch and right_pinch:
            cv2.line(img, left_center, right_center, (255, 255, 0), 3)
            dist_now = distance(left_center, right_center)
            dx = left_center[0] - right_center[0]
            dy = left_center[1] - right_center[1]
            angle_z = math.degrees(math.atan2(dy, dx))

            if not zoom_active:
                zoom_active = True
                zoom_start_dist = dist_now
                start_angle_z = angle_z
                original_size = shape3d.size
            else:
                # Zoom (scale)
                scale = dist_now / zoom_start_dist
                shape3d.size = int(max(50, min(original_size * scale, 400)))

                # Rotation (horizontal twist)
                d_angle = angle_z - start_angle_z
                shape3d.rotate(0, d_angle * 0.5, 0)
                cv2.putText(img, f"3D Scale: {int(scale*100)}% | Rot: {int(d_angle)}°",
                            (40, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
        else:
            zoom_active = False
            zoom_start_dist = None
            original_size = None

        # --- 2D MODE CONTROLS ---
        if not mode_3d:
            for label, hand in [("left", left_hand), ("right", right_hand)]:
                if not hand:
                    setattr(shapes, f"selected_{label}", None)
                    continue

                pinch, center = is_pinch(hand)
                if pinch:
                    cv2.circle(img, center, 12, (0, 255, 255), -1)

                    # Drawing mode
                    if shapes.drawing:
                        shapes.current_draw["points"].append(center)
                        continue

                    # Button click (Add, Draw, etc.)
                    if pinch_cooldown <= 0 and not draw_cooldown_start:
                        clicked = shapes.check_button_click(*center)
                        if clicked:
                            if clicked == "draw":
                                draw_cooldown_start = time.time()
                            else:
                                shapes.add_shape(clicked)
                            pinch_cooldown = 25

                    # Move selected shape
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
                    if shapes.drawing:
                        shapes.finish_draw()
                    setattr(shapes, f"selected_{label}", None)
                    setattr(shapes, f"last_{label}_pos", None)

        # --- DRAW EVERYTHING ---
        if not mode_3d:
            img = shapes.draw_ui(img)
            cv2.putText(img, "🟢 2D Mode | Pinch: Add / Move / Draw / Delete | Esc to Quit",
                        (40, 700), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        else:
            img = shape3d.draw(img)
            cv2.putText(img, "🔵 3D Mode | Two-Hand Pinch: Scale + Rotate | Press 'T' to Toggle 2D/3D | Esc to Quit",
                        (40, 700), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow(window_name, img)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == ord('t'):
            mode_3d = not mode_3d  # toggle mode

        pinch_cooldown = max(0, pinch_cooldown - 1)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
