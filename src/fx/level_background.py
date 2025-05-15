import pygame
import random
import math
from src.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, LEVEL_BG_GRADIENT_TOP, LEVEL_BG_GRADIENT_BOTTOM,
    LEVEL_BG_PARTICLE_COLORS, LEVEL_BG_PARTICLE_COUNT, LEVEL_BG_PARTICLE_SPEED_RANGE,
    LEVEL_BG_PARTICLE_RADIUS_RANGE, LEVEL_BG_WISP_COLORS, LEVEL_BG_WISP_COUNT,
    LEVEL_BG_WISP_MAX_LENGTH, LEVEL_BG_WISP_MAX_WIDTH, LEVEL_BG_WISP_SPEED_RANGE
)

class Particle:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.radius = random.uniform(LEVEL_BG_PARTICLE_RADIUS_RANGE[0], LEVEL_BG_PARTICLE_RADIUS_RANGE[1])
        self.color = random.choice(LEVEL_BG_PARTICLE_COLORS)
        self.base_speed_x = random.uniform(LEVEL_BG_PARTICLE_SPEED_RANGE[0], LEVEL_BG_PARTICLE_SPEED_RANGE[1]) * random.choice([-1, 1])
        self.base_speed_y = random.uniform(LEVEL_BG_PARTICLE_SPEED_RANGE[0], LEVEL_BG_PARTICLE_SPEED_RANGE[1]) * random.choice([-1, 1])
        self.speed_x = self.base_speed_x
        self.speed_y = self.base_speed_y

        # Ensure some minimal movement
        if -0.1 < self.speed_x < 0.1: self.speed_x = 0.1 if self.speed_x >= 0 else -0.1
        if -0.1 < self.speed_y < 0.1: self.speed_y = 0.1 if self.speed_y >= 0 else -0.1

    def update(self, dt, camera_offset_x=0, camera_offset_y=0):
        # Simulate parallax: slower particles move less with camera
        parallax_factor = self.radius / LEVEL_BG_PARTICLE_RADIUS_RANGE[1] # Smaller particles have less parallax (appear further)
        
        self.x += self.speed_x * dt # Particles have their own independent movement
        self.y += self.speed_y * dt

        # Apparent movement due to camera (parallax)
        # This part might be tricky if particles are not tied to world coords
        # For a purely screen-space effect that reacts to camera, it's simpler.
        # Let's assume for now particles are screen-fixed but have their own motion.

        # Wrap around screen edges
        if self.x < -self.radius: self.x = SCREEN_WIDTH + self.radius
        if self.x > SCREEN_WIDTH + self.radius: self.x = -self.radius
        if self.y < -self.radius: self.y = SCREEN_HEIGHT + self.radius
        if self.y > SCREEN_HEIGHT + self.radius: self.y = -self.radius

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))

