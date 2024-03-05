import random, pygame
from modules.Shapes import *

class ObjectManager:
    def __init__(self):
        self.objects = []

    def insert(self, object):
        self.objects.append(object)
    
    def remove_object(self, object):
        for other_object in self.objects:
            if other_object.ID == object.ID:
                self.objects.remove(other_object)
                return True  
        return False
    
    def objects_to_rect(self, surface):
        e = []
        for object in self.objects:
            shape, radius, colour = object.draw(surface)
            e.append([shape, radius, colour])
        return e
     
    def populate(self, amount : int, custom_func = None):
        if custom_func != None:
            self.objects += custom_func()
            return
           
        # This is just like a hello world.
        for _ in range(0, amount + 1):
            obj = Square(pygame.Vector2(1280/2 + random.randint(-100, 100),720/2 + random.randint(-100, 100)), 50, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
            self.insert(obj)

    def clear_objects(self):
        self.objects = []
