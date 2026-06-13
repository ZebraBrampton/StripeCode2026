import pygame
from os import environ

class RideWindow:

    def __init__(self, caption, size, pos, queue_in, queue_out, logs): # Initialize all important variables for the window
        self.caption = caption # Title of the window
        self.size = size # Size of the window
        self.pos = pos # Position of the window on the screen
        self.queue_in = queue_in # The pipeline that recieves messages
        self.queue_out = queue_out # The pipeline that sends out messages
        self.logs = logs # The data logs that contains all information about the stations

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
        self.curr_hour = 10 # Current hour
        self.wait_sold = None # Current wait time/items sold for rides/food stations
        self.station_type = None # Current station type (food or ride)
        self.joy_sales = None # Current guest satisfaction/sales amount for rides/food stations
        self.alert_stations = [] # List of stations that have alerts
        self.fix_text = "" # Text that is displaying on the fix button
        self.cta_type = None # Type of CTA that is being displayed on the CTA button
        
        # Visual variable (rectangles)
            # Background colour of the window
        self.background_colour = (0, 0, 0)
            # Rectangle attributes for the wait time/items sold fix button 
        self.wait_button_rect = pygame.Rect(self.size[0] // 10, self.size[1] * 0.6, self.size[0] // 2, self.size[1] // 10)
            # Rectangle attributes for the guest satisfaction/sales amount fix button
        self.satisfaction_button_rect = pygame.Rect(self.size[0] // 10, self.size[1] * 0.75, self.size[0] // 2, self.size[1] // 10)
            # Rectangle attributes for the CTA button
        self.cta_rect = pygame.Rect(self.size[0] // 1.5, self.size[1] * 0.6, self.size[0] // 3.5, self.size[1] // 4)

        # Audio initialization - fix sound effect
        self.fixSFX = pygame.mixer.Sound("Audio/FixSFX.mp3")

    def findData(self): # Locate the specific stats of the clicked station at current hour
        str_hour = str(self.curr_hour) # Convert to string

        if (str_hour, self.curr_station) in self.logs: # Check if there is data for the current station at given hour
            values = self.logs[(str_hour, self.curr_station)] # Store the data into a variable
            # Split up the stored data in 'values' to be used in seperate variables
            self.wait_sold = values[0] # Wait time for rides or items sold for food stations
            self.joy_sales = values[1] # Guest satisfaction for rides or sales amount for food stations
            if "%" in self.joy_sales: # Check if logs contain "&" to indicate a ride, otherwise it is a food station
                self.station_type = "Ride"
            else:
                self.station_type = "Food"

    def check_alert_type(self): # Determine which type of alert is occurring for current station on screen
        alert_type = [] # Checks to see the types of alerts within this station
        
        if self.station_type == "Ride": # If the current station is a ride
            wait_time = float(self.wait_sold) # Convert wait time to a float for comparison
            satisfaction = int(self.joy_sales.replace('%', '')) # Convert satisfaction percentage
           
            if wait_time > 50 and satisfaction < 70: # Check if wait time is above 50 minutes and satisfaction is below 70% for CTA
                alert_type.append("Express Queue")
           
            elif wait_time > 35 and satisfaction < 70: # Check if wait time is above 35 minutes and satisfaction is below 70% for CTA
                alert_type.append("Increase Staffing")

            else:
                if wait_time > 30: # Check if wait time is above 30 minutes
                    alert_type.append("Wait Time")

                if satisfaction < 75: # Check if satisfaction is below 75%
                    alert_type.append("Guest Satisfaction")
        
        elif self.station_type == "Food": # If the current station is a food station
            items_sold = int(self.wait_sold) # Convert items sold to an integer for comparison
            sales_amount = float(self.joy_sales.replace('$', '')) # Convert sales amount to a float for comparison

            if items_sold > 20 and sales_amount < 100: # Check if more than 20 items sold and less than $100 in sales for CTA
                alert_type.append("Flash Sale")
           
            elif items_sold > 30 and sales_amount < 200: # Check if more than 30 items sold and less than $200 in sales for CTA
                alert_type.append("Fast-Pass")

            else:
                if items_sold < 20: # Check if items sold is below 20
                    alert_type.append("Items Sold")

                if sales_amount < 150: # Check if sales is below $150
                    alert_type.append("Sales Amount")

        return alert_type # Return back to the code the list of alerts

    def detect_alert(self): # Check all stations in the hour to see if they have alerts, then send the information to main window
        self.alert_stations = [] # Resets the list of stations that are having issues every time the hour changes

        for key, value in self.logs.items(): # Brings the (hour, station) and (wait/sold, joy/sales, alert) values
            if key[1] not in self.alert_stations: # Check if station is already in the alert list
                if str(self.curr_hour) in key and value[2] == True: # Check if there is an alert at the current hour
                    self.alert_stations.append(key[1]) # Add station to list of stations that are having issues
                
        self.queue_out.put(self.alert_stations) # Send alert list to main window with station names that is having issues

    def draw_text(self, text, colour, text_pos): # Creates and draws text onto the screen
        text_surface = self.font.render(text, True, colour) # Render the text with the given colour
        text_rect = text_surface.get_rect(center=text_pos) # Get the rectangle of the text surface and set its center to the given text position
        self.window.blit(text_surface, text_rect) # Draw the text surface onto the window at the position of the text rectangle

    def draw_satisfaction_button(self, alert): # Draws and monitors the guest satisfaction / sales amount button
        
        if self.station_type == "Ride": # If the station type is ride
            self.fix_text = "Improve Guest Satisfaction"
        
        elif self.station_type == "Food": # If the station type is food
            self.fix_text = "Improve Sales Amount"

        if alert: # If there is an alert for station on screen
            
            # Draw the red fix button
            self.satisfaction_button = pygame.draw.rect(self.window, (255, 0, 0), self.satisfaction_button_rect)
            
            # Draw the text on the fix button
            self.draw_text(self.fix_text, (255, 255, 255), (self.size[0] * 0.35, self.size[1] * 0.8))

            # Get mouse position
            pos = pygame.mouse.get_pos()

            if self.satisfaction_button.collidepoint(pos): # Check if mouse is hovering over the fix button
                pygame.draw.rect(self.window, (255, 100, 100), self.satisfaction_button_rect) # Change the colour

                self.draw_text(self.fix_text, (255, 255, 255), (self.size[0] * 0.35, self.size[1] * 0.8)) # Draw the text on top of new coloured button

                if pygame.mouse.get_pressed()[0] == 1: # If user clicks on the fix button (presses left mouse button)
                    
                    self.fixSFX.play() # Play the fix sound effect when the satisfaction/sales fix button is clicked

                    if self.station_type == "Ride": # If current station is a ride
                        updated_data = int(self.joy_sales.replace('%', '')) + 10 # Increase satisfaction percentage by 10% when fix button is clicked for ride station
                        self.joy_sales = f"{updated_data}%" # Update joy_sales variable
                    
                    elif self.station_type == "Food": # If current station is a food station
                        updated_data = float(self.joy_sales.replace('$', '')) + 50 # Increase sales amount by $50 when fix button is clicked for food station
                        self.joy_sales = f"${updated_data:.2f}" # Update joy_sales variable

        else: # If there is no alert for current station on screen
            
            # Draw the greyed out wait_time button
            pygame.draw.rect(self.window, (100, 100, 100), self.satisfaction_button_rect)

            # Draw the text on the wait_time button
            self.draw_text(self.fix_text, (255, 255, 255), (self.size[0] * 0.35, self.size[1] * 0.8))

    def draw_wait_sold_button(self, alert): # Draws and monitors the wait time / items sold button
        
        if self.station_type == "Ride": # If current station is a ride
            self.fix_text = "Improve Wait Times"
        
        elif self.station_type == "Food": # If current station is a food station
            self.fix_text = "Improve Items Sold"

        if alert: # If there is an alert for station on screen

            # Draw the red fix button
            self.fix = pygame.draw.rect(self.window, (255, 0, 0), self.wait_button_rect)
            
            # Draw the text on the fix button
            self.draw_text(self.fix_text, (255, 255, 255), (self.size[0] * 0.35, self.size[1] * 0.65))

            # Get mouse position
            pos = pygame.mouse.get_pos()

            if self.fix.collidepoint(pos): # Check if mouse is hovering over the fix button
                pygame.draw.rect(self.window, (255, 100, 100), self.wait_button_rect) # Change the colour of the button

                self.draw_text(self.fix_text, (255, 255, 255), (self.size[0] * 0.35, self.size[1] * 0.65)) # Draw the text on top of new coloured button

                if pygame.mouse.get_pressed()[0] == 1: # If user clicks on the fix button (presses left mouse button)
                    
                    self.fixSFX.play() # Play the fix sound effect when the wait time/items sold fix button is clicked

                    if self.station_type == "Ride": # If current station is a ride
                        updated_data = float(self.wait_sold) - 10 # Decrease wait time by 10 minutes when fix button is clicked for ride station
                        self.wait_sold = f"{updated_data:.1f}" # Update wait_sold variable
                    
                    elif self.station_type == "Food": # If current station is a food station
                        updated_data = int(self.wait_sold) + 10 # Increase items sold by 10 when fix button is clicked for food station
                        self.wait_sold = f"{updated_data}" # Update wait_sold variable

        else: # If there is no alert for current station on screen

            # Draw the greyed out wait_time button
            pygame.draw.rect(self.window, (100, 100, 100), self.wait_button_rect)

            # Draw the text on the wait_time button
            self.draw_text(self.fix_text, (255, 255, 255), (self.size[0] * 0.35, self.size[1] * 0.65))

    def draw_cta_button(self, alert): # Draws and monitors the dynamic CTA button

        if alert: # If there is an alert for station on screen that requires a CTA button
            # Draw the red fix button
            self.fix = pygame.draw.rect(self.window, (255, 0, 0), self.cta_rect)
            
            # Draw the text on the fix button
            self.draw_text(self.cta_type, (255, 255, 255), (self.size[0] * 0.8, self.size[1] * 0.65))

            # Get mouse position
            pos = pygame.mouse.get_pos()

            if self.fix.collidepoint(pos): # Check if mouse is hovering over the fix button
                pygame.draw.rect(self.window, (255, 100, 100), self.cta_rect) # Change the colour of the button

                self.draw_text(self.cta_type, (255, 255, 255), (self.size[0] * 0.8, self.size[1] * 0.65)) # Draw the text on top of new coloured button

                if pygame.mouse.get_pressed()[0] == 1: # If user clicks on the fix button (presses left mouse button)
                    
                    self.fixSFX.play() # Play the fix sound effect when the CTA button is clicked

                    if self.cta_type == "Express Queue": # If the CTA is express queue for a ride station
                        updated_data = float(self.wait_sold) // 2 # Decrease wait time by halving it
                        self.wait_sold = f"{updated_data:.1f}" # Update wait_sold variable

                        updated_data = int(self.joy_sales.replace('%', '')) + 15 # Increase satisfaction percentage by 15%
                        self.joy_sales = f"{updated_data}%" # Update joy_sales variable

                    
                    elif self.cta_type == "Increase Staffing": # If the CTA is increase staffing for a ride station
                        updated_data = float(self.wait_sold) - 20 # Decrease wait time by halving it
                        self.wait_sold = f"{updated_data:.1f}" # Update wait_sold variable

                        updated_data = int(self.joy_sales.replace('%', '')) + 10 # Increase satisfaction percentage by 10%
                        self.joy_sales = f"{updated_data}%" # Update joy_sales variable
                    

                    elif self.cta_type == "Flash Sale": # If the CTA is flash sale for a food station
                        updated_data = int(self.wait_sold) + 10 # Increase items sold by 10
                        self.wait_sold = f"{updated_data}" # Update wait_sold variable

                        updated_data = float(self.joy_sales.replace('$', '')) * 1.5 # Increase sales amount
                        self.joy_sales = f"${updated_data:.2f}" # Update wait_sold variable


                    elif self.cta_type == "Fast-Pass": # If the CTA is fast-pass for a food station
                        updated_data = int(self.wait_sold) + 5 # Increase items sold
                        self.wait_sold = f"{updated_data}" # Update wait_sold variable

                        updated_data = float(self.joy_sales.replace('$', '')) * 1.3 # Increase sales amount
                        self.joy_sales = f"${updated_data:.2f}" # Update wait_sold variable

                    self.cta_type = "" # Remove the CTA after it has been used once

        else: # If there is no alert for current station on screen that requires a CTA button

            # Draw the greyed out cta button
            pygame.draw.rect(self.window, (100, 100, 100), self.cta_rect)

            # Draw the text on the cta button
            self.draw_text("CTA", (255, 255, 255), (self.size[0] * 0.8, self.size[1] * 0.65))

    def draw_alerts(self): # Determines which buttons should be drawn and not
        # All buttons are set to not be drawn unless changed
        wait_sold_bool = False
        satisfaction_bool = False
        cta_bool = False
        self.cta_type = None

        # If current station has an alert from the list of stations having alerts
        if self.curr_station in self.alert_stations:
            
            # Retrieve the types of alerts for the station that is having problems
            alerts = self.check_alert_type()

            # If no basic fix buttons are in alert types
            if alerts and (("Wait Time" not in alerts) and
                           ("Items Sold" not in alerts) and
                           ("Guest Satisfaction" not in alerts) and
                           ("Sales Amount" not in alerts)):
                cta_bool = True # Set CTA button to be drawn
                self.cta_type = alerts[0] # Set the type of CTA that should be drawn into this variable

            else: # If there are basic fix buttons in the alert types

                # Draw the appropriate fix buttons based on the types of alerts for the station that is having problems
                if "Wait Time" in alerts or "Items Sold" in alerts: # If there is an alert for wait time or items sold
                    wait_sold_bool = True # Draw the wait time/items sold fix button

                if "Guest Satisfaction" in alerts or "Sales Amount" in alerts: # If there is an alert for guest satisfaction or sales amount
                    satisfaction_bool = True # Draw the guest satisfaction/sales amount fix button

            if wait_sold_bool == False and satisfaction_bool == False and cta_bool == False:
                self.alert_stations.remove(self.curr_station) # Remove station from list of stations that is having issues    
                self.queue_out.put(self.alert_stations) # Send message to main window that the issue has been fixed for the station that is having issues

        self.draw_wait_sold_button(wait_sold_bool) # Draw the wait time or items sold fix button based on the alert type for the station that is having issues
        self.draw_satisfaction_button(satisfaction_bool) # Draw the guest satisfaction or sales amount fix button based on the alert type for the station that is having issues
        self.draw_cta_button(cta_bool) # Draw the CTA button if there is an alert that requires a CTA based on the alert type for the station that is having issues

    def draw_bg(self): # Draws the background
        self.window.fill(self.background_colour) # Fill the background with the current background colour

        self.window.blit(self.overlay, (0, 0)) # Draw the semi-transparent overlay on top of the background

    def draw_station_data(self): # Determines which text should be drawn depending on the current station
        if self.station_type == "Ride": # If current station is a ride, draw the wait time and guest satisfaction data
            self.draw_text(f"Current Wait Time (minutes): {self.wait_sold}", (255, 255, 255), (self.size[0] // 2, self.size[1] // 3))
            self.draw_text(f"Current Guest Satisfaction: {self.joy_sales}", (255, 255, 255), (self.size[0] // 2, self.size[1] // 2))
        
        elif self.station_type == "Food": # If current station is a food station, draw the items sold and sales amount data
            self.draw_text(f"Current Items Sold: {self.wait_sold}", (255, 255, 255), (self.size[0] // 2, self.size[1] // 3))
            self.draw_text(f"Current Sales Amount: {self.joy_sales}", (255, 255, 255), (self.size[0] // 2, self.size[1] // 2))

    def draw(self): # Main drawing function that calls other drawing functions
        # Background screen
        self.draw_bg()

        # Draw the fix buttons
        self.draw_alerts()

        # Draw the current station
        self.draw_text(f"Current Station: {self.curr_station}", (255, 255, 255), (self.size[0] // 2, self.size[1] // 5))
        
        # Draw the current hour
        self.draw_text(f"Current Hour: {self.curr_hour}", (255, 255, 255), (self.size[0] // 2, self.size[1] // 4))
        
        # Draw the current data
        self.draw_station_data()

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
                self.detect_alert() # Check for any stations that are having issues at the current hour and send message to main window to draw alert symbol on main window for those stations that are having issues
                self.findData() # Update the wait time, joy and sales data for the station that is currently being displayed in the second window when the hour changes
            
            elif msg.startswith("S:"): # If the message starts with "S:"
                self.curr_station = msg[2:].split("_")[0] # Update the current station
                self.background_colour = (msg[2:].split("_")[1].strip("()").split(",")) # Update the background colour (contained as str)
                self.background_colour = tuple(int(x.strip()) for x in self.background_colour) # Converts all iterable values into a tuple
                self.findData() # Update the wait time, joy and sales data for the station that is currently being displayed in the second window when the station changes

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