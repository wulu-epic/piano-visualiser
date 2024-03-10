import pygame, math, threading
from modules import Piano

class Scene:
    def __init__(self, scene_name) -> None:
        pygame.init()

        self.screen_width = 1280
        self.screen_height = 720

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()

        self.scene_objects = [] 
        self.scene_name = scene_name
        self.running = True
        

        self.threads = []

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def insert_object(self, object : pygame.Rect):
        self.scene_objects.append(object)
        return self.scene_objects[self.scene_objects.index(object)] # returns a direct reference to the object within the render queue
    
    def remove_object(self, object):
        self.scene_objects.remove(object)

    def clean(self):
        for thread in self.threads:
            t : threading.Thread = thread
            if not t.isDaemon() and t.is_alive():
                t.join()
                
        pygame.quit()

    def order_draw_order_by_z_index(self):
        pass # Shape class will contain Z-index value, before starting to draw, we sort it by the z index, low to high (lower values get drawn first)

    def fill_scene(self, objects):
        for obj in objects:
            self.insert_object(obj)

    def run(self, custom_functions):  
        while self.running:
            self.handle_events()
            self.screen.fill((30,30,30))

            for item in custom_functions:
                if len(item) == 2:
                    #Custom arguement functionality TODO will have to setup a more modular system for this later.
                    void, arg = item
                    if arg is not None and type(arg) is Piano.PianoVisualiser and not arg.visualisation_running:
                        thread = threading.Thread(target=void, args=(arg,), daemon=True)
                        thread.start()

                        self.threads.append(thread)
                else:
                    void = item[0]
                    thread = threading.Thread(target=void, daemon=True)
                    thread.start()
                    
                    self.threads.append(thread)
                        
            for object in self.scene_objects:
                object.draw(self.screen)

            pygame.display.set_caption(f"{self.scene_name} FPS: {math.ceil(self.clock.get_fps())} OBJECTS: {len(self.scene_objects)}") 
            pygame.display.flip()
            self.clock.tick(360)

        self.clean()