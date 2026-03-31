import pygame
from os import environ

from imageClass import Image

class ParkWindow:
    SIMULATIONHOUR = 1000 * 10 # One simulation hour is 10 seconds (10,000ms)
    STARTTIME = 11 # Start clock at 10:00 AM
    ENDTIME = 21 # End clock at 9:00 PM

    def __init__(self, caption, size, pos, queue, images):
        self.caption = caption
        self.size = size
        self.pos = pos
        self.queue = queue
        self.images = images
        
        self.running = True
        self.FPS = 60

        environ['SDL_VIDEO_WINDOW_POS'] = f"{pos[0]}, {pos[1]}"

        pygame.init()

        self.window = pygame.display.set_mode(self.size)

        pygame.display.set_caption(self.caption)

        self.font = pygame.font.SysFont("Arial", 18, bold=True)

        self.clock = pygame.time.Clock()

        self.time_text = "00:00"
        self.total_sim_hours = 0
        self.total_paused_time = 0
        self.prev_hour = self.STARTTIME
        self.queue.put(self.prev_hour)


    def initImages(self):
        for ride in self.images:
            self.images[ride] = Image(*self.images[ride])

    
    def draw_text(self, text, colour, text_pos):
        text_surface = self.font.render(text, True, colour)
        text_rect = text_surface.get_rect(center=text_pos)
        self.window.blit(text_surface, text_rect)


    def draw(self):
        self.window.fill((200, 200, 200))

        # Draw stations and rides
        for ride in self.images:
            if self.images[ride].draw(self.window):
                self.queue.put(ride)
        
        # Draw timer
        self.draw_text(self.time_text, (0, 0, 0), (100, 100))



    def confirm_exit(self):
        overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        
        # Draw the overlay onto the main window
        self.window.blit(overlay, (0, 0))
        
        # Draw confirmation text on top of the overlay
        self.draw_text("Are you sure you want to exit? Press Y or N", (255, 255, 255), (self.size[0] // 2, self.size[1] // 2))
        
        # Force the display to update so the user actually sees the overlay
        pygame.display.flip()
        
        # Wait for the user's response
        waiting = True
        self.initial_paused_time = pygame.time.get_ticks()

        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True # If they click the window's X again, force quit
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        self.queue.put("QUIT") # Put "QUIT" into communication pipe so second window (if open) will close
                        return True  # Yes, exit the program
                    
                    elif event.key == pygame.K_n:
                        self.final_paused_time = pygame.time.get_ticks()

                        self.total_paused_time += (self.final_paused_time - self.initial_paused_time)
                        return False # No, return to the main loop
        return False


    def events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                
                if self.confirm_exit():
                    self.running = False
                
        if self.total_sim_hours >= self.ENDTIME:
            self.running = False
        

    def sim_time(self):
        # Get the current elapsed time
        start_offset_ms = self.STARTTIME * self.SIMULATIONHOUR
        
        total_milis = pygame.time.get_ticks() + start_offset_ms - self.total_paused_time
        
        # Calculate the simulation time
        self.total_sim_hours = total_milis / self.SIMULATIONHOUR

        # Use 24-hour clock
        hour = int(self.total_sim_hours) % 24
        minute = int((self.total_sim_hours * 60) % 60)

        self.time_text = f"{hour:02}:{minute:02}"

        if self.prev_hour != hour:
            self.queue.put(hour)
        
        self.prev_hour = hour
        

    def update(self):
        
        self.sim_time()

        pygame.display.flip()

        self.clock.tick(self.FPS)


    def run(self):
        
        self.initImages()

        while self.running:

            self.draw()

            self.events()

            self.update()
        
        pygame.quit()