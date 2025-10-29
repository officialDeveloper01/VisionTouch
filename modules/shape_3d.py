from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
import cv2
import math


class Shape3DManager:
    def __init__(self):
        self.active_shape = "cube"
        self.rotation = [0, 0]
        self.scale = 1.0
        self.position = [0, 0]
        self.pinch_active = {"left": False, "right": False}

    def set_active_shape(self, shape_type):
        self.active_shape = shape_type

    def handle_pinch(self, center, label):
        """Move or rotate the 3D shape based on pinch gesture."""
        self.pinch_active[label] = True
        if label == "left":
            # Move object
            self.position[0] = (center[0] - 640) / 100
            self.position[1] = (360 - center[1]) / 100
        else:
            # Rotate object
            self.rotation[0] = (center[1] - 360) / 3
            self.rotation[1] = (center[0] - 640) / 3

    def handle_release(self, label):
        self.pinch_active[label] = False

    def draw_cube(self):
        glutSolidCube(1.0)

    def draw_pyramid(self):
        glBegin(GL_TRIANGLES)
        vertices = [
            [0, 1, 0],
            [-1, -1, 1],
            [1, -1, 1],
            [1, -1, -1],
            [-1, -1, -1],
        ]
        faces = [
            [0, 1, 2],
            [0, 2, 3],
            [0, 3, 4],
            [0, 4, 1],
            [1, 2, 3, 4]
        ]
        for face in faces[:4]:
            for v in face:
                glVertex3fv(vertices[v])
        glEnd()

    def draw_sphere(self):
        quad = gluNewQuadric()
        gluSphere(quad, 0.8, 32, 32)

    def draw_cylinder(self):
        quad = gluNewQuadric()
        gluCylinder(quad, 0.5, 0.5, 1.2, 32, 32)

    def render_preview(self, frame):
        """Render the 3D shape as an overlay in OpenCV window."""
        h, w, _ = frame.shape
        preview = np.zeros((h, w, 3), dtype=np.uint8)

        # Create an off-screen OpenGL context
        glutInit()
        glutInitDisplayMode(GLUT_RGB | GLUT_DEPTH | GLUT_DOUBLE)
        glutInitWindowSize(400, 400)
        glutCreateWindow(b"3D Preview")

        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslatef(self.position[0], self.position[1], -4.0)
        glScalef(self.scale, self.scale, self.scale)
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)

        glColor3f(0.3, 0.8, 1.0)
        if self.active_shape == "cube":
            self.draw_cube()
        elif self.active_shape == "pyramid":
            self.draw_pyramid()
        elif self.active_shape == "sphere":
            self.draw_sphere()
        elif self.active_shape == "cylinder":
            self.draw_cylinder()

        glutSwapBuffers()
        glutHideWindow()

        cv2.putText(preview, f"3D Mode: {self.active_shape}", (40, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        return preview
