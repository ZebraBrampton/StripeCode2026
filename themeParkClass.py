import pygame
from os import environ

from imageClass import Image

class ParkWindow:

    SIMULATIONHOUR = 1000 * 10 # One simulation hour is 10 seconds (10,000ms)
    STARTTIME = 10 # Start clock at 10:00 AM
    ENDTIME = 21 # End clock at 9:00 PM

    def __init__(self, caption, size, pos, queue_in, queue_out, images):
        self.caption = caption
        self.size = size
        self.pos = pos
        self.queue_in = queue_in
        self.queue_out = queue_out
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
        self.queue_out.put(self.prev_hour)

        self.alert_stations = []

    def initImages(self):
        for ride in self.images: # Load all the station and ride images on the main window
            self.images[ride] = Image(*self.images[ride])

    def startGame(self):
        overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        
        # Draw the overlay onto the main window
        self.window.blit(overlay, (0, 0))

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

    def pause(self):
        
        pygame.draw.polygon(self.window, (0, 0, 0), (
            (self.size[0] * (351/400), self.size[1] * (23/900)),
            (self.size[0] * (15/16), self.size[1] * (1/18)),
            (self.size[0] * (351/400), self.size[1] * (77/900))
        )) # Draw a red triangle above the pause button to indicate that the simulation is paused
        
        overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        
        # Draw the overlay onto the main window
        self.window.blit(overlay, (0, 0))

        # Draw pause text on top of the overlay
        self.draw_text("Simulation Paused. Press any key to resume.", (255, 255, 255), (self.size[0] // 2, self.size[1] // 2))

        # Force the display to update so the user actually sees the overlay
        pygame.display.flip()

        waiting = True # Wait for the user to press a key to resume the simulation

        self.initial_paused_time = pygame.time.get_ticks() # Start counting paused time until the user presses a key to resume the simulation so that the paused time will not be included in the simulation time calculation

        # Event loop to wait for user input
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: # If the user clicks the window's X
                    waiting = False
                    self.queue_out.put("QUIT") # Put "QUIT" into communication pipe so second window will close
                    self.running = False
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN: # If user presses any key or clicks the mouse button
                    waiting = False
        
        # Take the final paused time after the user presses a key to resume
        self.final_paused_time = pygame.time.get_ticks()

        # Calculate the total paused time and add it to the total_paused_time variable
        self.total_paused_time += (self.final_paused_time - self.initial_paused_time)

    def draw_pause_button(self):
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

    def check_alert(self, msg):
        if msg.startswith("ALERT_ADD_"):
                alert_station = msg.split("_")[-1] # Get the station name from the message
                
                self.alert_stations.append(alert_station) # Add station to list of stations that are having issues

        elif msg.startswith("ALERT_REMOVE_"):
            alert_station = msg.split("_")[-1] # Get the station name from the message

            if alert_station in self.alert_stations:
                self.alert_stations.remove(alert_station) # Remove station from list of stations that are having issues

    def draw_text(self, text, colour, text_pos):
        text_surface = self.font.render(text, True, colour)
        text_rect = text_surface.get_rect(center=text_pos)
        self.window.blit(text_surface, text_rect)

    def draw_alert(self):
        for alert in self.alert_stations:
            if alert in self.images:
                self.images[alert].draw_alert(self.window) # Call the draw_alert method for any station that is having issues to draw the alert symbol on the main window

    def draw(self):
        self.window.fill((200, 200, 200))

        # Draw stations and rides
        for ride in self.images:

            if self.images[ride].draw(self.window):
                self.queue_out.put(f"S:{ride}")
        
        # Draw timer
        self.draw_text(self.time_text, (0, 0, 0), (100, 100))

        # Draw alerts
        self.draw_alert()

        # Draw the pause button
        self.draw_pause_button()

    def confirm_exit(self):
        overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        
        # Draw the overlay onto the main window
        self.window.blit(overlay, (0, 0))
        
        # Draw confirmation text on top of the overlay
        self.draw_text("Are you sure you want to exit? Press 'Y' (Yes) or 'N' (No)", (255, 255, 255), (self.size[0] // 2, self.size[1] // 2))
        
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
                        self.queue_out.put("QUIT") # Put "QUIT" into communication pipe so second window (if open) will close
                        return True  # Yes, exit the program
                    
                    elif event.key == pygame.K_n:
                        self.final_paused_time = pygame.time.get_ticks()

                        self.total_paused_time += (self.final_paused_time - self.initial_paused_time)
                        return False # No, return to the main loop

    def restart(self):
        self.time_text = "00:00" # Reset time text
        self.total_paused_time = pygame.time.get_ticks() # Reset total paused time
        self.prev_hour = self.STARTTIME # Reset previous hour to the start time
        self.queue_out.put(self.prev_hour) # Send message to second window to reset its display to the default screen
        self.alert_stations = [] # Reset list of stations that are having issues to empty list

    def confirm_restart(self):
        overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        
        # Draw the overlay onto the main window
        self.window.blit(overlay, (0, 0))
        
        # Draw confirmation text on top of the overlay
        self.draw_text("GAME OVER - Do you wish to restart? Press 'Y' (Yes) or 'N' (No)", (255, 255, 255), (self.size[0] // 2, self.size[1] // 2))
        
        # Force the display to update so the user actually sees the overlay
        pygame.display.flip()
        
        # Wait for the user's response
        waiting = True

        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True # If they click the window's X again, force quit
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        self.queue_out.put("RESTART") # Put "RESTART" into communication pipe so second window will reset its data and return to default screen
                        return True  # Yes, restart the program
                    
                    elif event.key == pygame.K_n:
                        return False # No, return to the main loop
        return False
   
    def sim_time(self):
        # Get the current elapsed time
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
    
    def events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                
                if self.confirm_exit():
                    self.running = False
                
        if self.total_sim_hours >= self.ENDTIME:
            if self.confirm_restart(): # Reset all display variables
                self.restart()

            else: # If user does not want to restart, end the program
                self.running = False

    def update(self):
        
        try:
            msg = self.queue_in.get_nowait() # Grabs the most recent message in queue
            
            if type(msg) == str:
                if msg == "QUIT":
                    self.running = False

                if msg.startswith("ALERT_"):
                    self.check_alert(msg) # Call function to check for alert and draw it on the screen if there is one
        
            elif type(msg) == list:
                self.alert_stations = msg # Update the list of stations that are having issues if there is a change in the list from the second window

        except:
            pass

        self.sim_time()

        pygame.display.flip()

        self.clock.tick(self.FPS)

    def run(self):
        
        self.initImages()

        self.startGame()

        while self.running:

            self.draw()

            self.events()

            self.update()
        
        pygame.quit()