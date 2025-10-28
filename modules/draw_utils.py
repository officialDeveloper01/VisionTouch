# modules/draw_utils.py
import cv2
import numpy as np

class AirDrawer:
    def __init__(self, width, height):
        self.canvas = np.zeros((height, width, 3), np.uint8)
        self.last_point = None

    def draw(self, frame, x, y, mode):
        if mode == "DRAW":
            if self.last_point is None:
                self.last_point = (x, y)
            cv2.line(self.canvas, self.last_point, (x, y), (0, 0, 255), 5)  # red
            self.last_point = (x, y)

        elif mode == "ERASE":
            cv2.circle(self.canvas, (x, y), 40, (0, 0, 0), -1)
            self.last_point = None

        elif mode == "MOVE":
            if self.last_point is None:
                self.last_point = (x, y)
            dx = x - self.last_point[0]
            dy = y - self.last_point[1]
            M = np.float32([[1, 0, dx], [0, 1, dy]])
            self.canvas = cv2.warpAffine(self.canvas, M, (self.canvas.shape[1], self.canvas.shape[0]))
            self.last_point = (x, y)

        else:
            self.last_point = None

        return frame

    def overlay_on_frame(self, frame):
        mask = self.canvas.astype(bool)
        frame[mask] = cv2.addWeighted(frame, 0.6, self.canvas, 0.8, 0)[mask]
        return frame

    def clear(self):
        self.canvas[:] = 0
        self.last_point = None
