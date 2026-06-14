import pygame
from os import environ

from initialization import config

class RideWindow:
    def __init__(self, caption, size, pos, queue_in, queue_out, random_data, given_data):
        self.caption = caption # Title of the window
        self.size = size # Size of the window
        self.pos = pos # Position of the window on the screen
        self.queue_in = queue_in # The pipeline that recieves messages
        self.queue_out = queue_out # The pipeline that sends out messages
        self.random_data = random_data
        self.given_data = given_data

        self.main_log = None

        # Initialize variables for the window
        self.running = True
        self.FPS = 60

        # Set the window position using the environment variable from the os module
        environ['SDL_VIDEO_WINDOW_POS'] = f"{pos[0]}, {pos[1]}"

        # Initialize pygame and create the window, font, clock and overlay
        pygame.init()

        self.window = pygame.display.set_mode(self.size)

        pygame.display.set_caption(self.caption)

        self.font = pygame.font.SysFont("Arial", 18, bold=True)

        self.clock = pygame.time.Clock()

        self.overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 100))

        # Variables for data
        self.curr_station = "N/A" # Current station
        self.curr_hour = config['simulation']['startHour'] # Starting hour
        
        # Store current ride statuses
        self.ride_statuses = {}

        # Background colour of the window
        self.background_colour = (0, 0, 0)

        # Audio initialization - fix sound effect
        self.fixSFX = pygame.mixer.Sound("International/Audio/FixSFX.mp3")

    def draw_text(self, text, colour, text_pos): # Creates and draws text onto the screen
        text_surface = self.font.render(text, True, colour) # Render the text with the given colour
        text_rect = text_surface.get_rect(center=text_pos) # Get the rectangle of the text surface and set its center to the given text position
        self.window.blit(text_surface, text_rect) # Draw the text surface onto the window at the position of the text rectangle

    def draw_bg(self): # Draws the background
        self.window.fill(self.background_colour) # Fill the background with the current background colour

        self.window.blit(self.overlay, (0, 0)) # Draw the semi-transparent overlay on top of the background

    def weatherUpdate(self):
        weather_values = self.main_log[self.curr_hour]['weather_values']
        self.ride_statuses = self.main_log[self.curr_hour]['rides']

        # Combine weather and ride states
        data_packet = {
            'weather': weather_values,
            'rides': self.ride_statuses
        }

        self.queue_out.put(data_packet)


    def draw(self): # Main drawing function that calls other drawing functions
        # Background screen
        self.draw_bg()
        
        # Draw the current hour
        self.draw_text(f"Current Hour: {self.curr_hour}:00", (255, 255, 255), (self.size[0] // 2, 40))

        # Show current station
        self.draw_text(f"Current Station: {self.curr_station}", (255, 255, 255), (self.size[0] // 2, 100))
        
        IMPACT_COLORS = {
            "FULL": (0, 255, 0),    # Green
            "SLOW": (255, 255, 0),  # Yellow
            "STOP": (255, 0, 0)     # Red
            }
        
        current_impact = self.ride_statuses.get(self.curr_station, "FULL")
        impact_color = IMPACT_COLORS.get(current_impact, (255, 0, 0))

        self.draw_text(f"Current Impact: {current_impact}", impact_color, (self.size[0] // 2, 140))

        # Header for listing the stats
        self.draw_text("--- Current Statistics ---", (200, 200, 200), (self.size[0] // 2, 220))
        
        y_pos = 260
        colors = {"FULL": (0, 255, 0), 
                  "SLOW": (255, 255, 0)}

        for ride, status in self.ride_statuses.items():
            color = colors.get(status, (255, 0, 0))
            self.draw_text(f"{ride}: {status}", color, (self.size[0] // 2, y_pos))
            y_pos += 40

    def events(self): # Checks if user wants to quit pygame

        for event in pygame.event.get(): # Checks all pygame events

            if event.type == pygame.QUIT: # Check if user clicks the "X" button to close the window

                self.queue_out.put("QUIT") # Send a message to quit the program
                self.running = False # Stop running the window loop to close the window

    def update(self): # Updates the current stats of the simulation
        
        try:
            msg = self.queue_in.get_nowait() # Grabs the most recent message in queue

            if msg == "QUIT": # If message recieved is to quit the program
                self.running = False # Stop running the window loop to close the window

            elif type(msg) == int: # If the message is an integer
                self.curr_hour = msg # Update the current hour
                self.weatherUpdate()
            
            elif msg.startswith("run_"):
                if msg == "run_GIVEN":
                    self.main_log = self.given_data
                else:
                    self.main_log = self.random_data
            
            elif msg.startswith("S:"): # If the message starts with "S:"
                self.curr_station = msg[2:].split("_")[0] # Update the current station
                self.background_colour = (msg[2:].split("_")[1].strip("()").split(",")) # Update the background colour (contained as str)
                self.background_colour = tuple(int(x.strip()) for x in self.background_colour) # Converts all iterable values into a tuple

            elif msg == "RESTART": # If the message is to restart the simulation
                self.curr_station = "N/A" # Reset current station
                self.curr_hour = 10 # Reset current hour
                self.wait_sold = None # Reset wait time/items sold
                self.station_type = None # Reset station type
                self.joy_sales = None # Reset guest satisfaction/sales amount
                self.alert_stations = [] # Reset list of stations that are having issues
    
        except: # If no messages are in queue, it will cause an error, this except: after the try: is used to ignore the error and continue running the program
            pass # Pass statement to just ignore and move on 

        # Update the display
        pygame.display.flip()

        # Cap the frame rate to 60 FPS
        self.clock.tick(self.FPS)

    def run(self): # Main running loop

        while self.running: # When self.running is True, this window loop will continue to run and keep the window open
            
            # Main drawing function that calls other drawing functions to draw the current screen
            self.draw()

            # Checks for any events such as user trying to quit the program or messages from the main window
            self.events()

            # Updates current stats of the simulation
            self.update()
        
        pygame.quit() # Quit pygame when the window loop is no longer running