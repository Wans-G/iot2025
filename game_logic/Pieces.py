import pygame

tile_image = ["game_logic/img/Wood_Tile.png", "game_logic/img/Sheep_Tile.png", "game_logic/img/Wheat_Tile.png",
          "game_logic/img/Brick_Tile.png", "game_logic/img/Ore_Tile.png", "game_logic/img/Desert_Tile.png", "game_logic/img/Ocean_Tile.png"]

road_image = ["game_logic/img/Road_Red.png","game_logic/img/Road_Orange.png","game_logic/img/Road_White.png","game_logic/img/Road_Blue.png"]

town_image = ["game_logic/img/Town_Red.png","game_logic/img/Town_Orange.png","game_logic/img/Town_White.png","game_logic/img/Town_Blue.png"]

class Tile():
    def __init__(self, pos:tuple, type:int, value:int, num:int):
        self.sprite = pygame.image.load(tile_image[type]).convert_alpha()
        self.position = pos
        self.recource = type
        self.value = value
        self.num = num
        font = pygame.font.SysFont("Ariel", 20)
        self.posText = font.render(str(num), False, (0, 0, 0))
        self.valueText = font.render(str(value), False, (0, 0, 0))
        self.centered = (pos[0] - self.sprite.get_width()/2, pos[1] - self.sprite.get_height()/2)
        self.posTextCenter = (pos[0] - self.posText.get_rect().width/2, pos[1] + 20 - self.posText.get_rect().height/2)
        self.valTextCenter = (pos[0] - self.valueText.get_rect().width/2, pos[1] - self.valueText.get_rect().height/2)
    
    def getRecource(self):
        return self.recource
    
    def getPosition(self):
        return self.position
    
    def getNumber(self) -> int:
        return self.num

    def getTokenValue(self):
        return self.value
    
    def render(self, screen:pygame.Surface):
        screen.blit(self.sprite, self.centered)
        if (self.value != 0):
            pygame.draw.circle(screen, "tan", self.position, 10)
            screen.blit(self.valueText, self.valTextCenter)
        screen.blit(self.posText, self.posTextCenter)

class Road():
    def __init__(self, pos:tuple, angle:int, color:int):
        self.sprite = pygame.image.load(road_image[color]).convert_alpha()
        self.sprite = pygame.transform.rotate(self.sprite, angle)
        self.position = pos
        self.angle = angle
        self.color = color
        self.centered = (pos[0] - self.sprite.get_width()/2, pos[1] - self.sprite.get_height()/2)

    def getColor(self) -> int:
        return self.color

    def render(self, screen:pygame.Surface):
        screen.blit(self.sprite, self.centered)

class Town():
    def __init__(self, pos:tuple, color:int):
        self.sprite = pygame.image.load(town_image[color]).convert_alpha()
        self.position = pos
        self.color = color
        self.centered = (pos[0] - self.sprite.get_width()/2, pos[1] - self.sprite.get_height()/2)
    
    def getColor(self) -> int:
        return self.color

    def render(self, screen:pygame.Surface):
        screen.blit(self.sprite, self.centered)
