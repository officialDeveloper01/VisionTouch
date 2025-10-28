# modules/draw_utils.py
import cv2
import numpy as np

class AirDrawer:
    def __init__(self, width, height):
        self.canvas = np.zeros((height, width, 3), np.uint8)
        self.prev_x, self.prev_y = 0, 0
        self.brush_color = (0, 0, 255)  # Red
        self.brush_thickness = 8

    def draw(self, img, x, y, draw_mode):
        """Draw on a separate canvas and overlay on the frame."""
        if draw_mode:
            if self.prev_x == 0 and self.prev_y == 0:
                self.prev_x, self.prev_y = x, y
            cv2.line(self.canvas, (self.prev_x, self.prev_y), (x, y), self.brush_color, self.brush_thickness)
            self.prev_x, self.prev_y = x, y
        else:
            self.prev_x, self.prev_y = 0, 0  # Reset when not drawing

        # Combine drawing canvas with the webcam feed
        img_gray = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        _, inv_mask = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
        inv_mask = cv2.cvtColor(inv_mask, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, inv_mask)
        img = cv2.bitwise_or(img, self.canvas)
        return img

    def clear(self):
        self.canvas.fill(0)
