from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
import math

class Shape3DManager:
    def __init__(self):
        self.shapes = []

    def init_window(self):
        pygame.init()
        pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (800 / 600), 0.1, 50.0)
        glTranslatef(0.0, 0.0, -5)

    def create_shape(self, shape_type):
        shape = {"type": shape_type, "scale": 1.0, "rotation": [0, 0, 0], "pos": [0, 0, 0]}
        self.shapes.append(shape)
        return shape

    def draw_cube(self, size=1):
        glBegin(GL_QUADS)
        for surface in (
            (0, 1, 2, 3),
            (3, 2, 6, 7),
            (7, 6, 5, 4),
            (4, 5, 1, 0),
            (1, 5, 6, 2),
            (4, 0, 3, 7),
        ):
            for vertex in surface:
                glColor3fv((1, 0.5, 0.2))
                glVertex3fv([
                    (-1 if vertex & 1 else 1) * size,
                    (-1 if vertex & 2 else 1) * size,
                    (-1 if vertex & 4 else 1) * size,
                ])
        glEnd()

    def draw_sphere(self, radius=1):
        quad = gluNewQuadric()
        glColor3f(0.3, 0.6, 1)
        gluSphere(quad, radius, 32, 32)

    def draw_pyramid(self, size=1):
        glBegin(GL_TRIANGLES)
        glColor3f(1, 0, 0)
        glVertex3f(0, size, 0)
        glVertex3f(-size, -size, size)
        glVertex3f(size, -size, size)

        glColor3f(0, 1, 0)
        glVertex3f(0, size, 0)
        glVertex3f(size, -size, size)
        glVertex3f(size, -size, -size)

        glColor3f(0, 0, 1)
        glVertex3f(0, size, 0)
        glVertex3f(size, -size, -size)
        glVertex3f(-size, -size, -size)

        glColor3f(1, 1, 0)
        glVertex3f(0, size, 0)
        glVertex3f(-size, -size, -size)
        glVertex3f(-size, -size, size)
        glEnd()

    def render_scene(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for shape in self.shapes:
            glPushMatrix()
            glTranslatef(*shape["pos"])
            glScalef(shape["scale"], shape["scale"], shape["scale"])
            glRotatef(shape["rotation"][0], 1, 0, 0)
            glRotatef(shape["rotation"][1], 0, 1, 0)
            glRotatef(shape["rotation"][2], 0, 0, 1)

            if shape["type"] == "cube":
                self.draw_cube(0.5)
            elif shape["type"] == "sphere":
                self.draw_sphere(0.5)
            elif shape["type"] == "pyramid":
                self.draw_pyramid(0.5)
            glPopMatrix()

        pygame.display.flip()
        pygame.time.wait(10)

    def move_shape(self, shape, cursor):
        x, y = cursor
        shape["pos"][0] = (x - 640) / 320
        shape["pos"][1] = -(y - 360) / 320

    def rotate_shape(self, shape, x_angle, y_angle, z_angle):
        shape["rotation"][0] += x_angle
        shape["rotation"][1] += y_angle
        shape["rotation"][2] += z_angle

    def scale_shape(self, shape, factor):
        shape["scale"] += factor
        shape["scale"] = max(0.2, min(3.0, shape["scale"]))

    # ------------------------------------------------------------
# Compatibility wrappers for main.py
# ------------------------------------------------------------

_manager = Shape3DManager()
_manager.init_window()

def create_shape_3d(shape_type, pos):
    """Create a 3D shape at the given screen position."""
    shape = _manager.create_shape(shape_type)
    # Convert 2D position to OpenGL 3D coordinate
    x, y = pos
    shape["pos"] = [(x - 640) / 320, -(y - 360) / 320, 0]
    return shape

def draw_shape_3d(img, shape=None):
    """Render the 3D scene using PyOpenGL and pygame."""
    _manager.render_scene()
    return img

# Optional helper for movement, rotation, scaling
def move_shape_3d(shape, cursor):
    _manager.move_shape(shape, cursor)

def rotate_shape_3d(shape, x_angle, y_angle, z_angle):
    _manager.rotate_shape(shape, x_angle, y_angle, z_angle)

def scale_shape_3d(shape, factor):
    _manager.scale_shape(shape, factor)
