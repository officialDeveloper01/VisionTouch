import pyautogui
import numpy as np
import cv2
import time

class VirtualMouse:
    def __init__(self, screen_w=None, screen_h=None, smoothening=3):
        self.screen_w, self.screen_h = pyautogui.size() if not screen_w else (screen_w, screen_h)
        self.smoothening = smoothening
        self.prev_x, self.prev_y = 0, 0
        self.curr_x, self.curr_y = 0, 0
        self.last_click_time = 0

    def move_cursor(self, x, y, frame_w, frame_h):
        # Map hand coords → screen coords
        target_x = np.interp(x, (100, frame_w - 100), (0, self.screen_w))
        target_y = np.interp(y, (100, frame_h - 100), (0, self.screen_h))

        # Smooth movement
        self.curr_x = self.prev_x + (target_x - self.prev_x) / self.smoothening
        self.curr_y = self.prev_y + (target_y - self.prev_y) / self.smoothening

        pyautogui.moveTo(self.curr_x, self.curr_y, _pause=False)
        self.prev_x, self.prev_y = self.curr_x, self.curr_y

        return int(self.curr_x), int(self.curr_y)

    def click_if_pinch(self, dist, threshold=40):
        """Perform a click if thumb and index are close (with cooldown)."""
        current_time = time.time()
        if dist < threshold and (current_time - self.last_click_time) > 0.4:
            pyautogui.click()
            self.last_click_time = current_time
            return True
        return False
