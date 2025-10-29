import cv2
import mediapipe as mp
import math
from modules.hand_detector import HandDetector
from modules.shape_utils import ShapeManager

# --- Setup ---
width, height = 1280, 720
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

detector = HandDetector(detectionCon=0.8)
shape_manager = ShapeManager(width, height)

mode = "UI"  # Toggle between UI and drawing
rotate_mode = False  # Active when both hands are detected for rotation
last_angle = None


# --- Helper functions ---
def calculate_angle(p1, p2, center):
    """Return angle (in degrees) between two points relative to a center."""
    ang1 = math.degrees(math.atan2(p1[1] - center[1], p1[0] - center[0]))
    ang2 = math.degrees(math.atan2(p2[1] - center[1], p2[0] - center[0]))
    return ang2 - ang1


def draw_text(frame, text, pos, color=(255, 255, 255)):
    cv2.putText(frame, text, pos, cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)


# --- Main Loop ---
while True:
    success, frame = cap.read()
    frame = cv2.flip(frame, 1)

    hands, frame = detector.findHands(frame)

    if hands:
        # Left & right hand distinction
        hand1 = hands[0]
        lmList1 = hand1["lmList"]
        bbox1 = hand1["bbox"]
        center1 = hand1["center"]
        fingers1 = detector.fingersUp(hand1)

        hand2 = hands[1] if len(hands) == 2 else None
        center2 = hand2["center"] if hand2 else None

        # Left hand index tip
        x1, y1 = lmList1[8][0:2]

        # --- Shape interaction ---
        if fingers1 == [0, 1, 0, 0, 0]:  # Only index finger up
            if mode == "UI":
                btn_type = shape_manager.check_button_click(x1, y1)
                if btn_type:
                    shape_manager.add_shape(btn_type)

                # Select or move shape
                if not shape_manager.selected_left:
                    shape_manager.selected_left = shape_manager.select_shape(x1, y1)
                else:
                    shape_manager.last_left_pos = shape_manager.move_shape(
                        shape_manager.selected_left, x1, y1, shape_manager.last_left_pos
                    )

            elif mode == "DRAW" and shape_manager.drawing and shape_manager.current_draw:
                shape_manager.current_draw["points"].append((x1, y1))

        # --- Finish drawing on pinch (thumb + index) ---
        if fingers1 == [1, 1, 0, 0, 0] and shape_manager.drawing:
            shape_manager.finish_draw()

        # --- Two-hand interaction for rotation ---
        if hand2:
            fingers2 = detector.fingersUp(hand2)
            if fingers1 == [0, 1, 0, 0, 0] and fingers2 == [0, 1, 0, 0, 0]:
                # Both index fingers up → rotate mode
                rotate_mode = True

                if shape_manager.selected_left:
                    shape = shape_manager.selected_left

                    # Compute relative angle between two hands
                    angle_now = math.degrees(
                        math.atan2(center2[1] - center1[1], center2[0] - center1[0])
                    )

                    if last_angle is None:
                        last_angle = angle_now
                    else:
                        delta = angle_now - last_angle
                        if abs(delta) > 2:
                            shape_manager.rotate_shape(shape, delta)
                        last_angle = angle_now
            else:
                rotate_mode = False
                last_angle = None
        else:
            rotate_mode = False
            last_angle = None

        # --- Deselect if pinch together over bin ---
        if shape_manager.selected_left:
            if shape_manager.remove_shape_if_in_bin(shape_manager.selected_left):
                shape_manager.selected_left = None
                shape_manager.last_left_pos = None
        else:
            shape_manager.selected_left = None
            shape_manager.last_left_pos = None
            rotate_mode = False
            last_angle = None

    # --- Draw all UI and shapes ---
    frame = shape_manager.draw_ui(frame)

    # --- Info text ---
    draw_text(frame, "Mode: " + mode, (60, 650))
    if rotate_mode:
        draw_text(frame, "Rotate Mode Active", (60, 690), (0, 255, 0))

    cv2.imshow("Gesture Drawing", frame)

    # --- Keyboard controls ---
    key = cv2.waitKey(1)
    if key == ord("t"):
        mode = "DRAW" if mode == "UI" else "UI"
    elif key == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()
