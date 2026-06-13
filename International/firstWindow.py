import pygame
from os import environ

from rideClass import Rides

class ParkWindow:

    def __init__(self, caption, size, pos, queue_in, queue_out, images): # Initialize all variables for main window
        self.caption = caption
        self.size = size
        self.pos = pos
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.images = images
        
        self.running = True
        self.FPS = 60
        
        environ['SDL_VIDEO_WINDOW_POS'] = f"{pos[0]}, {pos[1]}" # Change the position of window

        pygame.init() # Initialize pygame and all its modules

        self.window = pygame.display.set_mode(self.size) # Create the main window with the specified size

        pygame.display.set_caption(self.caption) # Set the caption of the window to the specified caption

        self.font = pygame.font.SysFont("Arial", 18, bold=True) # Create a font object to use for drawing text

        self.clock = pygame.time.Clock() # Create a clock object to control the frame rate of the simulation

        self.overlay = pygame.Surface(self.size, pygame.SRCALPHA) # Create a transparent surface to use as an overlay for pause and confirmation screens
        self.overlay.fill((0, 0, 0, 180)) # Fill the overlay with a semi-transparent black color (the last value is the alpha channel for transparency)

        # Initialize variables for time tracking
        self.time_text = "00:00"
        self.total_sim_hours = 0
        self.total_paused_time = 0
        self.prev_hour = self.STARTTIME
        self.queue_out.put(self.prev_hour)

        # Initialize Images
        for ride in self.images:
            self.images[ride] = Rides(*self.images[ride])

        # Audio initialization
        pygame.mixer.music.load("Audio/BGM.mp3")
        pygame.mixer.music.set_volume(0.5)

        self.pauseSFX = pygame.mixer.Sound("Audio/PauseSFX.mp3")
        self.restartSFX = pygame.mixer.Sound("Audio/RestartSFX.mp3")
        self.exitSFX = pygame.mixer.Sound("Audio/ExitSFX.mp3")

    def draw_text(self, text, colour, text_pos): # Creates and draws text onto the screen
            text_surface = self.font.render(text, True, colour)
            text_rect = text_surface.get_rect(center=text_pos)
            self.window.blit(text_surface, text_rect)

    def startGame(self): # Waits for user to input any key to begin simulation
        # Draw the overlay onto the main window
        self.window.blit(self.overlay, (0, 0))

        # Draw welcome text on top of the overlay
        self.draw_text("Welcome to the Theme Park Simulator! Press any key to start.", (255, 255, 255), (self.size[0] // 2, self.size[1] // 2))

        # Force the display to update so the user actually sees the overlay
        pygame.display.flip()

        waiting = True # Wait for the user to press a key to start the simulation

        self.initial_paused_time = pygame.time.get_ticks() # Start counting paused time until the user presses a key to start the simulation so that the paused time will not be included in the simulation time calculation

        # Event loop to wait for user input
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: # If the user clicks the window's X
                    waiting = False
                    self.queue_out.put("QUIT") # Put "QUIT" into communication pipe so second window will close
                    self.running = False
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN: # If user presses any key or clicks the mouse button
                    waiting = False
        
        # Take the final paused time after the user presses a key
        self.final_paused_time = pygame.time.get_ticks()

        # Calculate the total paused time and add it to the total_paused_time variable
        self.total_paused_time += (self.final_paused_time - self.initial_paused_time)

    def draw(self): # Main drawing function to call other drawing functions
            self.window.fill((200, 200, 200))

    def run(self): # Main running loop

            self.startGame()

            pygame.mixer.music.play(-1) # Play the background music in a loop (-1 means it will loop infinetly)

            while self.running:

                self.draw()

                self.events()

                self.update()
            
            pygame.quit()