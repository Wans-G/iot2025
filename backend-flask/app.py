from dotenv import load_dotenv
load_dotenv()
from flask import Flask, jsonify
import requests
from flask_cors import CORS
#from flask_socketio import SocketIO, emit
from pathlib import Path
import importlib.util
import time
import sys
import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

#Setting up location for image of board
current_dir = Path(__file__).resolve().parent
project_dir = current_dir.parent

# Add project root to sys.path BEFORE attempting to import from it
sys.path.insert(0, str(project_dir))

# Now this import should work````````
from game_logic.Game_Logic import Game
from database import gameDatabase

game_logic_folder = project_dir / 'game_logic'
game_logic_file = game_logic_folder / 'Game_Logic.py'
photo_file = 'board.jpg'

pi = os.environ.get("PI_ADDRESS")


player_id = 0

app = Flask(__name__)
CORS(app)
#socketsio = SocketIO(app, cors_allowed_origins='*')

session_user_map={}

current = Game()
database = gameDatabase()


privateKey = RSA.generate(1024)
public = privateKey.publickey()

requests.post(f"http:{pi}:5000/initial/<{public}>")


#main
@app.route('/')
def index():
    return ("Hi")

@app.route('/join-game')
def joining():
    global player_id
    current_id = player_id
    player_id+=1
    return jsonify(id=current_id)

@app.route('/start-game')
def starting():
    camera()
    current.startGame()
    return jsonify({"success": True})

@app.route('/game-info')
def get_game_info():
    playerColor = ["red", "orange", "white", "blue"]

    game_info = {
        "roll": current.lastRoll,
        "players": [
            {
                "color": playerColor[player.playerNumber],
                "victoryPoints": player.victoryPoints,
                "hand": {
                    "lumber": player.hand[0],
                    "wool": player.hand[1],
                    "grain": player.hand[2],
                    "brick": player.hand[3],
                    "ore": player.hand[4]
                },
                "cards": {
                    0: player.devCards[0],  # knight
                    1: player.devCards[1],  # point
                    2: player.devCards[2],  # road building
                    3: player.devCards[3],  # year of plenty
                    4: player.devCards[4]   # monopoly
                }
            }
            for player in current.players
        ]
    }
    return jsonify(game_info)

@app.route('/build-road/<int:id>')
def road(id):
    global current
    attempt = current.buildRoad(id)
    return jsonify(action=attempt)


@app.route('/build-house/<int:id>')
def house(id):
    global current
    attempt = current.placeTown(id)
    return jsonify(action=attempt)

@app.route('/build-city/<int:id>')
def city(id):
    global current
    attempt=current.upgradeCity(id)
    return jsonify(action=attempt)

@app.route('/buy-dev-card/<int:id>')
def dev_card(id):
    global current
    attempt = current.buyDevCard(id)
    return jsonify(action=attempt)

@app.route('/use-dev-card/<int:card>/<int:player_id>')
def use_dev_card(card, player_id):
    if(card==3 or card==4):
        args = requests.args.get('args')
        args = list(map(int, args.split(','))) if args else []
        success = current.useDevCard(card, player_id, args)
    else:
        success = current.useDevCard(card, player_id)
    return jsonify({"success": success})

@app.route('/end-turn/<int:id>')
def end_turn(id):
    print("starting to end")
    global current
    if(current.getTurn() != id):
        return jsonify(action=False)
    camera()
    current.nextTurn()
    roll=current.gameInfo()
    #socketsio.emit('resource-update')
    return jsonify(dice=roll["Roll"], player=roll["Current_Player"])

@app.route('/update-resources')
def update_r():
    global current
    info = current.playerInfo()
    return info['Hand']

    
@app.route('/update/<int:id>')
def update_all(id):
    global current
    player_info = current.playerInfo(id)
    game_info = current.gameInfo()
    return jsonify(player=player_info, game=game_info)


@app.route('/admin')
def admin():
    return('admin')

@app.route('/save')
def save():
    try:
        database.saveGame("TestGame", current)
    except Exception as e:
        print(e)
        return jsonify({"success": False})
    return jsonify({"success": True})

@app.route('/load')
def load():
    try:
        database.loadGame("TestGame", current)
    except Exception as e:
        print(e)
        return jsonify({"success": False})
    return jsonify({"success": True})

def camera():
    print("starting to shoot a photo")
    r = requests.post(f'http://{pi}:5000/take-photo')
    time.sleep(7)
    print('took photo')
    r2 = requests.get(f'http://{pi}:5000/get-photo')
    image = bytearray(r2.content)
    global game_logic_folder
    global photo_file
    file = open(photo_file, 'wb')
    file.write(image)
    file.close()
    decrypt(privateKey)


def decrypt(privateKey):
    path = '/usr/project/backend-flask/board.jpg'
    fin = open(path, 'rb')
    image = fin.read()
    fin.close()
    
    image = bytearray(image)
    cipher_rsa = PKCS1_OAEP.new(privateKey)
    image = cipher_rsa.decrypt(image)

    fin = open(path, 'wb')
    fin.write(image)
    fin.close()

if(__name__ == '__main__'):
    app.run(port=8000, debug=True)