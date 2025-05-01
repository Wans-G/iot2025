from Pieces_old import Tile
from Pieces_old import Road
from Pieces_old import Town
import numpy as np
import pygame
import random

grid:list[Tile] = [[None for i in range(7)] for k in range(7)]
tileSize = 32
land = [(0,0),(1,0),(0,1),(-1,1),(-1,0),(0,-1),(1,-1),(2,-1),(2,0),(1,1),(0,2),(-1,2),(-2,2),(-2,1),(-2,0),(-1,-1),(0,-2),(1,-2),(2,-2)]
ocean = [(3,-2),(3,-1),(3,0),(2,1),(1,2),(0,3),(-1,3),(-2,3),(-3,3),(-3,2),(-3,1),(-3,0),(-2,-1),(-1,-2),(0,-3),(1,-3),(2,-3),(3,-3)]
position = land + ocean


tokenOrder = [5,2,6,3,8,10,9,12,11,4,8,10,9,4,5,6,3,11]
test_map = [0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,4,4,4,5]

cube_direction_vectors = [(+1, 0, -1), (+1, -1, 0), (0, -1, +1), (-1, 0, +1), (-1, +1, 0), (0, +1, -1)]

class HexGrid():
    def __init__(self):
        self.roads:dict[frozenset:Road] = {}
        self.towns:dict[frozenset:Town] = {}

    def createGrid(self, center:tuple):
        i = 0
        t = 0
        random.shuffle(test_map)
        tokenOrder.reverse()
        for p in land:
            posX, posY = getGridToScreen(p[0], p[1])
            rec = test_map[i]
            self.setGrid(p, Tile((posX + center[0], posY + center[1]), rec, tokenOrder[t] if rec < 5 else 0, str(i)))
            if (rec < 5):
                t += 1
            i += 1
        for p in ocean:
            posX, posY = getGridToScreen(p[0], p[1])
            self.setGrid(p, Tile((posX + center[0], posY + center[1]), 6, 0, str(i)))
            i += 1

    def buildRoad(self, tile1:int, tile2:int, color:int):
        rs = self.connectedRoads(tile1, tile2, color)
        for r in rs:
            if (self.roads.__contains__(r) and self.roads[r].getColor() == color):
                return self.addRoad(tile1, tile2, color)
        return False

    def addRoad(self, tile1:int, tile2:int, color:int) -> bool:
        if (not checkNeighbor(position[tile1], position[tile2])):
            return False
        if (frozenset({tile1,tile2}) in self.roads):
            return False
        pos1 = self.getGrid(position[tile1]).getPosition()
        pos2 = self.getGrid(position[tile2]).getPosition()
        if (pos1[1] - pos2[1] == 0):
            angle = 0
        else:
            angle = np.round(np.rad2deg(np.tan((pos1[0] - pos2[0])/(pos1[1] - pos2[1]))) / 30)  * 30 + 90
        roadPos = ((pos1[0] + pos2[0]) / 2, (pos1[1] + pos2[1]) / 2)
        self.roads[frozenset({tile1, tile2})] = Road(roadPos, int(angle), color)
        return True

    def connectedRoads(self, tile1:int, tile2:int, color:int) -> list[int]:
        ns = getMutualNeighbors(position[tile1], position[tile2])
        for n in ns:
            town = self.towns[frozenset({tile1, tile2, position.index(n)})]
            if (town != None and not town.getColor() == color):
                ns.remove(n)
        ts = [position.index(n) for n in ns]
        return [frozenset({tile1, t}) for t in ts] + [frozenset({tile2, t}) for t in ts]

    def longestRoad(self, road:frozenset, color:int):
        
        pass

    def buildTown(self, tile1:int, tile2:int, tile3:int, color:int) -> bool:
        if (not self.townOnRoad({tile1,tile2,tile3}, color)):
            return False
        return self.addTown(tile1, tile2, tile3, color)

    def addTown(self, tile1:int, tile2:int, tile3:int, color:int) -> bool:
        if (not checkCorner(position[tile1], position[tile2], position[tile3])):
            return False
        if (frozenset({tile1,tile2,tile3}) in self.towns):
            return False
        if (len(self.towns) and not self.canPlaceTown([tile1, tile2, tile3])):
            return False
        pos1 = self.getGrid(position[tile1]).getPosition()
        pos2 = self.getGrid(position[tile2]).getPosition()
        pos3 = self.getGrid(position[tile3]).getPosition()
        townPos = ((pos1[0] + pos2[0] + pos3[0]) / 3, (pos1[1] + pos2[1] + pos3[1]) / 3)
        self.towns[frozenset({tile1,tile2,tile3})] = Town(townPos, color)
        return True

    def townOnRoad(self, pos:list[int], color:int) -> bool:
        tiles = [frozenset({pos[0], pos[1]}),frozenset({pos[1], pos[2]}),frozenset({pos[0], pos[2]})]
        return any([r for r in (set(tiles) & set(self.towns)) if r.getColor() == color])

    def canPlaceTown(self, pos:list[int]) -> bool:
        tiles = [frozenset({pos[0], pos[1]}),frozenset({pos[1], pos[2]}),frozenset({pos[0], pos[2]})]
        positions:list = [key for key in self.towns.keys() if (key.issuperset(tiles[0]) or key.issuperset(tiles[1]) or key.issuperset(tiles[2])) and key != pos]
        return len(positions) == 0

    def setGrid(self, pos, tile:Tile):
        grid[pos[0]+3][pos[1]+3] = tile

    def getGrid(self, pos) -> Tile:
        return grid[pos[0]+3][pos[1]+3]

    def drawGrid(self, screen:pygame.Surface):
        for p in position:
            self.getGrid(p).render(screen)

        for key in self.roads:
            self.roads[key].render(screen)
        
        for key in self.towns:
            self.towns[key].render(screen)


    def harvestRecources(self, number:int) -> list[list[int]]:
        if (number == 7 or number < 2 or number > 12):
            return None
        tiles = self.getToken(number)

        out = [[0]*5,[0]*5,[0]*5,[0]*5]

        for t in tiles:
            towns = [p for p in self.towns.keys() if int(t.getNumber()) in p]
            for p in towns:
                out[self.towns[p].getColor()][t.getRecource()] += (2 if self.towns[p].isCity() else 1)

        return out

    def getToken(self, number) -> list[Tile]:
        return [self.getGrid(p) for p in land if self.getGrid(p).getTokenValue() == number]

