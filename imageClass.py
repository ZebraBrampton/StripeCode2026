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
            self.image = pygame.image.load(f"Images/{name}.png").convert_alpha()

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

    def draw_text(self, text, colour, text_pos, surface):
        text_surface = pygame.font.SysFont("Arial", 18, bold=True).render(text, True, colour)
        text_rect = text_surface.get_rect(center=text_pos)
        surface.blit(text_surface, text_rect)

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

    def draw_alert(self, surface):
        # Flashes every 500ms (0.5 seconds)
        # Lowering time will make it flash faster, increasing time will make it flash slower
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            pygame.draw.polygon(surface, (255, 0, 0), [
                (self.pos[0] + self.width * 1.1, self.pos[1] + self.height // 2),
                (self.pos[0] + self.width * 1.1 - 10, self.pos[1] + self.height // 3),
                (self.pos[0] + self.width * 1.1 + 10, self.pos[1] + self.height // 3)
            ])
        
        self.draw_text("ALERT", (255, 255, 255), (self.pos[0] + self.width * 1.1, self.pos[1] + self.height // 2), surface)

    def draw(self, surface):
        
        action = self.check_mouse(surface)

        # Draw image on screen
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action