import random
from . import scan
from . import Split_Image
import json
import time

playerColor = ["red", "orange", "white", "blue"]
COLOR = {"red": 0, "orange": 1, "white": 2, "blue": 3}

RESOURCE = {"Wood":0, "Sheep":1, "Wheat":2, "Brick":3, "Ore":4}
#tile = ["Forest", "Pasture", "Field", "Hill", "Mountain", "Desert"]
devCard = ["knight", "point", "road", "plenty", "monopoly"]
deckSetup = [14,5,2,2,2]

SPLIT_PATH = "split_img"
INPUT = "board.jpg"


class Game():
    def __init__(self):
        self.setup = True
        self.currentTurn = 0
        self.players = [Player(0), Player(1), Player(2), Player(3)]
        self.lastRoll = 0
        self.board = {0:[], 2:[],3:[],4:[],5:[],6:[],8:[],9:[],10:[],11:[],12:[]}
        self.tiles = [0] * 19 #[4, 2, 0, 1, 0, 4, 1, 0, 4, 1, 3, 2, 0, 3, 1, 2, 3, 2, 0]
        #self.robber = 0
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

        # get image

        Split_Image.split(input=str(INPUT), output=str(SPLIT_PATH))
        for i in range(19):
            openai = None
            while (openai == None):
                openai = scan.analyze_tile_background(f"{SPLIT_PATH}/{i}_tile.jpg")
                time.sleep(1)
            print(openai)
            result = json.loads(openai)
            if (not result["number"] == 0):
                self.board[result["number"]].append(i)
                self.tiles[i] = RESOURCE[result["resource"]]
            time.sleep(1)
            

        print(self.board)
        print(self.tiles)

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
            self.players[self.currentTurn].addPoint()
            return True
        print("Cant Afford")
        return False
    
    def upgradeCity(self, player:int) -> bool:
        if (self.setup):
            return False
        if (player != self.currentTurn):
            print("Not Players Turn")
            return False
        if (self.players[self.currentTurn].payCards([0,0,2,0,3])):
            self.players[self.currentTurn].addPoint()
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
    
    #   0 - knight, remove a knight card
    #   1 - point,  cant ues, always false
    #   2 - road building, remove a card
    #   3 - year of plenty, needs an args array of two cards to add. ex: [0,1] wood and sheep
    #   4 - monopoly, needs an args array of 1 of card to take. ex: [4] takes all ore
    def useDevCard(self, card:int, player:int, args:list = []) -> bool:
        if (self.setup):
            return False
        if (player != self.currentTurn):
            print("Not Players Turn")
            return False
        if (card == 3 and len(args) < 2):
            return False 
        if (card == 4 and len(args) < 1):
            return False 
        if (self.players[player].useDevCard(card)):
            if (card == 3): # year of plenty
                self.players[player].addResourse(args[0], 1)
                self.players[player].addResourse(args[1], 1)
            if (card == 4): # monopoly
                sum = 0
                for p in self.players:
                    sum += p.loseCard(args[0])
                self.players[player].addResourse(args[0], sum)
            return True
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
        ## get image ##

        Split_Image.split(input=str(INPUT), output=str(SPLIT_PATH))

        for i in self.board[num]:
            result = None
            while (result == None):
                result = scan.analyze_single_tile(f"{SPLIT_PATH}/{i}_tile.jpg")
                time.sleep(1)
            print(result)
            result = json.loads(result)
            res = self.tiles[i]
            for t in result["vertices"]:
                p = COLOR[t["color"]]
                self.players[p].addResourse(res, t["type"])
            time.sleep(1)


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
        self.victoryPoints = 2

    def addPoint(self):
        self.victoryPoints += 1

    def getPoints(self) -> int:
        return self.victoryPoints

    def addCards(self, cards:list[int]):
        for i in range(5):
            self.hand[i] += cards[i]
            self.cardCount += cards[i]

    def addResourse(self, resource:int, number:int):
        self.hand[resource] += number
        self.cardCount += number

    def hasCards(self, cardCost:list[int]) -> bool:
        for i in range(5):
            if (self.hand[i] < cardCost[i]):
                return False
        return True
    
    def addDevCard(self, card:int):
        self.devCards[card] += 1
        if (card == 1): # vicory point
            self.victoryPoints += 1

    def useDevCard(self, card:int):
        if (self.devCards[card] > 0):
            if (card == 0):
                # Knight, player moves robber, steal one card
                self.devCards[card] -= 1
                return True
            if (card == 1):
                # Point, Cant use
                return False
            if (card == 2):
                # Road Building, place 2 roads
                self.devCards[card] -= 1
                return True
            if (card == 3):
                # Year of plenty, gain 2 resourses
                self.devCards[card] -= 1
                return True
            if (card == 4):
                # Monopoly gain all of 1 card type
                self.devCards[card] -= 1
                return True
        return False

    def payCards(self, cardCost:list[int]) -> bool:
        if (not self.hasCards(cardCost)):
            return False
        for i in range(5):
            self.hand[i] -= cardCost[i]
            self.cardCount -= cardCost[i]
        return True

    def loseCard(self, card:int) -> int:
        # Lose all of a card, return count, used for monopoly
        temp = self.hand[card]
        self.hand[card] = 0
        return temp

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
                "Points": self.victoryPoints,
                "Hand": {"Wood": self.hand[0],
                         "Sheep": self.hand[1],
                         "Wheat": self.hand[2],
                         "Brick": self.hand[3],
                         "Ore": self.hand[4]},
                "Cards": {devCard[0]: self.devCards[0],
                          devCard[1]: self.devCards[1],
                          devCard[2]: self.devCards[2],
                          devCard[3]: self.devCards[3],
                          devCard[4]: self.devCards[4]}
                }


if (__name__ == "__main__"):
    game = Game()
    game.startGame()

    print(game.gameInfo())
    for i in range(4):
        print(game.playerInfo(i))