from flask import Flask, jsonify
import requests
from flask_cors import CORS
#from flask_socketio import SocketIO, emit
from pathlib import Path
import importlib.util
import time
from Game_Logic import Game

#Setting up location for image of board
current_dir = Path(__file__).resolve().parent
project_dir = current_dir.parent
game_logic_folder = project_dir / 'game_logic'
game_logic_file = game_logic_folder / 'Game_Logic.py'
photo_file = game_logic_folder / 'board.jpg'


'''
decrypt_mod = importlib.util.spec_from_file_location("decrypt.py", project_dir + "/decrypt.py")
decrypt = importlib.util.module_from_spec(decrypt_mod)
decrypt_mod.loader.exec_module(decrypt)
'''

player_id = 0


app = Flask(__name__)
CORS(app)
#socketsio = SocketIO(app, cors_allowed_origins='*')

session_user_map={}

current = Game()

#main
@app.route('/')
def index():
    return ("Hi")

@app.route('/join-game')
def joining():
    global player_id
    current_id = player_id
    player_id+=1
    if(player_id == 4):
        current.startGame()
    return jsonify(id=current_id)

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
    return jsonify(dice=roll["Roll"], player=roll[""])

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


@app.route('/game-info')
def get_game_info():
    return ("game-info")


@app.route('/admin')
def admin():
    return('admin')


def camera():
    print("starting to shoot a photo")
    r = requests.post('http://172.23.23.61:5000/take-photo')
    time.sleep(7)
    print('took photo')
    r2 = requests.get('http://172.23.23.61:5000/get-photo')
    image = bytearray(r2.content)
    global game_logic_folder
    global photo_file
    file = open(photo_file, 'wb')
    file.write(image)
    file.close()

if(__name__ == '__main__'):
    #socketsio.run(app, port=5000,debug=True)
    app.run(port=8000, debug=True)