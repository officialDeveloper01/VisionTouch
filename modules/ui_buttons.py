import cv2

class UIButtonManager:
    def __init__(self):
        self.buttons_2d = [
            {"label": "Square", "x": 60, "y": 50, "w": 150, "h": 70, "type": "square"},
            {"label": "Circle", "x": 230, "y": 50, "w": 150, "h": 70, "type": "circle"},
            {"label": "Triangle", "x": 400, "y": 50, "w": 150, "h": 70, "type": "triangle"},
            {"label": "Draw", "x": 570, "y": 50, "w": 150, "h": 70, "type": "draw"},
            {"label": "➡ 3D Mode", "x": 1080, "y": 50, "w": 150, "h": 70, "type": "toggle_mode"},
        ]

        self.buttons_3d = [
            {"label": "Cube", "x": 60, "y": 50, "w": 150, "h": 70, "type": "cube"},
            {"label": "Pyramid", "x": 230, "y": 50, "w": 150, "h": 70, "type": "pyramid"},
            {"label": "Sphere", "x": 400, "y": 50, "w": 150, "h": 70, "type": "sphere"},
            {"label": "Cylinder", "x": 570, "y": 50, "w": 150, "h": 70, "type": "cylinder"},
            {"label": "⬅ 2D Mode", "x": 1080, "y": 50, "w": 150, "h": 70, "type": "toggle_mode"},
        ]

    def check_button_click(self, px, py):
        all_btns = self.buttons_2d + self.buttons_3d
        for btn in all_btns:
            if btn["x"] <= px <= btn["x"] + btn["w"] and btn["y"] <= py <= btn["y"] + btn["h"]:
                return btn["type"]
        return None

    def draw_buttons(self, frame, mode_3d=False):
        
        btns = self.buttons_3d if mode_3d else self.buttons_2d
        for btn in btns:
            cv2.rectangle(frame, (btn["x"], btn["y"]),
                          (btn["x"] + btn["w"], btn["y"] + btn["h"]), (0, 0, 0), -1)
            cv2.rectangle(frame, (btn["x"], btn["y"]),
                          (btn["x"] + btn["w"], btn["y"] + btn["h"]), (255, 255, 255), 2)
            cv2.putText(frame, btn["label"], (btn["x"] + 15, btn["y"] + 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        return frame
