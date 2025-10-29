# modules/hand_detector.py
import cv2
import mediapipe as mp


class HandDetector:
    def __init__(self, detection_conf=0.7, track_conf=0.7, max_hands=2, **kwargs):
        # Backward compatibility: accept old parameter names if passed
        if "detectionCon" in kwargs:
            detection_conf = kwargs["detectionCon"]
        if "trackCon" in kwargs:
            track_conf = kwargs["trackCon"]
        if "maxHands" in kwargs:
            max_hands = kwargs["maxHands"]

        self.detection_conf = detection_conf
        self.track_conf = track_conf
        self.max_hands = max_hands

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_conf,
            min_tracking_confidence=self.track_conf,
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None


    def find_hands(self, img, draw=True):
        """
        Detect hands in a BGR image. Call this once per frame.
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        if draw and self.results and self.results.multi_hand_landmarks:
            for hand_lms, hand_type in zip(
                self.results.multi_hand_landmarks, self.results.multi_handedness
            ):
                self.mp_draw.draw_landmarks(
                    img, hand_lms, self.mp_hands.HAND_CONNECTIONS
                )

                # Draw label ("Left" / "Right")
                label = hand_type.classification[0].label
                h, w, _ = img.shape
                cx, cy = int(hand_lms.landmark[0].x * w), int(hand_lms.landmark[0].y * h)
                cv2.putText(
                    img,
                    label,
                    (cx - 30, cy + 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )
        return img

    def find_positions(self, img, draw=False):
        """
        Returns list of hands; each hand is dict:
            {
                "label": "Right"/"Left",
                "landmarks": [ (id, x, y), ... ],
                "center": (cx, cy)
            }
        """
        all_hands = []
        if not self.results or not self.results.multi_hand_landmarks:
            return all_hands

        for hand_idx, hand_lms in enumerate(self.results.multi_hand_landmarks):
            h, w, _ = img.shape
            lm_list = []
            for id, lm in enumerate(hand_lms.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((id, cx, cy))

            label = self.results.multi_handedness[hand_idx].classification[0].label

            cx = sum([pt[1] for pt in lm_list]) // len(lm_list)
            cy = sum([pt[2] for pt in lm_list]) // len(lm_list)

            hand_data = {"label": label, "landmarks": lm_list, "center": (cx, cy)}
            all_hands.append(hand_data)

            if draw:
                cv2.circle(img, (cx, cy), 10, (255, 0, 0), cv2.FILLED)
                cv2.putText(
                    img,
                    f"{label} Hand",
                    (cx - 40, cy - 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                )

        return all_hands

    def fingers_up(self, hand):
        """
        Returns list [thumb, index, middle, ring, pinky] with 1=up, 0=down.
        """
        lm = hand["landmarks"]
        label = hand.get("label", "Right")  # Default "Right" if missing

        fingers = []

        # Thumb (depends on handedness)
        if label == "Right":
            fingers.append(1 if lm[4][1] < lm[3][1] else 0)
        else:
            fingers.append(1 if lm[4][1] > lm[3][1] else 0)

        # Other fingers: tip.y < pip.y means finger up
        tip_ids = [8, 12, 16, 20]
        for tid in tip_ids:
            fingers.append(1 if lm[tid][2] < lm[tid - 2][2] else 0)

        return fingers

    def get_angle_between_hands(self, hand1, hand2):
        """
        Compute the rotation angle (in degrees) between two hands based on their center positions.
        Useful for rotation gestures.
        """
        import math

        (x1, y1) = hand1["center"]
        (x2, y2) = hand2["center"]
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        return angle
