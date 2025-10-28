# modules/hand_detector.py

import cv2
import mediapipe as mp

class HandDetector:
    def __init__(self, mode=False, max_hands=2, detection_conf=0.7, track_conf=0.7):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_conf = detection_conf
        self.track_conf = track_conf

        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_conf,
            min_tracking_confidence=self.track_conf
        )
        self.mp_draw = mp.solutions.drawing_utils

    def find_hands(self, img, draw=True):
        """Detect all hands and optionally draw landmarks."""
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        return img

    def find_positions(self, img, draw=True):
        """Return list of all landmarks for each detected hand."""
        all_hands = []
        if self.results.multi_hand_landmarks:
            for hand_no, hand in enumerate(self.results.multi_hand_landmarks):
                lm_list = []
                for id, lm in enumerate(hand.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append((id, cx, cy))
                    if draw:
                        cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
                        cv2.putText(img, str(id), (cx + 5, cy - 5),
                                    cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 1)
                all_hands.append(lm_list)
        return all_hands

    def fingers_up(self, lm_list):
        """Return a list of 5 elements (1 if finger is up, else 0)."""
        tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        fingers = []

        # Thumb
        if lm_list[tips[0]][1] > lm_list[tips[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Fingers
        for id in range(1, 5):
            if lm_list[tips[id]][2] < lm_list[tips[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers
