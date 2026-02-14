import pygame
import random
import math

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(3, 8)
        self.lifetime = 1.0
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, 4)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= dt
        self.size = max(0, self.size - dt * 5)
        return self.lifetime > 0

    def draw(self, screen):
        alpha = int(self.lifetime * 255)
        # Handle alpha if surface supports it, or just draw
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

class EffectManager:
    def __init__(self):
        self.particles = []
        self.shake_amount = 0
        self.shake_duration = 0

    def create_burst(self, x, y, color=(255, 215, 0), count=20):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def trigger_shake(self, amount, duration):
        self.shake_amount = amount
        self.shake_duration = duration

    def update(self, dt):
        # Update particles
        self.particles = [p for p in self.particles if p.update(dt)]
        
        # Update shake
        if self.shake_duration > 0:
            self.shake_duration -= dt
        else:
            self.shake_amount = 0

    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)

    def get_shake_offset(self):
        if self.shake_duration > 0:
            return (random.randint(-self.shake_amount, self.shake_amount),
                    random.randint(-self.shake_amount, self.shake_amount))
        return (0, 0)
