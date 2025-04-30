import pygame
from game_logic.Pieces_old import Tile
import numpy as np
from game_logic.Grid_old import HexGrid
import random

# Dependencies: Python, pygame, numpy


screenDimention = (1280, 820)
center = (screenDimention[0] / 2, screenDimention[1] / 2)

recource = {"Wood": 0, "Sheep": 1, "Wheat": 2, "Brick": 3, "Ore": 4, "Desert": 5}
color = {"Red": 0, "Orange": 1, "White": 2, "Blue": 3}
playerColor = ["red", "orange", "white", "blue"]

devCard = ["knight", "point", "road", "plenty", "monopoly"]
deckSetup = [14,5,2,2,2]

def main():
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode(screenDimention, pygame.RESIZABLE)
    gameBoard = pygame.Surface((400,400))
    player0 = pygame.Surface((320,280))
    player1 = pygame.Surface((320,280))
    player2 = pygame.Surface((320,280))
    player3 = pygame.Surface((320,280))
    gameInfo = pygame.Surface((320, 160))

    clock = pygame.time.Clock()
    running = True

    game = Game()

    game.placeTown(0, 1, 2, color["Red"])
    game.placeRoad(2, 1, color["Red"])
    game.placeTown(5, 6, 17, color["Red"])
    game.placeRoad(17, 6, color["Red"])

    game.placeTown(15, 16, 5, color["Blue"])
    game.placeRoad(15, 5, color["Blue"])
    game.placeTown(3, 4, 13, color["Blue"])
    game.placeRoad(13, 4, color["Blue"])

    game.placeTown(3, 12, 11, color["Orange"])
    game.placeRoad(12, 11, color["Orange"])
    game.placeTown(1, 7, 8, color["Orange"])
    game.placeRoad(7, 8, color["Orange"])

    game.placeTown(6, 7, 18, color["White"])
    game.placeRoad(18, 7, color["White"])
    game.placeTown(2, 11, 10, color["White"])
    game.placeRoad(11, 10, color["White"])

    while (running):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game.setup:
                        game.startGame() 
                    else:
                        game.nextTurn()
                if event.key == pygame.K_b:
                    print(game.placeRoad(6,18,0))
                    print(game.placeRoad(6,7,0))
                if event.key == pygame.K_c:
                    print(game.buyDevCard(game.getTurn()))


        # render
        screenX, screenY = screen.get_size()
        center = (screenX / 2, screenY / 2)
        scaleX, scaleY = (screenX / screenDimention[0] * 2, screenY / screenDimention[1] * 2)
        
        gameBoard.fill("blue")
        player0.fill("grey")
        player1.fill("grey")
        player2.fill("grey")
        player3.fill("grey")
        gameInfo.fill("grey")

        game.display(gameBoard, gameInfo, [player0,player1,player2,player3])

        displayBoard = pygame.transform.scale_by(gameBoard, min(scaleY, scaleX))
        displayP3 = pygame.transform.scale_by(player3, min(scaleY, scaleX)/2)
        displayP2 = pygame.transform.scale_by(player2, min(scaleY, scaleX)/2)
        displayP1 = pygame.transform.scale_by(player1, min(scaleY, scaleX)/2)
        displayP0 = pygame.transform.scale_by(player0, min(scaleY, scaleX)/2)
        displayInfo = pygame.transform.scale_by(gameInfo, min(scaleY, scaleX)/2)


        screen.fill("blue")
        screen.blit(displayBoard, (center[0] - displayBoard.get_width()/2, center[1] - displayBoard.get_height()/2))
        screen.blit(displayP0, (0, 0))
        screen.blit(displayP1, (screenX - displayP1.get_width(), 0))
        screen.blit(displayP2, (0, screenY - displayP2.get_height()))
        screen.blit(displayP3, (screenX - displayP3.get_width(), screenY - displayP3.get_height()))
        screen.blit(displayInfo, (screenX/2 - displayInfo.get_width()/2 , 0))

        pygame.display.flip()
    
        clock.tick(30)  # limits FPS to 30

        pass
    pygame.quit()

class Game():
    def __init__(self):
        self.setup = True
        self.currentTurn = 0
        self.gameGrid = HexGrid()
        self.gameGrid.createGrid((200,200))
        self.players = [Player(0), Player(1), Player(2), Player(3)]
        self.font = pygame.font.SysFont("Ariel", 40)
        self.lastRoll = 0
        self.deck = None

    def getTurn(self) -> int:
        return self.currentTurn

    def startGame(self):
        if (self.setup == False):
            return
        self.setup = False
        self.deck = []
        for i in range(5):
            self.deck += [i] *  deckSetup[i] 
        random.shuffle(self.deck)

        ## Get board setup ##

        self.nextTurn()
        self.currentTurn = 0
    
    def placeRoad(self, tile1:int, tile2:int, player:int) -> bool:
        if (self.setup):
            self.gameGrid.addRoad(tile1, tile2, player)
            return True
        if (player != self.currentTurn):
            print("Not Players Turn")
            return False
        if (self.players[self.currentTurn].payCards([1,0,0,1,0])):
            if (not self.gameGrid.buildRoad(tile1, tile2, player)):
                self.players[self.currentTurn].addCards([1,0,0,1,0])
                print("Can't Build Here")
                return False
            return True
        print("Cant Afford")
        return False

    def placeTown(self, tile1:int, tile2:int, tile3:int, player:int) -> bool:
        if (self.setup):
            self.gameGrid.addTown(tile1, tile2, tile3, player)
            return True
        if (player != self.currentTurn):
            return False
        if (self.players[self.currentTurn].payCards([1,1,1,1,0])):
            if (not self.gameGrid.addTown(tile1, tile2, tile3, player)):
                self.players[self.currentTurn].addCards([1,1,1,1,0])
                return False
            return True
        return False
    
    def buyDevCard(self, player:int) -> bool:
        if (self.setup):
            return False
        if (player != self.currentTurn):
            return False
        if (len(self.deck) > 0 and self.players[self.currentTurn].payCards([0,1,1,0,1])):
            card = self.deck.pop()
            self.players[self.currentTurn].addDevCard(card)
            return True
        return False
    
    def trade(self, give:list[int], recieve:list[int], player:int):
        if (self.setup or player != self.currentTurn):
            return False
        return self.players[player].trade(give, recieve)

    def display(self, screen:pygame.Surface, infoSurface:pygame.Surface, playerSurfaces:list):
        self.gameGrid.drawGrid(screen)  # Game board

        for i in range(4):  # Player info
            self.players[i].display(playerSurfaces[i], self.font)

        # Game info
        text = "Current turn: {}\nRoll: {}".format(playerColor[self.currentTurn], self.lastRoll)
        lines = text.splitlines()
        for i in range(len(lines)):
            recourceText = self.font.render(lines[i], False, (0, 0, 0))
            infoSurface.blit(recourceText, (5, 5 + (i)*(recourceText.get_rect().height + 5)))

    def nextTurn(self):
        self.currentTurn = (self.currentTurn + 1) % 4
        number = roll()
        print(number)
        self.lastRoll = number
        if (number == 7):
            pass
        else:
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
        self.hand = [0,0,0,0,0]

    def addCards(self, cards:list[int]):
        for i in range(5):
            self.hand[i] += cards[i]
            self.cardCount += cards[i]

    def hasCards(self, cardCost:list[int]) -> bool:
        for i in range(5):
            if (self.hand[i] < cardCost[i]):
                return False
        return True
    
    def addDevCard(self, card:int):
        self.hand[card] += 1

    def payCards(self, cardCost:list[int]) -> bool:
        if (not self.hasCards(cardCost)):
            return False
        for i in range(5):
            self.hand[i] -= cardCost[i]
            self.cardCount -= cardCost[i]
        return True

    def getHand(self) -> list[int]:
        return self.hand
    
    def display(self, screen:pygame.Surface, font:pygame.font):
        playertext = font.render("Player{}".format(self.playerNumber+1), False, playerColor[self.playerNumber])
        screen.blit(playertext, (5, 5))

        text = "Wood: {0}\nSheep: {1}\nWheat: {2}\nBrick: {3}\nOre: {4}".format(*self.hand)
        lines = text.splitlines()
        for i in range(len(lines)):
            recourceText = font.render(lines[i], False, (0, 0, 0))
            screen.blit(recourceText, (5, 5 + (i + 1)* (recourceText.get_rect().height + 5)))
    
    def trade(self, give:list[int], recieve:list[int]) -> bool:
        if (not self.hasCards(give)):   # Cant afford
            return False
        if (not sum(give) % 4 == 0):    # Not a multiple of 4
            return False
        if (not sum(give) / 4 == sum(recieve)):     # Not a 4-1 trade
            return False
        
        self.payCards(give)
        self.addCards(recieve)
        return True

if (__name__ == "__main__"):
    main()