class Wisp:
    def __init__(self):
        self.points = []
        self.color = random.choice(LEVEL_BG_WISP_COLORS)
        self.max_length = random.randint(LEVEL_BG_WISP_MAX_LENGTH // 2, LEVEL_BG_WISP_MAX_LENGTH)
        self.width = random.randint(LEVEL_BG_WISP_MAX_WIDTH // 2, LEVEL_BG_WISP_MAX_WIDTH)
        self.speed = random.uniform(LEVEL_BG_WISP_SPEED_RANGE[0], LEVEL_BG_WISP_SPEED_RANGE[1])
        self.angle = random.uniform(0, 2 * math.pi) # Radians
        self.current_pos = pygame.math.Vector2(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
        self.angle_change_timer = 0
        self.angle_change_interval = random.uniform(1, 3) # Seconds
        self.target_angle = self.angle

    def update(self, dt):
        self.angle_change_timer += dt
        if self.angle_change_timer > self.angle_change_interval:
            self.target_angle += random.uniform(-0.8, 0.8) # Wider change in direction
            self.angle_change_timer = 0
            self.angle_change_interval = random.uniform(1.5, 3.5)

        # Smoothly turn towards target angle
        angle_diff = (self.target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
        self.angle += angle_diff * 0.05 # Adjust speed of turning (slower for smoother turns)
        self.angle %= (2 * math.pi) # Keep angle within 0-2pi

        # Update position based on new angle
        delta_x = math.cos(self.angle) * self.speed * dt
        delta_y = math.sin(self.angle) * self.speed * dt
        self.current_pos.x += delta_x
        self.current_pos.y += delta_y

        self.points.append(self.current_pos.copy())
        if len(self.points) > self.max_length:
            self.points.pop(0)

        # Wrap around screen edges for the leading point of the wisp
        # This ensures wisps re-enter the screen after exiting
        if self.current_pos.x < -self.width and all(p.x < -self.width for p in self.points):
            self.current_pos.x = SCREEN_WIDTH + self.width
            self.points = [self.current_pos.copy()] # Reset tail to new position
        elif self.current_pos.x > SCREEN_WIDTH + self.width and all(p.x > SCREEN_WIDTH + self.width for p in self.points):
            self.current_pos.x = -self.width
            self.points = [self.current_pos.copy()]
        if self.current_pos.y < -self.width and all(p.y < -self.width for p in self.points):
            self.current_pos.y = SCREEN_HEIGHT + self.width
            self.points = [self.current_pos.copy()]
        elif self.current_pos.y > SCREEN_HEIGHT + self.width and all(p.y > SCREEN_HEIGHT + self.width for p in self.points):
            self.current_pos.y = -self.width
            self.points = [self.current_pos.copy()]

    def draw(self, surface):
        if len(self.points) > 1:
            num_segments = len(self.points) - 1
            for i in range(num_segments):
                start_point = self.points[i]
                end_point = self.points[i+1]
                # Calculate alpha and width based on segment position in the tail
                # Tail gets thinner and more transparent
                segment_ratio = (i + 1) / len(self.points)
                alpha = self.color[3] * segment_ratio
                current_width = max(1, int(self.width * segment_ratio))
                
                if current_width > 0 and alpha > 0:
                    try:
                        pygame.draw.line(surface, (*self.color[:3], int(alpha)), start_point, end_point, current_width)
                    except TypeError as e:
                        print(f"Error drawing wisp line: {e}, color={(*self.color[:3], int(alpha))}, start={start_point}, end={end_point}, width={current_width}")
                        # Fallback if error occurs
                        pass 

class MagicalBackground:
    def __init__(self):
        self.gradient_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._draw_gradient()
        self.particles = [Particle() for _ in range(LEVEL_BG_PARTICLE_COUNT)]
        self.wisps = [Wisp() for _ in range(LEVEL_BG_WISP_COUNT)]
        self.fx_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    def _draw_gradient(self):
        top_color = LEVEL_BG_GRADIENT_TOP
        bottom_color = LEVEL_BG_GRADIENT_BOTTOM
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
            g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
            b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
            pygame.draw.line(self.gradient_surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))

    def update(self, dt, camera_offset=None):
        # camera_offset could be a pygame.math.Vector2, representing how much the camera has moved
        # This can be used for parallax effects if desired.
        # For now, particles and wisps update independently of camera for simplicity.
        # If camera_offset is provided (e.g. camera_offset.x, camera_offset.y):
        # Parallax effect: Adjust particle/wisp positions slightly opposite to camera movement.
        # E.g., particle.x -= camera_offset.x * particle.parallax_factor
        for particle in self.particles:
            particle.update(dt) # Pass camera_offset here if implementing parallax for particles
        for wisp in self.wisps:
            wisp.update(dt) # Wisps are screen-fixed for now

    def draw(self, surface):
        # Draw the pre-rendered gradient
        surface.blit(self.gradient_surface, (0, 0))

        # Clear the fx_surface for redrawing particles and wisps
        self.fx_surface.fill((0,0,0,0)) # Fill with transparent
        for particle in self.particles:
            particle.draw(self.fx_surface)
        for wisp in self.wisps:
            wisp.draw(self.fx_surface)
        
        # Blit the combined FX onto the main surface
        surface.blit(self.fx_surface, (0,0))
