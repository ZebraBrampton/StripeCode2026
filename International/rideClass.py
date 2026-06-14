import pygame

# Rides class
class Rides:
    def __init__(self, name: str, file: str, pos: tuple, scale: tuple, outside: bool, colour: tuple=(0, 0, 0)): # Initalizes properties of the images

        # Initialize variables
        self.name = name
        self.pos = pos
        self.width, self.height = scale
        self.outside = outside
        self.colour = colour

        # Check if current image is the map
        if self.pos == (0, 0):
            self.map = True

        else:
            self.map = False


        # Initialize the image using initialized variables
        try:
            self.image = pygame.image.load(file).convert_alpha()

            self.image = pygame.transform.scale(self.image, scale) # Change the scale of the image

            self.rect = self.image.get_rect() # Get the rectangle of the image for mouse collision detection

            self.rect.topleft = (self.pos) # (x, y)

            self.clicked = False # Variable to check if the image has been clicked on or not, used to prevent multiple clicks from one click

            self.hover_colour = (255, 0, 0) # Colour of the outline when the mouse is hovered above the image
            
        except FileNotFoundError: # If the image file is not found
            self.image = None # Set image to None if file is not found
        
        # Audio Initialization
        self.clickSFX = pygame.mixer.Sound("International/Audio/ClickSFX.mp3")

    def draw_text(self, text, colour, text_pos, surface): # Draws text onto given surface
        text_surface = pygame.font.SysFont("Arial", 18, bold=True).render(text, True, colour) # Create a text surface using the given text and colour
        text_rect = text_surface.get_rect(center=text_pos) # Get the rectangle of the text surface and set its center to the given text position
        surface.blit(text_surface, text_rect) # Draw the text surface onto the given surface at the position of the text rectangle

    def hover_mouse(self, surface): # Creates a outline of image when mouse is hovered above the image
    
        pygame.draw.line(surface, self.hover_colour, (self.pos),
                        (self.pos[0] + self.width, self.pos[1]),
                        5)
        
        pygame.draw.line(surface, self.hover_colour, (self.pos[0] + self.width, self.pos[1]),
                        (self.pos[0] + self.width, self.pos[1] + self.height),
                        5)
        
        pygame.draw.line(surface, self.hover_colour, (self.pos[0] + self.width, self.pos[1] + self.height), 
                        (self.pos[0], self.pos[1] + self.height),
                        5)
        
        pygame.draw.line(surface, self.hover_colour, (self.pos[0], self.pos[1] + self.height), 
                        (self.pos),
                        5)
        
    def check_mouse(self, surface): # Checks if mouse is hovered above the image and if the user clicked on image
        action = False # If user clicked on the image
        
        if self.map: # If the image is the map, there will be no clicking or hovering effects
            return action # Return False if the image is the map

        # Get mouse pos
        pos = pygame.mouse.get_pos()

        # Check mouseover and clicked conditions
        if self.rect.collidepoint(pos) and self.outside:
            
            self.hover_mouse(surface) # Call the hover mouse function to create the outline when mouse is hovered above the image

            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False: # If the left mouse button is being pressed and the image has not already been clicked from that click
                self.clickSFX.play() # Play click sound effect when image is clicked
                self.clicked = True # Set clicked to True to prevent multiple clicks from one click
                action = True # Set action to True if the image has been clicked on

        if pygame.mouse.get_pressed()[0] == 0: # If the mouse button is not being pressed, reset clicked to False to allow for clicking again
            self.clicked = False # Reset clicked to False when mouse button is released to allow for clicking again

        return action # Return whether the image has been clicked on or not

    def draw_signal(self, surface): # Draws a ride impact symbol
        pass

    def draw(self, surface): # Main drawing function that returns whether image has been clicked on or not
        
        action = self.check_mouse(surface) # Check if the image has been clicked on and store the result in action variable

        # Draw image on screen
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action # Return whether the image has been clicked on or not