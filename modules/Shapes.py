import pygame
import random
from pygame.math import Vector2

class Shape:
    def __init__(self, position : pygame.Vector2, size, colour):
        self.position : pygame.Vector2 = pygame.Vector2(position)
        self.size = size

        self.object = None
        self.root = False

        self.colour = colour
        self.original_colour = self.colour
        self.ID = random.randint(0, 256*128)
        self.border_radius = 0

    def draw(self, surface):
        return self.object
    
class Square(Shape):
    def __init__(self, position: Vector2, size: Vector2, colour):
        super().__init__(position, size, colour)

    def draw(self, surface):
        self.object = pygame.draw.rect(surface, self.colour, (*self.position, *self.size))
        return self.object, self.size, self.colour

class Circle(Shape):
    def __init__(self, position : pygame.Vector2, radius, colour):
        super().__init__(position, radius, colour)

    def draw(self, surface):
        self.object = pygame.draw.circle(surface, self.colour, (int(self.position.x), int(self.position.y)), self.size)
        return self.object, self.size, self.colour
