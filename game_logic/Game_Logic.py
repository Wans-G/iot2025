
import numpy as np
import random

playerColor = ["red", "orange", "white", "blue"]
recource = ["Wood", "Sheep", "Wheat", "Brick", "Ore"]
devCard = ["knight", "point", "road", "plenty", "monopoly"]
deckSetup = [14,5,2,2,2]

class Game():
    def __init__(self):
        self.setup = True
        self.currentTurn = 0
        self.players = [Player(0), Player(1), Player(2), Player(3)]
        self.lastRoll = 0
        self.board  = {2:[],3:[],4:[],5:[],6:[],8:[],9:[],10:[],11:[],12:[]}
        self.tiles = [0] * 19
        self.deck = None

    def getTurn(self) -> int:
        return self.currentTurn

    def startGame(self):
        if (self.setup == False):
            return
        self.setup = False

        ## Shuffle deck ##
        self.deck = []
        for i in range(5):
            self.deck += [i] *  deckSetup[i] 
        random.shuffle(self.deck)

        ## Get board setup ##

        self.nextTurn()
        self.currentTurn = 0
    
    def buildRoad(self, player:int) -> bool:
        if (self.setup):
            return False
        if (player != self.currentTurn):
            print("Not Players Turn")
            return False
        if (self.players[self.currentTurn].payCards([1,0,0,1,0])):
            return True
        print("Cant Afford")
        return False

    def placeTown(self, player:int) -> bool:
        if (self.setup):
            return False
        if (player != self.currentTurn):
            print("Not Players Turn")
            return False
        if (self.players[self.currentTurn].payCards([1,1,1,1,0])):
            return True
        print("Cant Afford")
        return False
    
    def buyDevCard(self, player:int) -> bool:
        if (self.setup):
            return False
        if (player != self.currentTurn):
            print("Not Players Turn")
            return False
        if (len(self.deck) > 0 and self.players[self.currentTurn].payCards([0,1,1,0,1])):
            card = self.deck.pop()
            self.players[self.currentTurn].addDevCard(card)
            return True
        print("Cant Afford")
        return False
    
    def trade(self, give:list[int], recieve:list[int], player:int):
        if (self.setup or player != self.currentTurn):
            return False
        return self.players[player].trade(give, recieve)

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
        for i in self.board[num]:
            cards = [0,0,0,0,0] # api call with i
            pass

        cards = self.gameGrid.harvestRecources(num)
        if (cards == None):
            return
        for i in range(4):
            self.players[i].addCards(cards[i])

    def gameInfo(self):
        return {"Current_Player": self.currentTurn,
                "Roll": self.lastRoll}
    
    def playerInfo(self, playerNumber:int):
        return self.players[playerNumber].playerInfo()

def roll() -> int:
    return random.randint(1,6) + random.randint(1,6)

class Player():
    def __init__(self, num:int):
        self.hand:list[int] = [0,0,0,0,0]
        self.cardCount:int = 0
        self.playerNumber:int = num
        self.devCards = [0,0,0,0,0]

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
        self.devCards[card] += 1

    def payCards(self, cardCost:list[int]) -> bool:
        if (not self.hasCards(cardCost)):
            return False
        for i in range(5):
            self.hand[i] -= cardCost[i]
            self.cardCount -= cardCost[i]
        return True

    def getHand(self) -> list[int]:
        return self.hand
    
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
    
    def playerInfo(self):
        return {"Player": self.playerNumber, 
                "Color": playerColor[self.playerNumber], 
                "Hand": {recource[0]: self.hand[0],
                         recource[1]: self.hand[1],
                         recource[2]: self.hand[2],
                         recource[3]: self.hand[3],
                         recource[4]: self.hand[4]},
                "Cards": {devCard[0]: self.devCards[0],
                          devCard[1]: self.devCards[1],
                          devCard[2]: self.devCards[2],
                          devCard[3]: self.devCards[3],
                          devCard[4]: self.devCards[4]}
                }
