from flask import Flask, jsonify
import requests
from flask_cors import CORS
from pathlib import Path
import importlib.util
import time
from Game_Logic import Game

#Getting the files from the other library
current_dir = Path(__file__).resolve().parent
project_dir = current_dir.parent
game_logic_folder = project_dir / 'game_logic'
game_logic_file = game_logic_folder / 'Game_Logic.py'


'''
decrypt_mod = importlib.util.spec_from_file_location("decrypt.py", project_dir + "/decrypt.py")
decrypt = importlib.util.module_from_spec(decrypt_mod)
decrypt_mod.loader.exec_module(decrypt)
'''

player_id = 0


app = Flask(__name__)
CORS(app)

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
    return jsonify(id=current_id)

@app.route('/build-road/<int:id>')
def road(id):
    global current
    if(current.getTurn() != id):
        attempt = False
        return jsonify(action=attempt)
    attempt = current.buildRoad(id)
    return jsonify(action=attempt)


@app.route('/build-house/<int:id>')
def house(id):
    global current
    if(current.getTurn() != id ):
        return jsonify(action=False)
    attempt = current.placeTown(id)
    return jsonify(action=attempt)

@app.route('/build-city/<int:id>')
def city(id):
    global current
    if(current.getTurn() != id):
        return jsonify(action=False)
    attempt=current.upgradeCity(id)
    return jsonify(action=attempt)

@app.route('/buy-dev-card/<int:id>')
def dev_card(id):
    global current
    if(current.getTurn() != id ):
        return jsonify(action=False)
    attempt = current.buyDevCard(id)
    return jsonify(action=attempt)

@app.route('/end-turn/<int:id>')
def end_turn(id):
    
    #global current
    #if(current.getTurn() != id):
        #return jsonify(action=False)
    camera()
    #attempt = current.nextTurn()
    #return jsonify(action=attempt)
    

@app.route('/game-info')
def get_game_info():
    return ("game-info")


@app.route('/admin')
def admin():
    return('admin')


def camera():
    r = requests.post('http://172.23.23.61:5000/take-photo')
    time.sleep(7)
    r2 = requests.get('http://172.23.23.61:5000/get-photo')
    image = r2.content
    global game_logic_folder
    file = open(game_logic_folder + "/board.jpg", 'wb')
    file.write(image)
    file.close()

if(__name__ == '__main__'):
    app.run(debug=True)
