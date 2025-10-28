import cv2
import mediapipe as mp

class HandDetector:
    def __init__(self, detection_conf=0.7, track_conf=0.7):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=detection_conf,
            min_tracking_confidence=track_conf
        )
        self.mp_draw = mp.solutions.drawing_utils

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        if draw and self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        return img

    def find_positions(self, img, draw=False):
        all_hands = []
        if self.results.multi_hand_landmarks:
            for hand_idx, hand_lms in enumerate(self.results.multi_hand_landmarks):
                my_hand = []
                h, w, _ = img.shape
                for id, lm in enumerate(hand_lms.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    my_hand.append((id, cx, cy))

                # Add handedness label
                label = self.results.multi_handedness[hand_idx].classification[0].label
                all_hands.append({"label": label, "landmarks": my_hand})
        return all_hands

    def fingers_up(self, hand):
        lm_list = hand["landmarks"]
        fingers = []

        # Thumb
        if lm_list[4][1] > lm_list[3][1]:
            fingers.append(1)
        else:
            fingers.append(0)
        # 4 Fingers
        for id in [8, 12, 16, 20]:
            if lm_list[id][2] < lm_list[id - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers
