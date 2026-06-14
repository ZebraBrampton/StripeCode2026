import pygame
from os import environ

from rideClass import Rides
from initialization import config

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
        self.STARTTIME = config['simulation']['startHour']
        self.ENDTIME = config['simulation']['endHour']

        self.SIMULATIONHOUR = config['simulation']['realTimeInterval'] * 1000
        self.prev_hour = self.SIMULATIONHOUR
        self.queue_out.put(self.prev_hour)

        # Weather variables
        self.rain = 0
        self.wind = 0
        self.temp = 0

        # Initialize Images
        for ride in self.images:
            self.images[ride] = Rides(*self.images[ride])
        
        # Audio initialization
        pygame.mixer.music.load("International/Audio/BGM.mp3")
        pygame.mixer.music.set_volume(0.5)

        self.pauseSFX = pygame.mixer.Sound("International/Audio/PauseSFX.mp3")
        self.restartSFX = pygame.mixer.Sound("International/Audio/RestartSFX.mp3")
        self.exitSFX = pygame.mixer.Sound("International/Audio/ExitSFX.mp3")

    def update_weather(self, conditions): # Updates weather stats at given hour
        self.rain = conditions['rain']
        self.wind = conditions['wind']
        self.temp = conditions['temp']

    def draw_text(self, text, colour, text_pos): # Creates and draws text onto the screen
            text_surface = self.font.render(text, True, colour)
            text_rect = text_surface.get_rect(center=text_pos)
            self.window.blit(text_surface, text_rect)

    def draw_weather_icons(self): # Draws all weather icons according to their respective thresholds
        # Find temp impact
        if self.temp <= 25:
            temp_icon = "Low Temp"
        elif self.temp <= 32:
            temp_icon = "Moderate Temp"
        else:
            temp_icon = "High Temp"

        # Find wind speed impact
        if self.wind <= 20:
            wind_icon = "Low Wind"
        elif self.wind <= 40:
            wind_icon = "Moderate Wind"
        else:
            wind_icon = "Heavy Wind"

        # Find rain impact
        if self.rain <= 3:
            rain_icon = "Low Rain"
        elif self.rain <= 6:
            rain_icon = "Moderate Rain"
        else:
            rain_icon = "Heavy Rain"

        # Find simulation hour icon
        current_hour = int(self.total_sim_hours) % 24
        if current_hour < 12:
            time_icon = "Morning"
        elif current_hour < 17:
            time_icon = "Afternoon"
        else:
            time_icon = "Evening"

        # Display icons
        self.window.blit(self.images[temp_icon].image, self.images[temp_icon].rect.topleft)
        self.window.blit(self.images[wind_icon].image, self.images[wind_icon].rect.topleft)
        self.window.blit(self.images[rain_icon].image, self.images[rain_icon].rect.topleft)
        self.window.blit(self.images[time_icon].image, self.images[time_icon].rect.topleft)

        # Display values of each condition
        self.draw_text(f"{self.temp} °C", (0, 0, 0), (120, 120))
        self.draw_text(f"{self.wind} km/hr", (0, 0, 0), (120, 185))
        self.draw_text(f"{self.rain} mm/hr", (0, 0, 0), (120, 240))

    def startGame(self): # Waits for user to click 'Begin' or press any key to start simulation
        # Define colors
        CREAM = (249, 242, 218)
        BLACK = (0, 0, 0)
        BRIGHT_GREEN = (0, 255, 0)
        PURPLE_TEXT = (128, 0, 128)
        SUBTITLE_GRAY = (100, 100, 100)

        # Create more fonts
        title_font = pygame.font.SysFont("Georgia", 56, bold=True)
        subtitle_font = pygame.font.SysFont("Arial", 18, italic=True)
        button_font = pygame.font.SysFont("Arial", 20, bold=True)

        # Set up button dimensions and placement
        btn_width, btn_height = 200, 65
        btn_x = (self.size[0] // 2) - (btn_width // 2)
        btn_y = int(self.size[1] * 0.65)  # Positions button at ~65% down the window height
        begin_button_rect = pygame.Rect(btn_x, btn_y, btn_width, btn_height)

        waiting = True
        self.initial_paused_time = pygame.time.get_ticks()

        # Menu Loop
        while waiting:
            
            self.window.fill(CREAM)

            # 2. Render and draw the main Title text
            title_surf1 = title_font.render("RIDE RUSH", True, BLACK)
            title_surf2 = title_font.render("SIMULATION", True, BLACK)
            
            title_rect1 = title_surf1.get_rect(center=(self.size[0] // 2, int(self.size[1] * 0.22)))
            title_rect2 = title_surf2.get_rect(center=(self.size[0] // 2, int(self.size[1] * 0.36)))
            
            self.window.blit(title_surf1, title_rect1)
            self.window.blit(title_surf2, title_rect2)

            # 3. Render and draw the sub-slogan phrase
            sub_text = "It's so good it will knock your socks off!!!"
            sub_surf = subtitle_font.render(sub_text, True, SUBTITLE_GRAY)
            sub_rect = sub_surf.get_rect(center=(self.size[0] // 2, int(self.size[1] * 0.50)))
            self.window.blit(sub_surf, sub_rect)

            # 4. Draw the interactive Green Button rectangle
            pygame.draw.rect(self.window, BRIGHT_GREEN, begin_button_rect)

            # 5. Render and draw the "Begin" text centered perfectly inside the green box
            btn_surf = button_font.render("Begin", True, PURPLE_TEXT)
            btn_rect = btn_surf.get_rect(center=begin_button_rect.center)
            self.window.blit(btn_surf, btn_rect)

            # Flip the frame display buffer
            pygame.display.flip()

            # Event processing loop inside menu stage
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.queue_out.put("QUIT")
                    self.running = False
                
                # Check for keyboard press standard fallback
                if event.type == pygame.KEYDOWN:
                    waiting = False
                
                # Check for explicit mouse click interaction target matching the green box bounds
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left mouse click
                        if begin_button_rect.collidepoint(event.pos):
                            waiting = False

            # Lock the execution frame rate while idling in the start menu
            self.clock.tick(self.FPS)
        
        # Calculate the final accumulated offset for the backend data clock simulation engine
        self.final_paused_time = pygame.time.get_ticks()
        self.total_paused_time += (self.final_paused_time - self.initial_paused_time)

    def chooseRunType(self): # Prompts the user to select their data generation method
        
        # Define colours
        CREAM = (249, 242, 218)
        BLACK = (0, 0, 0)
        BRIGHT_GREEN = (0, 255, 0)
        BRIGHT_RED = (255, 0, 0)
        PURPLE_TEXT = (128, 0, 128)
        SUBTITLE_GRAY = (80, 80, 80)

        # Initialize fonts
        title_font = pygame.font.SysFont("Georgia", 72, bold=True)
        subtitle_font = pygame.font.SysFont("Georgia", 20, bold=True) 
        button_font = pygame.font.SysFont("Arial", 20, bold=True)

        # Initialize text surfaces
        title_surf = title_font.render("Run Type", True, BLACK)
        sub_surf = subtitle_font.render("Do you wish to run randomly generated values or given values?", True, SUBTITLE_GRAY)
        
        btn_random_surf = button_font.render("Random", True, PURPLE_TEXT)
        btn_given_surf = button_font.render("Given", True, PURPLE_TEXT)

        # Define the buttons rect
        center_x = self.size[0] // 2
        
        # Text Rects
        title_rect = title_surf.get_rect(center=(center_x, int(self.size[1] * 0.20)))
        sub_rect = sub_surf.get_rect(center=(center_x, int(self.size[1] * 0.50)))

        # Button Rects (Stacked vertically)
        btn_width, btn_height = 240, 65
        btn_start_y = int(self.size[1] * 0.65)
        btn_spacing = 20 # Gap between the two buttons
        
        random_button_rect = pygame.Rect(center_x - (btn_width // 2), btn_start_y, btn_width, btn_height)
        given_button_rect = pygame.Rect(center_x - (btn_width // 2), btn_start_y + btn_height + btn_spacing, btn_width, btn_height)
        
        # Center the text inside their respective buttons
        btn_random_text_rect = btn_random_surf.get_rect(center=random_button_rect.center)
        btn_given_text_rect = btn_given_surf.get_rect(center=given_button_rect.center)

        # Main loop
        waiting = True
        choice = None
        self.initial_paused_time = pygame.time.get_ticks()

        while waiting:
            # Draw Background
            self.window.fill(CREAM)

            # Draw Heading Texts
            self.window.blit(title_surf, title_rect)
            self.window.blit(sub_surf, sub_rect)

            # Draw Random Button (Green) & Text
            pygame.draw.rect(self.window, BRIGHT_GREEN, random_button_rect)
            self.window.blit(btn_random_surf, btn_random_text_rect)

            # Draw Given Button (Red) & Text
            pygame.draw.rect(self.window, BRIGHT_RED, given_button_rect)
            self.window.blit(btn_given_surf, btn_given_text_rect)

            # Update Display Buffer
            pygame.display.flip()

            # Event Processing
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.queue_out.put("QUIT")
                    self.running = False
                    return "QUIT"
                
                # Explicit Mouse Click Logic for Both Buttons
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left mouse click
                        if random_button_rect.collidepoint(event.pos):
                            choice = "RANDOM"
                            waiting = False
                        elif given_button_rect.collidepoint(event.pos):
                            choice = "GIVEN"
                            waiting = False

            # Lock Frame Rate
            self.clock.tick(self.FPS)
        
        # --- 6. Exit Menu Time Calculation ---
        self.final_paused_time = pygame.time.get_ticks()
        self.total_paused_time += (self.final_paused_time - self.initial_paused_time)
        
        return f"run_{choice}"

    def draw(self): # Main drawing function to call other drawing functions
        self.window.fill((200, 200, 200))

        # Draw stations and rides
        for ride in self.images:

            if self.images[ride].draw(self.window):
                self.queue_out.put(f"S:{ride}_{self.images[ride].colour}") 
            
        # Draw timer
        self.draw_text(self.time_text, (0, 0, 0), (120, 45))

        # Draw weather conditions
        self.draw_weather_icons()

        # Draw pause button
        self.draw_pause_button()

    def restart(self): # Restarts program by resetting all variables
        self.time_text = "00:00" # Reset time text
        self.total_paused_time = pygame.time.get_ticks() # Reset total paused time
        self.prev_hour = self.STARTTIME # Reset previous hour to the start time
        self.queue_out.put(self.prev_hour) # Send message to second window to reset its display to the default screen
        self.rain = 0
        self.wind = 0
        self.temp = 0

        pygame.mixer.music.play(-1) # Restart the background music in a loop (-1 means it will loop infinetly)

    def confirm_restart(self): # Checks if user wants to restart the simulation at the end
        
        # Draw the overlay onto the main window
        self.window.blit(self.overlay, (0, 0))
        
        # Draw confirmation text on top of the overlay
        self.draw_text("GAME OVER - Do you wish to restart? Press 'Y' (Yes) or 'N' (No)", (255, 255, 255), (self.size[0] // 2, self.size[1] // 2))
        
        # Force the display to update so the user actually sees the overlay
        pygame.display.flip()
        
        # Wait for the user's response
        waiting = True

        pygame.mixer.music.stop() # Stop the background music when the simulation is over

        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True # If they click the window's X again, force quit
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        self.queue_out.put("RESTART") # Put "RESTART" into communication pipe so second window will reset its data and return to default screen
                        self.restartSFX.play() # Play the restart sound effect when the simulation is over
                        return True  # Yes, restart the program
                    
                    elif event.key == pygame.K_n:
                        return False # No, return to the main loop
        return False

    def confirm_exit(self): # Prompts the user to confirm their choice of exitting
        
        # Define colours
        CREAM = (249, 242, 218)
        BLACK = (0, 0, 0)
        BRIGHT_GREEN = (0, 255, 0)
        BRIGHT_RED = (255, 0, 0)
        PURPLE_TEXT = (128, 0, 128)
        SUBTITLE_GRAY = (80, 80, 80)

        # Initialize fonts
        title_font = pygame.font.SysFont("Georgia", 72, bold=True)
        subtitle_font = pygame.font.SysFont("Georgia", 20, bold=True) 
        button_font = pygame.font.SysFont("Arial", 20, bold=True)

        # Initialize text surfaces
        title_surf = title_font.render("Simulation End", True, BLACK)
        sub_surf = subtitle_font.render("The Simulation has came to it’s close. Would you like to continue?", True, SUBTITLE_GRAY)
        
        btn_accept_surf = button_font.render("Yes", True, PURPLE_TEXT)
        btn_deny_surf = button_font.render("No", True, PURPLE_TEXT)

        # Define the buttons rect
        center_x = self.size[0] // 2
        
        # Text Rects
        title_rect = title_surf.get_rect(center=(center_x, int(self.size[1] * 0.20)))
        sub_rect = sub_surf.get_rect(center=(center_x, int(self.size[1] * 0.50)))

        # Button Rects (Stacked vertically)
        btn_width, btn_height = 240, 65
        btn_start_y = int(self.size[1] * 0.65)
        btn_spacing = 20 # Gap between the two buttons
        
        accept_button_rect = pygame.Rect(center_x - (btn_width // 2), btn_start_y, btn_width, btn_height)
        deny_button_rect = pygame.Rect(center_x - (btn_width // 2), btn_start_y + btn_height + btn_spacing, btn_width, btn_height)
        
        # Center the text inside their respective buttons
        btn_accept_text_rect = btn_accept_surf.get_rect(center=accept_button_rect.center)
        btn_deny_text_rect = btn_deny_surf.get_rect(center=deny_button_rect.center)

        pygame.mixer.music.pause() # Pause the background music when the user is deciding whether to exit or not

        self.exitSFX.play() # Play the exit sound effect when the user is deciding whether to exit or not

        # Main loop
        waiting = True
        choice = None
        self.initial_paused_time = pygame.time.get_ticks()

        while waiting:
            # Draw Background
            self.window.fill(CREAM)

            # Draw Heading Texts
            self.window.blit(title_surf, title_rect)
            self.window.blit(sub_surf, sub_rect)

            # Draw Accept Button (Green) & Text
            pygame.draw.rect(self.window, BRIGHT_GREEN, accept_button_rect)
            self.window.blit(btn_accept_surf, btn_accept_text_rect)

            # Draw Deny Button (Red) & Text
            pygame.draw.rect(self.window, BRIGHT_RED, deny_button_rect)
            self.window.blit(btn_deny_surf, btn_deny_text_rect)

            # Update Display Buffer
            pygame.display.flip()

            # Event Processing
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.queue_out.put("QUIT")
                    self.running = False
                    return "QUIT"
                
                # Explicit Mouse Click Logic for Both Buttons
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left mouse click
                        if accept_button_rect.collidepoint(event.pos):
                            waiting = False
                            return True
                        elif deny_button_rect.collidepoint(event.pos):
                            waiting = False

            # Lock Frame Rate
            self.clock.tick(self.FPS)
        
        # Exit menu time calculation
        self.final_paused_time = pygame.time.get_ticks()
        self.total_paused_time += (self.final_paused_time - self.initial_paused_time)

        # Resume music
        pygame.mixer.music.unpause()

        return False

    def pause(self): # Waits for user to input any key to resume simulation
        
        pygame.draw.polygon(self.window, (0, 0, 0), (
            (self.size[0] * (351/400), self.size[1] * (23/900)),
            (self.size[0] * (15/16), self.size[1] * (1/18)),
            (self.size[0] * (351/400), self.size[1] * (77/900))
        )) # Draw a red triangle above the pause button to indicate that the simulation is paused
        
        # Draw the overlay onto the main window
        self.window.blit(self.overlay, (0, 0))

        # Draw pause text on top of the overlay
        self.draw_text("Simulation Paused. Press any key to resume.", (255, 255, 255), (self.size[0] // 2, self.size[1] // 2))

        # Force the display to update so the user actually sees the overlay
        pygame.display.flip()

        waiting = True # Wait for the user to press a key to resume the simulation

        self.initial_paused_time = pygame.time.get_ticks() # Start counting paused time until the user presses a key to resume the simulation so that the paused time will not be included in the simulation time calculation

        pygame.mixer.music.pause() # Pause the background music when the simulation is paused

        self.pauseSFX.play() # Play the pause sound effect when the simulation is paused

        # Event loop to wait for user input
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: # If the user clicks the window's X
                    waiting = False
                    self.queue_out.put("QUIT") # Put "QUIT" into communication pipe so second window will close
                    self.running = False
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN: # If user presses any key or clicks the mouse button
                    waiting = False
                    pygame.mixer.music.unpause() # Resume the background music when the simulation is resumed
        
        # Take the final paused time after the user presses a key to resume
        self.final_paused_time = pygame.time.get_ticks()

        # Calculate the total paused time and add it to the total_paused_time variable
        self.total_paused_time += (self.final_paused_time - self.initial_paused_time)

    def draw_pause_button(self): # Draws the pause button and checks if user clicks on it
        # Hitbox of button
        self.pause_button = pygame.draw.rect(self.window, (255, 242, 204), (self.size[0] * 0.85, 10, self.size[0] * 0.1, self.size[0] * 0.1))
        
        # Circle outline of button
        pygame.draw.circle(self.window, (0, 0, 0), (self.size[0] * 0.9, self.size[1] * (1/18)), 40, 5)

        if self.pause_button.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.circle(self.window, (255, 0, 0), (self.size[0] * 0.9, self.size[1] * (1/18)), 40) # Highlight button when hovered

            if pygame.mouse.get_pressed()[0] == 1: # If the user clicks the pause button
                self.pause()

        # Draw the lines of the pause symbol
        pygame.draw.line(self.window, (0, 0, 0), (self.size[0] * (71/80), self.size[1] * (1/36)), (self.size[0] * (71/80), self.size[1] * (1/12)), 5)
        pygame.draw.line(self.window, (0, 0, 0), (self.size[0] * (73/80), self.size[1] * (1/36)), (self.size[0] * (73/80), self.size[1] * (1/12)), 5)

    def sim_time(self): # Calculates the current simulation time
        # Get the current time
        start_offset_ms = self.STARTTIME * self.SIMULATIONHOUR
        
        total_milis = pygame.time.get_ticks() + start_offset_ms - self.total_paused_time
        
        # Calculate the simulation time
        self.total_sim_hours = total_milis / self.SIMULATIONHOUR

        # Use 24-hour clock
        hour_24 = int(self.total_sim_hours) % 24
        minute = int((self.total_sim_hours * 60) % 60)

        # Determine AM or PM
        if hour_24 < 12:
            suffix = "AM"
        
        else:
            suffix = "PM"

        # Convert to 12-hour format
        hour_12 = hour_24 % 12

        # If hour is 0, set it to 12
        if hour_12 == 0:
            hour_12 = 12

        self.time_text = f"{hour_12:02}:{minute:02} {suffix}"

        if self.prev_hour != hour_24:
            self.queue_out.put(hour_24)
        
        self.prev_hour = hour_24
    
    def events(self): # Checks if any events occur

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                
                if self.confirm_exit():
                    self.running = False
                
        if self.total_sim_hours >= self.ENDTIME:
            if self.confirm_restart(): # Reset all display variables
                self.restart()

            else: # If user does not want to restart, end the program
                self.running = False

    def update(self): # Updates the current stats
        
        try:
            msg = self.queue_in.get_nowait() # Grabs the most recent message in queue
            
            if type(msg) == str:
                if msg == "QUIT":
                    self.running = False

            elif type(msg) == dict:
                # Unpack the packet from the second window
                if 'weather' in msg and 'rides' in msg:
                    self.update_weather(msg['weather'])
                    
                    # Loop through the received states and update the ride objects
                    for ride_name, status in msg['rides'].items():
                        if ride_name in self.images:
                            self.images[ride_name].status = status

        except:
            pass

        self.sim_time()

        pygame.display.flip()

        self.clock.tick(self.FPS)

    def run(self): # Main running loop

            self.startGame()

            choice=self.chooseRunType()
            self.queue_out.put(choice)

            pygame.mixer.music.play(-1) # Play the background music in a loop (-1 means it will loop infinetly)

            while self.running:

                self.draw()

                self.events()

                self.update()
            
            pygame.quit()