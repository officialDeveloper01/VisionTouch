import numpy as np
import cv2
import math

class Shape3D:
    def __init__(self, shape_type="cube", size=100, pos=(640, 360), color=(0, 255, 255)):
        self.shape_type = shape_type
        self.size = size
        self.pos = np.array(pos, dtype=float)
        self.color = color
        self.rotation = np.array([0.0, 0.0, 0.0])  # x, y, z rotation

    def get_vertices(self):
        s = self.size / 2
        if self.shape_type == "cube":
            return np.array([
                [-s, -s, -s],
                [ s, -s, -s],
                [ s,  s, -s],
                [-s,  s, -s],
                [-s, -s,  s],
                [ s, -s,  s],
                [ s,  s,  s],
                [-s,  s,  s]
            ])
        elif self.shape_type == "pyramid":
            return np.array([
                [-s, -s, -s],
                [ s, -s, -s],
                [ s, -s,  s],
                [-s, -s,  s],
                [ 0,  s,  0]
            ])
        else:
            return np.zeros((0, 3))

    def rotate(self, rx, ry, rz):
        self.rotation += np.array([rx, ry, rz])

    def project(self, vertices):
        # Build rotation matrices
        rx, ry, rz = np.radians(self.rotation)
        rot_x = np.array([
            [1, 0, 0],
            [0, math.cos(rx), -math.sin(rx)],
            [0, math.sin(rx),  math.cos(rx)]
        ])
        rot_y = np.array([
            [ math.cos(ry), 0, math.sin(ry)],
            [0, 1, 0],
            [-math.sin(ry), 0, math.cos(ry)]
        ])
        rot_z = np.array([
            [math.cos(rz), -math.sin(rz), 0],
            [math.sin(rz),  math.cos(rz), 0],
            [0, 0, 1]
        ])

        rotation_matrix = rot_z @ rot_y @ rot_x
        rotated = vertices @ rotation_matrix.T

        # Simple perspective projection
        f = 300  # focal length
        depth = rotated[:, 2] + f
        projected = rotated[:, :2] * (f / depth[:, np.newaxis])
        projected += self.pos
        return projected.astype(int)

    def draw(self, img):
        vertices = self.get_vertices()
        if len(vertices) == 0:
            return img

        points = self.project(vertices)

        if self.shape_type == "cube":
            edges = [
                (0,1), (1,2), (2,3), (3,0),
                (4,5), (5,6), (6,7), (7,4),
                (0,4), (1,5), (2,6), (3,7)
            ]
        elif self.shape_type == "pyramid":
            edges = [
                (0,1), (1,2), (2,3), (3,0),
                (0,4), (1,4), (2,4), (3,4)
            ]
        else:
            edges = []

        for (i, j) in edges:
            cv2.line(img, tuple(points[i]), tuple(points[j]), self.color, 2)

        return img
