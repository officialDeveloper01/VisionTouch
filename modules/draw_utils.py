# modules/draw_utils.py
import cv2
import numpy as np
import math

class AirDrawer:
    def __init__(self, width, height):
        self.canvas = np.zeros((height, width, 3), np.uint8)
        self.prev_x, self.prev_y = 0, 0
        self.brush_color = (0, 0, 255)
        self.brush_thickness = 8
        self.eraser_thickness = 50
        self.offset_x, self.offset_y = 0, 0
        self.move_start_x, self.move_start_y = None, None

    def _smooth_line(self, x1, y1, x2, y2):
        """Draw smooth interpolated line between points."""
        dist = int(math.hypot(x2 - x1, y2 - y1))
        if dist == 0:
            return
        for i in range(0, dist, 1):
            t = i / dist
            xi = int(x1 + (x2 - x1) * t)
            yi = int(y1 + (y2 - y1) * t)
            cv2.circle(self.canvas, (xi, yi), self.brush_thickness // 2, self.brush_color, -1)

    def draw(self, img, x, y, mode):
        """Draw, erase, or move based on mode."""
        if mode == "DRAW":
            if self.prev_x == 0 and self.prev_y == 0:
                self.prev_x, self.prev_y = x, y
            self._smooth_line(self.prev_x, self.prev_y, x, y)
            self.prev_x, self.prev_y = x, y

        elif mode == "ERASE":
            cv2.circle(self.canvas, (x, y), self.eraser_thickness, (0, 0, 0), -1)

        elif mode == "MOVE":
            if self.move_start_x is None:
                self.move_start_x, self.move_start_y = x, y
            else:
                dx = x - self.move_start_x
                dy = y - self.move_start_y
                self.offset_x += dx
                self.offset_y += dy
                self.move_start_x, self.move_start_y = x, y
                self.canvas = np.roll(self.canvas, dx, axis=1)
                self.canvas = np.roll(self.canvas, dy, axis=0)

        else:
            self.prev_x, self.prev_y = 0, 0
            self.move_start_x, self.move_start_y = None, None

        # Merge canvas with live frame
        img_gray = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        _, inv_mask = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
        inv_mask = cv2.cvtColor(inv_mask, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, inv_mask)
        img = cv2.bitwise_or(img, self.canvas)
        return img
    
    def overlay_on_frame(self, frame):
        return cv2.addWeighted(frame, 1, self.canvas, 1, 0)

    def clear(self):
        self.canvas.fill(0)
