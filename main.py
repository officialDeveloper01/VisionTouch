import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import cv2
import math
import time
from modules.hand_detector import HandDetector
from modules.shape_utils import ShapeManager
from modules.shape_3d import Shape3DManager
from modules.ui_buttons import UIButtonManager


def is_pinch(hand):
    """Return (isPinching, centerPoint)."""
    x1, y1 = hand["landmarks"][8][1], hand["landmarks"][8][2]
    x2, y2 = hand["landmarks"][4][1], hand["landmarks"][4][2]
    dist = math.hypot(x2 - x1, y2 - y1)
    return dist < 40, (int((x1 + x2) // 2), int((y1 + y2) // 2))


def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    detector = HandDetector(detection_conf=0.7, track_conf=0.7)
    shape2d = ShapeManager(1280, 720)
    shape3d = Shape3DManager()
    ui = UIButtonManager()

    window_name = "VisionTouch - Shape Sandbox"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    mode_3d = False
    pinch_cooldown = 0
    active_draw_cooldown = None
    cooldown_time = 3

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        img = detector.find_hands(frame, draw=False)
        hands = detector.find_positions(img, draw=False)

        # Fix mirrored labels
        for h in hands:
            h["label"] = "Right" if h["label"] == "Left" else "Left"

        current_time = time.time()

        # Handle drawing cooldown
        if active_draw_cooldown:
            elapsed = current_time - active_draw_cooldown
            if elapsed < cooldown_time:
                rem = int(cooldown_time - elapsed + 1)
                cv2.putText(img, f"🖊️ Drawing starts in {rem}s", (420, 360),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
            else:
                shape2d.drawing = True
                shape2d.current_draw = {"type": "draw", "points": [], "color": shape2d._random_color()}
                active_draw_cooldown = None

        # Draw all UI buttons
        ui.draw_buttons(img, mode_3d)

        for label, hand in [("left", next((h for h in hands if h["label"] == "Left"), None)),
                            ("right", next((h for h in hands if h["label"] == "Right"), None))]:

            if not hand:
                setattr(shape2d, f"selected_{label}", None)
                continue

            pinch, center = is_pinch(hand)
            if pinch:
                cv2.circle(img, center, 12, (0, 255, 255), -1)

                # =========================
                # Mode: 2D
                # =========================
                if not mode_3d:

                    # Drawing
                    if shape2d.drawing:
                        shape2d.current_draw["points"].append(center)
                        continue

                    # Button click
                    if pinch_cooldown <= 0 and not active_draw_cooldown:
                        clicked = ui.check_button_click(*center)
                        if clicked == "toggle_mode":
                            mode_3d = not mode_3d
                            pinch_cooldown = 25
                        elif clicked == "draw":
                            active_draw_cooldown = time.time()
                            pinch_cooldown = 25
                        elif clicked:
                            shape2d.add_shape(clicked)
                            pinch_cooldown = 25

                    # Move shapes
                    selected = getattr(shape2d, f"selected_{label}")
                    last_pos = getattr(shape2d, f"last_{label}_pos")
                    if selected is None:
                        shape = shape2d.select_shape(*center)
                        if shape:
                            setattr(shape2d, f"selected_{label}", shape)
                            setattr(shape2d, f"last_{label}_pos", center)
                    else:
                        new_pos = shape2d.move_shape(selected, *center, last_pos)
                        setattr(shape2d, f"last_{label}_pos", new_pos)
                        if shape2d.remove_shape_if_in_bin(selected):
                            setattr(shape2d, f"selected_{label}", None)

                # =========================
                # Mode: 3D
                # =========================
                else:
                    if pinch_cooldown <= 0:
                        clicked = ui.check_button_click(*center)
                        if clicked == "toggle_mode":
                            mode_3d = not mode_3d
                            pinch_cooldown = 25
                        elif clicked:
                            shape3d.set_active_shape(clicked)
                            pinch_cooldown = 25

                    shape3d.handle_pinch(center, label)

            else:
                if shape2d.drawing:
                    shape2d.finish_draw()

                setattr(shape2d, f"selected_{label}", None)
                setattr(shape2d, f"last_{label}_pos", None)
                shape3d.handle_release(label)

        pinch_cooldown = max(0, pinch_cooldown - 1)

        # Render appropriate view
        if not mode_3d:
            img = shape2d.draw_ui(img)
        else:
            img = shape3d.render_preview(img)

        cv2.putText(img, "Pinch to Add / Move / Draw / Delete | Toggle 2D/3D with button", (40, 700),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow(window_name, img)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
