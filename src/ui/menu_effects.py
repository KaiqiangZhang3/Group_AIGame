import pygame
import random
import math
from src.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, 
    GRADIENT_TOP_COLOR, GRADIENT_BOTTOM_COLOR,
    FIREFLY_COLOR, FIREFLY_GLOW_COLOR, MINIMAL_MENU_GLOW_COLOR, 
    BACKGROUND_GLOBAL_DRIFT_X, MIST_PARALLAX_FACTOR, FIREFLY_PARALLAX_FACTOR 
)

class MistParticle:
    """Represents a single particle for the mist/fog effect."""
    def __init__(self):
        self.world_x = random.randint(0, SCREEN_WIDTH) 
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(15, 40) 
        self.speed_x = random.uniform(-0.2, 0.2) 
        self.speed_y = random.uniform(-0.1, 0.1)
        base_mist_color = MINIMAL_MENU_GLOW_COLOR[:3] 
        self.alpha = random.randint(10, 40) 
        self.color = (*base_mist_color, self.alpha)
        self.age = 0

    def update(self, dt, global_drift_x):
        self.world_x += self.speed_x * dt * 60 
        self.y += self.speed_y * dt * 60
        
        self.screen_x = self.world_x - global_drift_x * MIST_PARALLAX_FACTOR

        if self.screen_x < -self.size: 
            self.world_x += SCREEN_WIDTH + self.size * 2 
        if self.screen_x > SCREEN_WIDTH + self.size: 
            self.world_x -= (SCREEN_WIDTH + self.size * 2)
        if self.y < -self.size: self.y = SCREEN_HEIGHT + self.size
        if self.y > SCREEN_HEIGHT + self.size: self.y = -self.size

    def draw(self, surface):
        particle_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, self.color, (self.size, self.size), self.size)
        surface.blit(particle_surf, (int(self.screen_x - self.size), int(self.y - self.size)))

class FireflyParticle:
    """Represents a magical firefly particle."""
    def __init__(self):
        self.world_x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.base_size = random.uniform(1.5, 3) 
        self.size = self.base_size
        self.color = FIREFLY_COLOR
        self.glow_color = FIREFLY_GLOW_COLOR
        self.glow_size_factor = 3.0
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(0.3, 0.8)
        self.drift_speed_x_intrinsic = random.uniform(-0.2, 0.2) 
        self.drift_speed_y_intrinsic = random.uniform(-0.2, 0.2) 
        self.pulse_speed = random.uniform(0.5, 1.5) 
        self.pulse_timer = random.uniform(0, 2 * math.pi / self.pulse_speed)
        self.pulse_amplitude = random.uniform(0.3, 0.7)

    def update(self, dt, global_drift_x):
        self.world_x += (math.cos(self.angle) * self.speed + self.drift_speed_x_intrinsic) * dt * 60
        self.y += (math.sin(self.angle) * self.speed + self.drift_speed_y_intrinsic) * dt * 60
        self.angle += random.uniform(-0.1, 0.1) * dt * 60

        self.screen_x = self.world_x - global_drift_x * FIREFLY_PARALLAX_FACTOR

        effective_wrap_width = SCREEN_WIDTH + self.base_size * self.glow_size_factor * 2
        if self.screen_x < -self.base_size * self.glow_size_factor : 
            self.world_x += effective_wrap_width
        if self.screen_x > SCREEN_WIDTH + self.base_size * self.glow_size_factor: 
            self.world_x -= effective_wrap_width
        if self.y < -self.base_size * self.glow_size_factor: 
            self.y = SCREEN_HEIGHT + self.base_size * self.glow_size_factor
        if self.y > SCREEN_HEIGHT + self.base_size * self.glow_size_factor: 
            self.y = -self.base_size * self.glow_size_factor

        self.pulse_timer += dt
        pulse_factor = 1.0 + math.sin(self.pulse_timer * self.pulse_speed) * self.pulse_amplitude
        self.size = self.base_size * pulse_factor

    def draw(self, surface):
        glow_radius = int(self.size * self.glow_size_factor)
        if glow_radius > 0:
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, self.glow_color, (glow_radius, glow_radius), glow_radius)
            surface.blit(glow_surf, (int(self.screen_x - glow_radius), int(self.y - glow_radius)), special_flags=pygame.BLEND_RGBA_ADD)

        core_radius = int(self.size)
        if core_radius > 0:
            pygame.draw.circle(surface, self.color, (int(self.screen_x), int(self.y)), core_radius)

class MenuBackgroundAnimator:
    def __init__(self, num_mist_particles=50, num_fireflies=25):
        self.mist_particles = [MistParticle() for _ in range(num_mist_particles)]
        self.fireflies = [FireflyParticle() for _ in range(num_fireflies)]
        self.gradient_render_width = SCREEN_WIDTH + 200 
        self.gradient_surface = self._create_gradient_surface(self.gradient_render_width)
        self.global_offset_x = 0.0

    def _create_gradient_surface(self, width):
        gradient_surf = pygame.Surface((width, SCREEN_HEIGHT))
        top_color = GRADIENT_TOP_COLOR
        bottom_color = GRADIENT_BOTTOM_COLOR
        for y in range(SCREEN_HEIGHT):
            r = top_color[0] + (bottom_color[0] - top_color[0]) * y / SCREEN_HEIGHT
            g = top_color[1] + (bottom_color[1] - top_color[1]) * y / SCREEN_HEIGHT
            b = top_color[2] + (bottom_color[2] - top_color[2]) * y / SCREEN_HEIGHT
            pygame.draw.line(gradient_surf, (int(r), int(g), int(b)), (0, y), (width, y))
        return gradient_surf

    def update(self, dt):
        self.global_offset_x += BACKGROUND_GLOBAL_DRIFT_X * dt * 60
        if self.global_offset_x > self.gradient_render_width - SCREEN_WIDTH:
            self.global_offset_x = 0
        elif self.global_offset_x < 0:
             self.global_offset_x = self.gradient_render_width - SCREEN_WIDTH

        for particle in self.mist_particles:
            particle.update(dt, self.global_offset_x)
        for firefly in self.fireflies:
            firefly.update(dt, self.global_offset_x)

    def draw(self, surface):
        surface.blit(self.gradient_surface, (0,0), (self.global_offset_x, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        for particle in self.mist_particles:
            particle.draw(surface)
        
        for firefly in self.fireflies:
            firefly.draw(surface) 
