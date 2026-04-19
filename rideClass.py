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

        self.running = True
        self.FPS = 60

        environ['SDL_VIDEO_WINDOW_POS'] = f"{pos[0]}, {pos[1]}"

        pygame.init()

        self.window = pygame.display.set_mode(self.size)

        pygame.display.set_caption(self.caption)

        self.font = pygame.font.SysFont("Arial", 18, bold=True)

        self.clock = pygame.time.Clock()


        self.curr_station = "N/A"
        self.curr_hour = 10
        self.wait_sold = None
        self.station_type = None
        self.joy_sales = None
        self.alert_stations = []
  
    def findData(self):
        str_hour = str(self.curr_hour)

        if (str_hour, self.curr_station) in self.logs:
            values = self.logs[(str_hour, self.curr_station)]
            self.wait_sold = values[0]
            self.joy_sales = values[1]
            #self.alert = values[2]
            if "%" in self.joy_sales:
                self.station_type = "Ride"
            else:
                self.station_type = "Food"

    def detect_alert(self, hour):
        str_hour = str(hour)

        for key, value in self.logs.items(): # Brings the (hour, station) and (wait/sold, joy/sales, alert) values
            if key[1] not in self.alert_stations: # Check if station is already in the alert list
                if str_hour in key and value[2] == True: # Check if there is an alert at the current hour
                    self.alert_stations.append(key[1]) # Add station to list of stations that are having issues
                
        self.queue_out.put(self.alert_stations) # Send alert list to main window with station names that is having issues

    def draw_text(self, text, colour, text_pos):
        text_surface = self.font.render(text, True, colour)
        text_rect = text_surface.get_rect(center=text_pos)
        self.window.blit(text_surface, text_rect)

    def draw_alert(self):

        if self.curr_station in self.alert_stations:

            # Draw the red fix button
            self.fix = pygame.draw.rect(self.window, (255, 0, 0), (self.size[0] // 2, self.size[1] * 0.7, self.size[0] // 2, self.size[1] // 6))

            # Draw the text on the fix button
            self.draw_text("FIX", (255, 255, 255), (self.size[0] * 0.75, self.size[1] * 0.75))

            pos = pygame.mouse.get_pos()

            if self.fix.collidepoint(pos):
                pygame.draw.rect(self.window, (255, 100, 100), (self.size[0] // 2, self.size[1] * 0.7, self.size[0] // 2, self.size[1] // 6))

                self.draw_text("FIX", (255, 255, 255), (self.size[0] * 0.75, self.size[1] * 0.75))

                if pygame.mouse.get_pressed()[0] == 1:
                    self.alert_stations.remove(self.curr_station) # Remove station from list of stations that is having issues when fix button is clicked
                    self.queue_out.put(self.alert_stations) # Send message to main window that the issue has been fixed for the station that is having issues

        else:
            # Draw the greyed out fix button
            pygame.draw.rect(self.window, (100, 100, 100), (self.size[0] // 2, self.size[1] * 0.7, self.size[0] // 2, self.size[1] // 6))

            # Draw the text on the fix button
            self.draw_text("FIX", (255, 255, 255), (self.size[0] * 0.75, self.size[1] * 0.75))

    def draw(self):
        # Background screen
        self.window.fill((0, 0, 0))

        # Draw the fix button
        self.draw_alert()

        # Draw the current station
        self.draw_text(f"Current Station: {self.curr_station}", (255, 255, 255), (self.size[0] // 2, self.size[1] // 5))
        
        # Draw the current hour
        self.draw_text(f"Current Hour: {self.curr_hour}", (255, 255, 255), (self.size[0] // 2, self.size[1] // 4))
        
        if self.station_type == "Ride":
            self.draw_text(f"Current Wait Time (minutes): {self.wait_sold}", (255, 255, 255), (self.size[0] // 2, self.size[1] // 3))
            self.draw_text(f"Current Guest Satisfaction: {self.joy_sales}", (255, 255, 255), (self.size[0] // 2, self.size[1] // 2))
        
        elif self.station_type == "Food":
            self.draw_text(f"Current Items Sold: {self.wait_sold}", (255, 255, 255), (self.size[0] // 2, self.size[1] // 3))
            self.draw_text(f"Current Sales Amount: {self.joy_sales}", (255, 255, 255), (self.size[0] // 2, self.size[1] // 2))
        
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
                self.detect_alert(self.curr_hour) # Check for any stations that are having issues at the current hour and send message to main window to draw alert symbol on main window for those stations that are having issues
                self.findData() # Update the wait time, joy and sales data for the station that is currently being displayed in the second window when the hour changes
            
            elif msg.startswith("S:"):
                self.curr_station = msg[2:]
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