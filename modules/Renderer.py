import pygame, math, threading

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

    def clean(self):
        for thread in self.threads:
            t : threading.Thread = thread
            if not t.isDaemon() and t.is_alive():
                t.join()
                
        pygame.quit()

    def fill_scene(self, objects):
        for obj in objects:
            self.insert_object(obj)

    def run(self, custom_functions):        
        while self.running:
            self.handle_events()
            self.screen.fill((30,30,30))

            for void, arg in (custom_functions):
                thread = threading.Thread(target=void,  args=(arg,), daemon=True)
                thread.start()
                self.threads.append(thread)
                    
            for object in self.scene_objects:
                object.draw(self.screen)

            pygame.display.set_caption(f"{self.scene_name} FPS: {math.ceil(self.clock.get_fps())}") 
            pygame.display.flip()
            self.clock.tick(0)

        self.clean()
