# modules/cube_utils.py
import cv2
import numpy as np
import random

class CubeManager:
    def __init__(self, width, height, num_cubes=4):
        self.width = width
        self.height = height
        self.cubes = []
        self.selected_cube = None
        self.last_pos = None
        self.colors = [(255, 0, 0), (0, 255, 0), (0, 255, 255), (255, 0, 255)]
        for i in range(num_cubes):
            x, y = random.randint(100, width-200), random.randint(100, height-200)
            size = random.randint(80, 120)
            color = self.colors[i % len(self.colors)]
            self.cubes.append({"x": x, "y": y, "size": size, "color": color})

    def draw_cubes(self, frame):
        for cube in self.cubes:
            x, y, s = cube["x"], cube["y"], cube["size"]
            color = cube["color"]
            cv2.rectangle(frame, (x, y), (x + s, y + s), color, -1)
            cv2.rectangle(frame, (x, y), (x + s, y + s), (255, 255, 255), 2)
        return frame

    def select_cube(self, px, py):
        for cube in self.cubes:
            if cube["x"] <= px <= cube["x"] + cube["size"] and cube["y"] <= py <= cube["y"] + cube["size"]:
                self.selected_cube = cube
                self.last_pos = (px, py)
                return cube
        return None

    def move_selected_cube(self, px, py):
        if self.selected_cube and self.last_pos:
            dx = px - self.last_pos[0]
            dy = py - self.last_pos[1]
            self.selected_cube["x"] += int(dx)
            self.selected_cube["y"] += int(dy)
            self.last_pos = (px, py)

    def release_cube(self):
        self.selected_cube = None
        self.last_pos = None
