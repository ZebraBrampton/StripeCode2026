import pygame
from os import environ

class RideWindow:

    def __init__(self, caption, size, pos, queue_in, queue_out, logs):
        self.caption = caption
        self.size = size
        self.pos = pos
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.logs = logs

        # Initialize variables for the window
        self.running = True
        self.FPS = 60

        environ['SDL_VIDEO_WINDOW_POS'] = f"{pos[0]}, {pos[1]}"

        pygame.init()

        self.window = pygame.display.set_mode(self.size)

        pygame.display.set_caption(self.caption)

        self.font = pygame.font.SysFont("Arial", 18, bold=True)

        self.clock = pygame.time.Clock()

        self.overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 100))


        # Variables for data
        self.curr_station = "N/A"
        self.curr_hour = 10
        self.wait_sold = None
        self.station_type = None
        self.joy_sales = None
        self.alert_stations = []
        self.fix_text = ""
        
        # Visual variables
        self.background_colour = (0, 0, 0)
        self.wait_button_rect = pygame.Rect(self.size[0] // 10, self.size[1] * 0.6, self.size[0] // 2, self.size[1] // 10)
        self.satisfaction_button_rect = pygame.Rect(self.size[0] // 10, self.size[1] * 0.75, self.size[0] // 2, self.size[1] // 10)
  
    def findData(self):
        str_hour = str(self.curr_hour)

        if (str_hour, self.curr_station) in self.logs:
            values = self.logs[(str_hour, self.curr_station)]
            self.wait_sold = values[0]
            self.joy_sales = values[1]
            if "%" in self.joy_sales:
                self.station_type = "Ride"
            else:
                self.station_type = "Food"

    def check_alert_type(self):
        alert_type = [] # Checks to see the types of alerts within this station
        
        if self.station_type == "Ride":
            if float(self.wait_sold) > 30: # Check if wait time is above 30 minutes
                alert_type.append("Wait Time")

            if int(self.joy_sales.replace('%', '')) < 75: # Check if joy is below 75%
                alert_type.append("Guest Satisfaction")
        
        elif self.station_type == "Food":
            items_sold = int(self.wait_sold) # Convert items sold to an integer for comparison
            sales_amount = float(self.joy_sales.replace('$', '')) # Convert sales amount to a float for comparison

            if items_sold < 20: # Check if items sold is below 20
                alert_type.append("Items Sold")

            if sales_amount < 150: # Check if sales is below $150
                alert_type.append("Sales Amount")

        return alert_type

    def detect_alert(self):
        self.alert_stations = [] # Resets the list of stations that are having issues every time the hour changes

        for key, value in self.logs.items(): # Brings the (hour, station) and (wait/sold, joy/sales, alert) values
            if key[1] not in self.alert_stations: # Check if station is already in the alert list
                if str(self.curr_hour) in key and value[2] == True: # Check if there is an alert at the current hour
                    self.alert_stations.append(key[1]) # Add station to list of stations that are having issues
                
        self.queue_out.put(self.alert_stations) # Send alert list to main window with station names that is having issues

    def draw_text(self, text, colour, text_pos):
        text_surface = self.font.render(text, True, colour)
        text_rect = text_surface.get_rect(center=text_pos)
        self.window.blit(text_surface, text_rect)

    def draw_satisfaction_button(self, alert):
        
        if self.station_type == "Ride":
            self.fix_text = "Improve Guest Satisfaction"
        
        elif self.station_type == "Food":
            self.fix_text = "Improve Sales Amount"

        if alert:
            # Draw the red fix button
            self.satisfaction_button = pygame.draw.rect(self.window, (255, 0, 0), self.satisfaction_button_rect)
            
            # Draw the text on the fix button
            self.draw_text(self.fix_text, (255, 255, 255), (self.size[0] * 0.35, self.size[1] * 0.8))

            pos = pygame.mouse.get_pos()

            if self.satisfaction_button.collidepoint(pos):
                pygame.draw.rect(self.window, (255, 100, 100), self.satisfaction_button_rect)

                self.draw_text(self.fix_text, (255, 255, 255), (self.size[0] * 0.35, self.size[1] * 0.8))

                if pygame.mouse.get_pressed()[0] == 1:

                    if self.station_type == "Ride":
                        updated_data = int(self.joy_sales.replace('%', '')) + 10 # Increase satisfaction percentage by 10% when fix button is clicked for ride station
                        self.joy_sales = f"{updated_data}%" # Update joy_sales variable
                    
                    elif self.station_type == "Food":
                        updated_data = float(self.joy_sales.replace('$', '')) + 50 # Increase sales amount by $50 when fix button is clicked for food station
                        self.joy_sales = f"${updated_data:.2f}" # Update joy_sales variable

        else:
            # Draw the greyed out wait_time button
            pygame.draw.rect(self.window, (100, 100, 100), self.satisfaction_button_rect)

            # Draw the text on the wait_time button
            self.draw_text(self.fix_text, (255, 255, 255), (self.size[0] * 0.35, self.size[1] * 0.8))

    def draw_wait_sold_button(self, alert):
        
        if self.station_type == "Ride":
            self.fix_text = "Improve Wait Times"
        
        elif self.station_type == "Food":
            self.fix_text = "Improve Items Sold"

        if alert:
            # Draw the red fix button
            self.fix = pygame.draw.rect(self.window, (255, 0, 0), self.wait_button_rect)
            
            # Draw the text on the fix button
            self.draw_text(self.fix_text, (255, 255, 255), (self.size[0] * 0.35, self.size[1] * 0.65))

            pos = pygame.mouse.get_pos()

            if self.fix.collidepoint(pos):
                pygame.draw.rect(self.window, (255, 100, 100), self.wait_button_rect)

                self.draw_text(self.fix_text, (255, 255, 255), (self.size[0] * 0.35, self.size[1] * 0.65))

                if pygame.mouse.get_pressed()[0] == 1:
                    
                    if self.station_type == "Ride":
                        updated_data = float(self.wait_sold) - 10 # Decrease wait time by 10 minutes when fix button is clicked for ride station
                        self.wait_sold = f"{updated_data:.1f}" # Update wait_sold variable
                    
                    elif self.station_type == "Food":
                        updated_data = int(self.wait_sold) + 10 # Increase items sold by 10 when fix button is clicked for food station
                        self.wait_sold = f"{updated_data}" # Update wait_sold variable

        else:
            # Draw the greyed out wait_time button
            pygame.draw.rect(self.window, (100, 100, 100), self.wait_button_rect)

            # Draw the text on the wait_time button
            self.draw_text(self.fix_text, (255, 255, 255), (self.size[0] * 0.35, self.size[1] * 0.65))

    def draw_alerts(self):
        wait_sold_bool = False
        satisfaction_bool = False

        if self.curr_station in self.alert_stations:
            
            # Retrieve the types of alerts for the station that is having problems
            alerts = self.check_alert_type()

            # Draw the appropriate fix buttons based on the types of alerts for the station that is having problems
            if "Wait Time" in alerts or "Items Sold" in alerts:
                wait_sold_bool = True

            if "Guest Satisfaction" in alerts or "Sales Amount" in alerts:
                satisfaction_bool = True
        
            if wait_sold_bool == False and satisfaction_bool == False:
                self.alert_stations.remove(self.curr_station) # Remove station from list of stations that is having issues    

        self.draw_wait_sold_button(wait_sold_bool) # Draw the wait time or items sold fix button based on the alert type for the station that is having issues
        self.draw_satisfaction_button(satisfaction_bool) # Draw the guest satisfaction or sales amount fix button based on the alert type for the station that is having issues

        self.queue_out.put(self.alert_stations) # Send message to main window that the issue has been fixed for the station that is having issues

    def draw_bg(self):
        self.window.fill(self.background_colour)

        self.window.blit(self.overlay, (0, 0))

    def draw_station_data(self):
        if self.station_type == "Ride":
            self.draw_text(f"Current Wait Time (minutes): {self.wait_sold}", (255, 255, 255), (self.size[0] // 2, self.size[1] // 3))
            self.draw_text(f"Current Guest Satisfaction: {self.joy_sales}", (255, 255, 255), (self.size[0] // 2, self.size[1] // 2))
        
        elif self.station_type == "Food":
            self.draw_text(f"Current Items Sold: {self.wait_sold}", (255, 255, 255), (self.size[0] // 2, self.size[1] // 3))
            self.draw_text(f"Current Sales Amount: {self.joy_sales}", (255, 255, 255), (self.size[0] // 2, self.size[1] // 2))

    def draw(self):
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

    def events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                self.queue_out.put("QUIT")
                self.running = False

    def update(self):
        
        try:
            msg = self.queue_in.get_nowait() # Grabs the most recent message in queue

            if msg == "QUIT":
                self.running = False

            elif type(msg) == int:
                self.curr_hour = msg
                self.detect_alert() # Check for any stations that are having issues at the current hour and send message to main window to draw alert symbol on main window for those stations that are having issues
                self.findData() # Update the wait time, joy and sales data for the station that is currently being displayed in the second window when the hour changes
            
            elif msg.startswith("S:"):
                self.curr_station = msg[2:].split("_")[0] # Update the current station
                self.background_colour = (msg[2:].split("_")[1].strip("()").split(",")) # Update the background colour (contained as str)
                self.background_colour = tuple(int(x.strip()) for x in self.background_colour) # Converts all iterable values into a tuple
                self.findData() # Update the wait time, joy and sales data for the station that is currently being displayed in the second window when the station changes

            elif msg == "RESTART":
                self.curr_station = "N/A"
                self.curr_hour = 10
                self.wait_sold = None
                self.station_type = None
                self.joy_sales = None
                self.alert_stations = []
    
        except:
            pass   

        # Update the display
        pygame.display.flip()

        # Cap the frame rate to 60 FPS
        self.clock.tick(self.FPS)

    def run(self):

        while self.running:

            self.draw()

            self.events()

            self.update()
        
        pygame.quit()