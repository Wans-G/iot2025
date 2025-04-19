import pygame
from Pieces import Tile
import numpy as np
from Grid import HexGrid
import random

# Dependencies: Python, pygame, numpy


screenDimention = (1280, 720)
center = (screenDimention[0] / 2, screenDimention[1] / 2)

recource = {"Wood": 0, "Sheep": 1, "Wheat": 2, "Brick": 3, "Ore": 4, "Desert": 5}
color = {"Red": 0, "Orange": 1, "White": 2, "Blue": 3}
playerColor = ["red", "orange", "white", "blue"]

def main():
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode(screenDimention, pygame.RESIZABLE)
    gameBoard = pygame.Surface((400,400))
    player0 = pygame.Surface((320,280))
    player1 = pygame.Surface((320,280))
    player2 = pygame.Surface((320,280))
    player3 = pygame.Surface((320,280))
    clock = pygame.time.Clock()
    running = True

    game = Game()

    game.placeTown(0, 1, 2, color["Red"])
    game.placeRoad(2, 1, color["Red"])
    game.placeRoad(2, 9, color["Red"])
    game.placeTown(5, 6, 17, color["Red"])
    game.placeRoad(17, 6, color["Red"])
    game.placeRoad(17, 18, color["Red"])

    game.placeTown(15, 16, 5, color["Blue"])
    game.placeRoad(4, 5, color["Blue"])
    game.placeRoad(15, 5, color["Blue"])
    game.placeTown(3, 4, 13, color["Blue"])
    game.placeRoad(13, 4, color["Blue"])
    game.placeRoad(4, 14, color["Blue"])

    game.placeTown(3, 12, 11, color["Orange"])
    game.placeRoad(12, 11, color["Orange"])
    game.placeRoad(12, 26, color["Orange"])
    game.placeTown(1, 7, 8, color["Orange"])
    game.placeRoad(7, 8, color["Orange"])
    game.placeRoad(20, 8, color["Orange"])

    game.placeTown(6, 7, 18, color["White"])
    game.placeRoad(18, 7, color["White"])
    game.placeRoad(18, 19, color["White"])
    game.placeTown(2, 11, 10, color["White"])
    game.placeRoad(11, 10, color["White"])
    game.placeRoad(25, 10, color["White"])
    
    game.startGame()
    game.nextTurn()

    while (running):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screenX, screenY = screen.get_size()
        center = (screenX / 2, screenY / 2)
        scaleX, scaleY = (screenX / screenDimention[0] * 2, screenY / screenDimention[1] * 2)
        
        gameBoard.fill("blue")
        player0.fill("grey")
        player1.fill("grey")
        player2.fill("grey")
        player3.fill("grey")

        game.display(gameBoard, [player0,player1,player2,player3])

        displayBoard = pygame.transform.scale_by(gameBoard, min(scaleY, scaleX))
        displayP3 = pygame.transform.scale_by(player3, min(scaleY, scaleX)/2)
        displayP2 = pygame.transform.scale_by(player2, min(scaleY, scaleX)/2)
        displayP1 = pygame.transform.scale_by(player1, min(scaleY, scaleX)/2)
        displayP0 = pygame.transform.scale_by(player0, min(scaleY, scaleX)/2)

        screen.fill("blue")
        screen.blit(displayBoard, (center[0] - displayBoard.get_width()/2, center[1] - displayBoard.get_height()/2))
        screen.blit(displayP0, (0, 0))
        screen.blit(displayP1, (screenX - displayP1.get_width(), 0))
        screen.blit(displayP2, (0, screenY - displayP2.get_height()))
        screen.blit(displayP3, (screenX - displayP3.get_width(), screenY - displayP3.get_height()))

        pygame.display.flip()

        clock.tick(30)  # limits FPS to 60

    pygame.quit()

class Game():
    def __init__(self):
        self.setup = True
        self.currentTurn = 0
        self.gameGrid = HexGrid()
        self.gameGrid.createGrid((200,200))
        self.players = [Player(0), Player(1), Player(2), Player(3)]
        self.font = pygame.font.SysFont("Ariel", 40)

    def startGame(self):
        self.setup = False

    def placeRoad(self, tile1:int, tile2:int, player:int) -> bool:
        if (self.setup):
            self.gameGrid.addRoad(tile1, tile2, player)
            return True
        if (player != self.currentTurn):
            return False
        if (self.players[self.currentTurn].payCards([1,0,0,1,0])):
            self.gameGrid.addRoad(tile1, tile2, player)
            return True
        return False

    def placeTown(self, tile1:int, tile2:int, tile3:int, player:int) -> bool:
        if (self.setup):
            self.gameGrid.addTown(tile1, tile2, tile3, player)
            return True
        if (player != self.currentTurn):
            return False
        if (self.players[self.currentTurn].payCards([1,1,1,1,0])):
            self.gameGrid.addTown(tile1, tile2, tile3, player)
            return True
        return False

    def display(self, surface:pygame.Surface, playerSurfaces:list):
        self.gameGrid.drawGrid(surface)
        for i in range(4):
            self.players[i].display(playerSurfaces[i], self.font)

    def nextTurn(self):
        self.currentTurn = (self.currentTurn + 1) % 4
        number = roll()
        print(number)
        self.distribute(number)

    def distribute(self, num: int):
        cards = self.gameGrid.harvestRecources(num)
        if (cards == None):
            return
        for i in range(4):
            self.players[i].addCards(cards[i])

def roll() -> int:
    return random.randint(1,6) + random.randint(1,6)

class Player():
    def __init__(self, num:int):
        self.hand:list[int] = [0,0,0,0,0]
        self.cardCount:int = 0
        self.playerNumber:int = num

    def addCards(self, cards:list[int]):
        for i in range(5):
            self.hand[i] += cards[i]
            self.cardCount += cards[i]

    def payCards(self, cardCost:list[int]) -> bool:
        for i in range(5):
            if (self.hand[i] < cardCost[i]):
                return False
        for i in range(5):
            self.hand[i] -= cardCost[i]
            self.cardCount -= cardCost[i]

    def getHand(self) -> list[int]:
        return self.hand
    
    def display(self, screen:pygame.Surface, font:pygame.font):
        playertext = font.render("Player{}".format(self.playerNumber+1), False, playerColor[self.playerNumber])
        screen.blit(playertext, (5, 5))

        text = "Wood: {0!s}\nSheep: {1}\nWheat: {2}\nBrick: {3}\nOre: {4}".format(*self.hand)
        lines = text.splitlines()
        for i in range(len(lines)):
            recourceText = font.render(lines[i], False, (0, 0, 0))
            screen.blit(recourceText, (5, 5 + (i + 1)* (recourceText.get_rect().height + 5)))
    
if (__name__ == "__main__"):
    main()