def getGridToScreen(q:int, r:int) -> tuple:
    xPos = int(tileSize * (np.sqrt(3) * float(q)  +  np.sqrt(3)/2.0 * float(r)))
    yPos = int(tileSize * 3.0/2.0 * float(r))
    return xPos, yPos

def checkNeighbor(pos1:tuple, pos2:tuple) -> bool:
    s1 = -(pos1[0] + pos1[1])
    s2 = -(pos2[0] + pos2[1])
    return {pos1[0] - pos2[0], pos1[1] - pos2[1], s1 - s2} == {0,1,-1}

def getMutualNeighbors(pos1:tuple, pos2:tuple) -> list[tuple]:
    if (not checkNeighbor(pos1, pos2)):
        return None
    n1 = getNeighbors(pos1)
    n2 = getNeighbors(pos2)
    return [p for p in n1 if n2.__contains__(p)]

def getNeighbors(pos:tuple) -> list[tuple]:
    return [(pos[0] + p[0], pos[1]+p[1]) for p in cube_direction_vectors]

def checkCorner(pos1:tuple, pos2:tuple, pos3:tuple) -> bool:
    s1 = -(pos1[0] + pos1[1])
    s2 = -(pos2[0] + pos2[1])
    s3 = -(pos3[0] + pos3[1])
    n1 = {pos1[0] - pos2[0], pos1[1] - pos2[1], s1 - s2} == {0,1,-1}
    n2 = {pos2[0] - pos3[0], pos2[1] - pos3[1], s2 - s3} == {0,1,-1}
    n3 = {pos1[0] - pos3[0], pos1[1] - pos3[1], s1 - s3} == {0,1,-1}
    return n1 and n2 and n3
