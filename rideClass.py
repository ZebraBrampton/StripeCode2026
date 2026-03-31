import pygame
from os import environ

class RideWindow:
    def __init__(self, caption, size, pos, queue, logs):
        self.caption = caption
        self.size = size
        self.pos = pos
        self.queue = queue
        self.logs = logs

        self.running = True
        self.FPS = 60

        environ['SDL_VIDEO_WINDOW_POS'] = f"{pos[0]}, {pos[1]}"

        pygame.init()

        self.window = pygame.display.set_mode(self.size)

        pygame.display.set_caption(self.caption)

        self.font = pygame.font.SysFont("Arial", 18, bold=True)

        self.clock = pygame.time.Clock()


        self.curr_station = "N/A"
        self.curr_hour = 0
        self.wait_sold = None
        self.joy_sales = None
        self.alert = None

    
    def findData(self, name, hour):
        if (hour, name) in self.logs:
            self.wait_sold = self.logs[(hour, name)][0]
            self.joy_sales = self.logs[(hour, name)][1]

    
    def draw_text(self, text, colour, text_pos):
        text_surface = self.font.render(text, True, colour)
        text_rect = text_surface.get_rect(center=text_pos)
        self.window.blit(text_surface, text_rect)


    def draw(self):
        # Background screen
        self.window.fill((0, 0, 0))

        # Draw the current station
        self.draw_text(f"Current Station: {self.curr_station}", (255, 255, 255), (self.size[0] // 2, self.size[1] // 5))
        
        # Draw the current hour
        self.draw_text(f"Current Hour: {self.curr_hour}", (255, 255, 255), (self.size[0] // 2, self.size[1] // 4))
        
        
        self.draw_text(f"Current : {self.wait_sold}", (255, 255, 255), (self.size[0] // 2, self.size[1] // 3))
        
        self.draw_text(f"Current : {self.joy_sales}", (255, 255, 255), (self.size[0] // 2, self.size[1] // 2))


        

    def events(self):

        while not self.queue.empty():
            
            try:
                msg = self.queue.get_nowait()

                if msg == "QUIT":
                    self.running = False

                elif type(msg) == int:
                    self.curr_hour = msg
                
                else:
                    self.curr_station = msg

            finally: # Incase an error comes along the way
                pass

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                self.running = False
            




    def update(self):

        self.findData(self.curr_station, str(self.curr_hour))

        pygame.display.flip()

        self.clock.tick(self.FPS)


    def run(self):

        while self.running:

            self.draw()

            self.events()

            self.update()
        
        pygame.quit()