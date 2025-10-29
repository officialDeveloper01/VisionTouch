# modules/shape_utils.py
import cv2
import numpy as np
import random
import math


class ShapeManager:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.shapes = []
        self.selected_left = None
        self.selected_right = None
        self.last_left_pos = None
        self.last_right_pos = None
        self.drawing_points = []  # store points for draw mode
        self.drawing = False
        self.current_draw = None

        # Button areas
        self.buttons = [
            {"label": "Square", "x": 60, "y": 50, "w": 150, "h": 70, "type": "square"},
            {"label": "Circle", "x": 230, "y": 50, "w": 150, "h": 70, "type": "circle"},
            {"label": "Triangle", "x": 400, "y": 50, "w": 150, "h": 70, "type": "triangle"},
            {"label": "Star", "x": 570, "y": 50, "w": 150, "h": 70, "type": "star"},
            {"label": "Pentagon", "x": 740, "y": 50, "w": 150, "h": 70, "type": "pentagon"},
            {"label": "Hexagon", "x": 910, "y": 50, "w": 150, "h": 70, "type": "hexagon"},
            {"label": "Draw", "x": 1080, "y": 50, "w": 150, "h": 70, "type": "draw"},
        ]

        # Bin area
        self.bin = {"x": width - 200, "y": height - 150, "w": 120, "h": 120}

    # ---------------- Utility ---------------- #

    def _random_color(self):
        return tuple(random.randint(80, 255) for _ in range(3))

    # ---------------- Shape Actions ---------------- #

    def add_shape(self, shape_type):
        size = random.randint(60, 120)
        x = random.randint(100, self.width - 300)
        y = random.randint(200, self.height - 250)
        color = self._random_color()

        if shape_type == "draw":
            self.drawing = True
            self.current_draw = {"type": "draw", "points": [], "color": color}
        else:
            self.shapes.append({
                "x": x, "y": y, "size": size, "color": color, "type": shape_type
            })

    def finish_draw(self):
        """End the draw mode and save it as a shape."""
        if self.current_draw and len(self.current_draw["points"]) > 5:
            self.shapes.append(self.current_draw)
        self.drawing = False
        self.current_draw = None
        self.drawing_points.clear()

    def select_shape(self, px, py):
        for shape in reversed(self.shapes):
            if shape["type"] in ["square", "pentagon", "hexagon"]:
                if shape["x"] <= px <= shape["x"] + shape["size"] and shape["y"] <= py <= shape["y"] + shape["size"]:
                    return shape
            elif shape["type"] in ["circle", "triangle", "star"]:
                cx, cy = shape["x"] + shape["size"] // 2, shape["y"] + shape["size"] // 2
                if (px - cx) ** 2 + (py - cy) ** 2 <= (shape["size"] // 2) ** 2:
                    return shape
            elif shape["type"] == "draw":
                pts = np.array(shape["points"])
                if len(pts) > 0:
                    x_min, y_min = np.min(pts[:, 0]), np.min(pts[:, 1])
                    x_max, y_max = np.max(pts[:, 0]), np.max(pts[:, 1])
                    if x_min <= px <= x_max and y_min <= py <= y_max:
                        return shape
        return None

    def move_shape(self, shape, px, py, last_pos):
        if shape and last_pos:
            dx = px - last_pos[0]
            dy = py - last_pos[1]
            if shape["type"] == "draw":
                shape["points"] = [(x + dx, y + dy) for (x, y) in shape["points"]]
            else:
                shape["x"] += int(dx)
                shape["y"] += int(dy)
                shape["x"] = np.clip(shape["x"], 0, self.width - shape["size"])
                shape["y"] = np.clip(shape["y"], 0, self.height - shape["size"])
        return (px, py)

    def remove_shape_if_in_bin(self, shape):
        bx, by, bw, bh = self.bin.values()
        if shape["type"] == "draw":
            pts = np.array(shape["points"])
            if len(pts) == 0:
                return False
            cx, cy = np.mean(pts[:, 0]), np.mean(pts[:, 1])
        else:
            cx, cy = shape["x"] + shape["size"] / 2, shape["y"] + shape["size"] / 2

        if bx < cx < bx + bw and by < cy < by + bh:
            self.shapes.remove(shape)
            return True
        return False

    def check_button_click(self, px, py):
        for btn in self.buttons:
            if btn["x"] <= px <= btn["x"] + btn["w"] and btn["y"] <= py <= btn["y"] + btn["h"]:
                return btn["type"]
        return None

    # ---------------- Drawing on Frame ---------------- #

    def draw_shape(self, frame, shape):
        color = shape["color"]

        if shape["type"] == "square":
            cv2.rectangle(frame, (shape["x"], shape["y"]),
                          (shape["x"] + shape["size"], shape["y"] + shape["size"]), color, -1)

        elif shape["type"] == "circle":
            center = (shape["x"] + shape["size"] // 2, shape["y"] + shape["size"] // 2)
            cv2.circle(frame, center, shape["size"] // 2, color, -1)

        elif shape["type"] == "triangle":
            pts = np.array([
                [shape["x"] + shape["size"] // 2, shape["y"]],
                [shape["x"], shape["y"] + shape["size"]],
                [shape["x"] + shape["size"], shape["y"] + shape["size"]],
            ], np.int32)
            cv2.fillPoly(frame, [pts], color)

        elif shape["type"] == "star":
            cx, cy = shape["x"] + shape["size"] // 2, shape["y"] + shape["size"] // 2
            pts = []
            for i in range(10):
                angle = i * 36
                r = shape["size"] // 2 if i % 2 == 0 else shape["size"] // 4
                x = int(cx + r * math.cos(math.radians(angle)))
                y = int(cy + r * math.sin(math.radians(angle)))
                pts.append([x, y])
            cv2.fillPoly(frame, [np.array(pts, np.int32)], color)

        elif shape["type"] in ["pentagon", "hexagon"]:
            sides = 5 if shape["type"] == "pentagon" else 6
            cx, cy = shape["x"] + shape["size"] // 2, shape["y"] + shape["size"] // 2
            pts = np.array([
                (int(cx + shape["size"] // 2 * math.cos(2 * math.pi * i / sides)),
                 int(cy + shape["size"] // 2 * math.sin(2 * math.pi * i / sides)))
                for i in range(sides)
            ], np.int32)
            cv2.fillPoly(frame, [pts], color)

        elif shape["type"] == "draw":
            for i in range(1, len(shape["points"])):
                cv2.line(frame, shape["points"][i - 1], shape["points"][i], color, 4)

    def draw_ui(self, frame):
        # Draw all shapes
        for shape in self.shapes:
            self.draw_shape(frame, shape)

        # Draw ongoing drawing
        if self.drawing and self.current_draw:
            for i in range(1, len(self.current_draw["points"])):
                cv2.line(frame, self.current_draw["points"][i - 1], self.current_draw["points"][i],
                         self.current_draw["color"], 4)

        # Draw buttons
        for btn in self.buttons:
            cv2.rectangle(frame, (btn["x"], btn["y"]),
                          (btn["x"] + btn["w"], btn["y"] + btn["h"]), (0, 0, 0), -1)
            cv2.rectangle(frame, (btn["x"], btn["y"]),
                          (btn["x"] + btn["w"], btn["y"] + btn["h"]), (255, 255, 255), 2)
            cv2.putText(frame, btn["label"], (btn["x"] + 20, btn["y"] + 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Draw bin
        bx, by, bw, bh = self.bin.values()
        cv2.rectangle(frame, (bx, by), (bx + bw, by + bh), (0, 0, 255), 2)
        cv2.putText(frame, "Bin", (bx + 30, by + 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)

        return frame
