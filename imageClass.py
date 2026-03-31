import pygame

# Image class
class Image:
    def __init__(self, name: str, pos: tuple, scale: tuple=None):

        # Initialize variables
        self.name = name
        self.pos = pos
            #self.scale = scale

        # Check if current image is the map
        if self.pos == (0, 0):
            self.map = True

        else:
            self.map = False


        # Initialize the image using initialized variables
        try:
            self.image = pygame.image.load(name + ".png").convert_alpha()

            self.width = self.image.get_width()
            #self.width = int( self.width * (scale[0] / 100) )

            self.height = self.image.get_height()
            #self.height = int( self.width * (scale[1] / 100) )

            self.image = pygame.transform.scale(self.image, (self.width, self.height))

            self.rect = self.image.get_rect()

            self.rect.topleft = (self.pos) # (x, y)

            self.clicked = False

            self.hover_colour = (255, 0, 0)

        except FileNotFoundError:
            self.image = None
    

    def hover_mouse(self, surface):

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
        

    def check_mouse(self, surface):
        action = False
        
        if self.map:
            return action

        # Get mouse pos
        pos = pygame.mouse.get_pos()

        # Check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            
            self.hover_mouse(surface)

            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        return action


    def draw(self, surface):
        
        action = self.check_mouse(surface)

        # Draw image on screen
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action