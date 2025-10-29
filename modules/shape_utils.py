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
        self.drawing_points = []
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

    def _random_color(self):
        return tuple(random.randint(80, 255) for _ in range(3))

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
                "x": x,
                "y": y,
                "size": size,
                "color": color,
                "type": shape_type,
                "rotation": 0  # new rotation attribute
            })

    def finish_draw(self):
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

    def rotate_shape(self, shape, angle_delta):
        """Rotate shape by delta angle in degrees."""
        if shape and shape["type"] != "draw":
            shape["rotation"] = (shape.get("rotation", 0) + angle_delta) % 360

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

    def draw_rotated_polygon(self, frame, pts, color):
        """Draw polygon after rotating its points."""
        cv2.fillPoly(frame, [pts.astype(np.int32)], color)

    def draw_shape(self, frame, shape):
        color = shape["color"]
        cx, cy = shape["x"] + shape["size"] // 2, shape["y"] + shape["size"] // 2
        angle = math.radians(shape.get("rotation", 0))

        def rotate_point(x, y):
            dx, dy = x - cx, y - cy
            x_rot = cx + dx * math.cos(angle) - dy * math.sin(angle)
            y_rot = cy + dx * math.sin(angle) + dy * math.cos(angle)
            return int(x_rot), int(y_rot)

        if shape["type"] == "square":
            pts = np.array([
                rotate_point(shape["x"], shape["y"]),
                rotate_point(shape["x"] + shape["size"], shape["y"]),
                rotate_point(shape["x"] + shape["size"], shape["y"] + shape["size"]),
                rotate_point(shape["x"], shape["y"] + shape["size"]),
            ])
            self.draw_rotated_polygon(frame, pts, color)

        elif shape["type"] == "circle":
            cv2.circle(frame, (cx, cy), shape["size"] // 2, color, -1)

        elif shape["type"] == "triangle":
            pts = np.array([
                (shape["x"] + shape["size"] // 2, shape["y"]),
                (shape["x"], shape["y"] + shape["size"]),
                (shape["x"] + shape["size"], shape["y"] + shape["size"]),
            ])
            pts = np.array([rotate_point(x, y) for x, y in pts])
            self.draw_rotated_polygon(frame, pts, color)

        elif shape["type"] == "star":
            pts = []
            for i in range(10):
                angle_deg = i * 36
                r = shape["size"] // 2 if i % 2 == 0 else shape["size"] // 4
                x = int(cx + r * math.cos(math.radians(angle_deg)))
                y = int(cy + r * math.sin(math.radians(angle_deg)))
                pts.append(rotate_point(x, y))
            self.draw_rotated_polygon(frame, np.array(pts), color)

        elif shape["type"] in ["pentagon", "hexagon"]:
            sides = 5 if shape["type"] == "pentagon" else 6
            pts = np.array([
                rotate_point(
                    int(cx + shape["size"] // 2 * math.cos(2 * math.pi * i / sides)),
                    int(cy + shape["size"] // 2 * math.sin(2 * math.pi * i / sides))
                )
                for i in range(sides)
            ])
            self.draw_rotated_polygon(frame, pts, color)

        elif shape["type"] == "draw":
            for i in range(1, len(shape["points"])):
                cv2.line(frame, shape["points"][i - 1], shape["points"][i], color, 4)

    def draw_ui(self, frame):
        for shape in self.shapes:
            self.draw_shape(frame, shape)

        if self.drawing and self.current_draw:
            for i in range(1, len(self.current_draw["points"])):
                cv2.line(frame, self.current_draw["points"][i - 1], self.current_draw["points"][i],
                         self.current_draw["color"], 4)

        # Buttons
        for btn in self.buttons:
            cv2.rectangle(frame, (btn["x"], btn["y"]), (btn["x"] + btn["w"], btn["y"] + btn["h"]), (0, 0, 0), -1)
            cv2.rectangle(frame, (btn["x"], btn["y"]), (btn["x"] + btn["w"], btn["y"] + btn["h"]), (255, 255, 255), 2)
            cv2.putText(frame, btn["label"], (btn["x"] + 20, btn["y"] + 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Bin
        bx, by, bw, bh = self.bin.values()
        cv2.rectangle(frame, (bx, by), (bx + bw, by + bh), (0, 0, 255), 2)
        cv2.putText(frame, "🗑️", (bx + 30, by + 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)

        return frame
