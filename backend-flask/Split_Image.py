import PIL.Image
import numpy as np
import os

tileSize = 52 # vertical tile height / 2
tile_path = "game_logic/split_img"# output path
padding = 20

land = [(0,0),(1,0),(0,1),(-1,1),(-1,0),(0,-1),(1,-1),(2,-1),(2,0),(1,1),(0,2),(-1,2),(-2,2),(-2,1),(-2,0),(-1,-1),(0,-2),(1,-2),(2,-2)]
ocean = [(3,-2),(3,-1),(3,0),(2,1),(1,2),(0,3),(-1,3),(-2,3),(-3,3),(-3,2),(-3,1),(-3,0),(-2,-1),(-1,-2),(0,-3),(1,-3),(2,-3),(3,-3)]
position = land# + ocean

tile_pos = [(0,0)] * len(position)

def split(input:str, output:str):
    im = PIL.Image.open(input)

    # Create tile position array
    for i in range(len(position)):
        p = position[i]
        tile_pos[i] = getGridToScreen(p[0], p[1])

    # Create road position array

    # Tiles and Tokens
    for i in range(len(tile_pos)):
        box = centered_box(tile_pos[i], im.size, (tileSize+padding)*2)
        tile = im.crop(box)
        out = os.path.join(output, f'{i}_tile.jpg')
        tile.save(out)

def centered_box(pos:tuple, img_size:tuple, box_size:int) -> tuple:
    w, h = img_size
    x1 = max(0, pos[0] + w/2 - box_size/2)
    x2 = min(w, pos[0] + w/2 + box_size/2)
    y1 = max(0, pos[1] + h/2 - box_size/2)
    y2 = min(h, pos[1] + h/2 + box_size/2)
    return (x1, y1, x2, y2)

def getGridToScreen(q:int, r:int) -> tuple:
    xPos = int(tileSize * (np.sqrt(3) * float(q)  +  np.sqrt(3)/2.0 * float(r)))
    yPos = int(tileSize * 3.0/2.0 * float(r))
    return xPos, yPos

def checkNeighbor(pos1:tuple, pos2:tuple) -> bool:
    s1 = -(pos1[0] + pos1[1])
    s2 = -(pos2[0] + pos2[1])
    return {pos1[0] - pos2[0], pos1[1] - pos2[1], s1 - s2} == {0,1,-1}

def roadPosition(pos1:tuple, pos2:tuple) -> tuple:
    return ((pos1[0] + pos2[0])//2, (pos1[1] + pos2[1])//2)

def townPosition(pos1:tuple, pos2:tuple, pos3:tuple) -> tuple:
    return ((pos1[0] + pos2[0] + pos3[0])//3, (pos1[1] + pos2[1] + pos3[1])//3)

if __name__ == "__main__":
    split()