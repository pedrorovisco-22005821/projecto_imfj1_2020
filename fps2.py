"""Cubefall sample application"""
import time
import random
import pygame

from quaternion import Quaternion

from scene import Scene
from object3d import Object3d
from camera import Camera
from mesh import Mesh
from material import Material
from color import Color
from vector3 import Vector3
from vector4 import Vector4

GRAVITY = -0.5
m_s = 0.01

class FallingCube(Object3d):
    """Falling cube 3d object"""

    def __init__(self, mesh):
        super().__init__("FallingCube")
        # Create a cube on a random positions
        self.position = Vector3(random.uniform(-6, 6),
                                random.uniform(6, 10), random.uniform(3, 10))
        self.mesh = mesh
        # Pick a random Color for the cube
        self.material = Material(Color(random.uniform(0.1, 1),
                                       random.uniform(0.1, 1),
                                       random.uniform(0.1, 1), 1),
                                 "FallingCubeMaterial")
        # Starting velocity is zero
        self.velocity = 0
        # Select a random rotation axis
        self.rotation_axis = Vector3(random.uniform(-1, 1),
                                     random.uniform(-1, 1),
                                     random.uniform(-1, 1)).normalized()
        # Select a random rotation speed
        self.rotation_speed = random.uniform(-0.5, 0.5)

    def update(self, delta_time):
        """Animates the cube, accelerating it with gravity and rotating it."""
        self.velocity += GRAVITY * delta_time
        self.position.y += self.velocity * delta_time

        q = Quaternion.AngleAxis(
            self.rotation_axis, self.rotation_speed * delta_time)
        self.rotation = q * self.rotation


def main():
    """Main function, it implements the application loop"""
    # Initialize pygame, with the default parameters
    pygame.init()

    # Define the size/resolution of our window
    res_x = 640
    res_y = 480

    # Create a window and a display surface
    screen = pygame.display.set_mode((res_x, res_y))

    # Create a scene
    scene = Scene("TestScene")
    scene.camera = Camera(False, res_x, res_y)

    # Moves the camera back 2 units
    scene.camera.position -= Vector3(0, 0, 2)

    # Create the cube mesh we're going to use for every single object
    cube_mesh = Mesh.create_cube((1, 1, 1))
    # Spawn rate is one cube every 500 ms
    spawn_rate = 0.5
    # Keep a timer for the cube spawn
    cube_spawn_time = spawn_rate
    # Storage for all the objects created this way
    falling_objects = []

    # Timer
    delta_time = 0
    prev_time = time.time()

    # Hide mouse cursor
    pygame.mouse.set_visible(False)
    # Lock the mouse cursor to the game window
    pygame.event.set_grab(True)
    locked = True

    #pygame.mouse.get_rel((x, y))
    pygame.mouse.set_pos(res_x / 2.0, res_y / 2.0)

    # Game loop, runs forever
    while True:
        # Process OS events
        for event in pygame.event.get():
            # Checks if the user closed the window
            if event.type == pygame.QUIT:
                # Exits the application immediately
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # If ESC is pressed release mouse
                    pygame.event.set_grab(False)
                    pygame.mouse.set_visible(True)
                    locked = False
                elif event.key == pygame.K_w:
                    # move player forward
                    move_player(scene.camera, Vector3(0, 0, 1))
                elif event.key == pygame.K_a:
                    # move player left
                    move_player(scene.camera, Vector3(-1, 0, 0))
                elif event.key == pygame.K_s:
                    # move player backward
                    move_player(scene.camera, Vector3(0, 0, -1))
                elif event.key == pygame.K_d:
                    # move player right
                    move_player(scene.camera, Vector3(1, 0, 0))
            elif event.type == pygame.MOUSEMOTION and locked:
                (mouse_x, mouse_y) = event.rel
                q1 = Quaternion.AngleAxis(Vector3(1, 0, 0), mouse_x * m_s)
                q2 = Quaternion.AngleAxis(Vector3(0, -1, 0), mouse_y * m_s)
                scene.camera.rotation = q1 * q2 * scene.camera.rotation
                # ^move camera with this
                #TODO: update rotation
                pygame.mouse.set_pos(res_x / 2.0, res_y / 2.0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not locked:
                    pygame.mouse.set_visible(False)
                    pygame.event.set_grab(True)
                    locked = True
                    pygame.mouse.set_pos(res_x / 2.0, res_y / 2.0)

        # Clears the screen with a very dark blue (0, 0, 20)
        screen.fill((0, 0, 0))

        # Update the cube spawn timer
        cube_spawn_time = cube_spawn_time - delta_time
        if cube_spawn_time < 0:
            # It's time to spawn a new cube
            cube_spawn_time = spawn_rate

            # Create a new cube, and add it to the scene
            new_cube = FallingCube(cube_mesh)
            scene.add_object(new_cube)

            # Add the new cube to the storage, so it can be updated
            falling_objects.append(new_cube)

        # Update the cubes
        for falling_object in falling_objects:
            falling_object.update(delta_time)

            # Is the cube fallen too far?
            if falling_object.position.y < -8:
                # Remove cube from scene
                scene.remove_object(falling_object)

        # Update the storage, so that all cubes that have fallen too far disappear
        falling_objects = [x for x in falling_objects if x.position.y > -8]

        # Render the scene
        scene.render(screen)

        # Swaps the back and front buffer, effectively displaying what we rendered
        pygame.display.flip()

        # Updates the timer, so we we know how long has it been since the last frame
        delta_time = time.time() - prev_time
        prev_time = time.time()

def move_player(camera, vec):
    #TODO: get forward axis and sideways axis, update pos
    q1 = camera.rotation
    #TODO: test
    v = Vector4(vec.x, vec.y, vec.z, 0)
    q2 = Quaternion(v)
    v2 = q1 * q2 * q1.inverted()
    v3 = Vector3(v2.x, v2.y, v2.z)
    camera.position = camera.position + v3
    #pass

# Run the main function
main()
