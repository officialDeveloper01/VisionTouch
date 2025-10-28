import cv2
import numpy as np


class AirDrawer:
    def __init__(self, width, height):
        self.canvas = np.zeros((height, width, 3), np.uint8)
        self.last_point = None
        self.smoothed_point = None
        self.alpha = 0.3  # smoothing factor (0–1)
        self.mode = "DRAW"
        self.offset_x = 0
        self.offset_y = 0

    def _smooth_point(self, x, y):
        """Apply exponential smoothing to the fingertip position."""
        if self.smoothed_point is None:
            self.smoothed_point = np.array([x, y], dtype=np.float32)
        else:
            self.smoothed_point = (
                self.alpha * np.array([x, y], dtype=np.float32)
                + (1 - self.alpha) * self.smoothed_point
            )
        return int(self.smoothed_point[0]), int(self.smoothed_point[1])

    def _interpolate_line(self, p1, p2):
        """Generate interpolated points to avoid gaps on fast movement."""
        x1, y1 = p1
        x2, y2 = p2
        dist = int(np.hypot(x2 - x1, y2 - y1))
        points = []
        for i in range(1, dist + 1):
            r = i / dist
            x = int(x1 + r * (x2 - x1))
            y = int(y1 + r * (y2 - y1))
            points.append((x, y))
        return points

    def draw(self, frame, x, y, mode):
        x, y = self._smooth_point(x, y)

        if mode == "DRAW":
            if self.last_point is None:
                self.last_point = (x, y)
            for px, py in self._interpolate_line(self.last_point, (x, y)):
                cv2.circle(self.canvas, (px, py), 3, (0, 255, 0), -1)
            self.last_point = (x, y)

        elif mode == "ERASE":
            cv2.circle(self.canvas, (x, y), 35, (0, 0, 0), -1)
            self.last_point = None

        elif mode == "MOVE":
            if self.last_point is None:
                self.last_point = (x, y)
            dx = x - self.last_point[0]
            dy = y - self.last_point[1]
            M = np.float32([[1, 0, dx], [0, 1, dy]])
            self.canvas = cv2.warpAffine(
                self.canvas, M, (self.canvas.shape[1], self.canvas.shape[0])
            )
            self.last_point = (x, y)

        else:
            self.last_point = None

        return frame

    def overlay_on_frame(self, frame):
        mask = self.canvas.astype(bool)
        frame[mask] = cv2.addWeighted(frame, 0.6, self.canvas, 0.7, 0)[mask]
        return frame

    def clear(self):
        self.canvas[:] = 0
        self.last_point = None
        self.smoothed_point = None
