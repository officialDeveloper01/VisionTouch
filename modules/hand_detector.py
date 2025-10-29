# modules/hand_detector.py
import cv2
import mediapipe as mp

class HandDetector:
    def __init__(self, detection_conf=0.7, track_conf=0.7, max_hands=2):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_conf,
            min_tracking_confidence=track_conf
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None

    def find_hands(self, img, draw=True):
        """
        Process the provided image (BGR). IMPORTANT: pass the raw (unflipped) frame here.
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        if draw and self.results and self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        return img

    def find_positions(self, img, draw=False):
        """
        Returns list of hands; each hand is dict:
            { "label": "Right"/"Left", "landmarks": [ (id, x, y), ... ] }
        Coordinates (x,y) are pixel coordinates in the SAME IMAGE you passed to find_hands().
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

            # Handedness label from Mediapipe (corresponds to the image passed)
            label = self.results.multi_handedness[hand_idx].classification[0].label
            all_hands.append({"label": label, "landmarks": lm_list})

        return all_hands

    def fingers_up(self, hand):
        """
        Expect `hand` as returned by find_positions (dict).
        Returns list [thumb, index, middle, ring, pinky] with 1=up,0=down.
        Uses a robust test: for non-thumb fingers compare tip.y < pip.y.
        For thumb use x comparison depending on handedness.
        """
        lm = hand["landmarks"]
        label = hand.get("label", "Right")  # default Right if missing

        fingers = []

        # Thumb: decide direction based on handedness
        # For the raw (unflipped) image coordinates:
        # - For "Right" hand, thumb tip (4).x < ip.x (3) means thumb is open (to the left)
        # - For "Left" hand, thumb tip (4).x > ip.x (3) means thumb is open (to the right)
        if label == "Right":
            fingers.append(1 if lm[4][1] < lm[3][1] else 0)
        else:
            fingers.append(1 if lm[4][1] > lm[3][1] else 0)

        # Other fingers: tip.y < pip.y -> finger up (y increases downward)
        tip_ids = [8, 12, 16, 20]
        for tid in tip_ids:
            fingers.append(1 if lm[tid][2] < lm[tid - 2][2] else 0)

        return fingers