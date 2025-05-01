from flask import Flask, jsonify
import requests
from flask_cors import CORS
from game_logic.Game_Logic import Game

#from decrypt import Decrypt

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
    if (player_id == 4):
        current.startGame()

    return jsonify(id=current_id)

@app.route('/game-info')
def get_game_info():
    game_info = {
        "roll": current.lastRoll,
        "players": [
            {
                "id": player.playerNumber,
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
    #not seeing cities yet in game logic, will update later
    attempt=False
    return jsonify(action=attempt)

@app.route('/buy-dev-card/<int:id>')
def dev_card(id):
    global current
    if(current.getTurn() != id ):
        return jsonify(action=False)
    attempt = current.buyDevCard(id)
    return jsonify(action=attempt)

@app.route('/use-dev-card/<int:card>/<int:player_id>')
def use_dev_card(card, player_id):
    args = requests.args.get('args')
    args = list(map(int, args.split(','))) if args else []
    success = current.useDevCard(card, player_id, args)
    return jsonify({"success": success})

@app.route('/end-turn/<int:id>')
def end_turn(id):
    global current
    if(current.getTurn() != id):
        return jsonify(action=False)
    attempt = current.nextTurn()
    #call to pi here
    image = camera()
    #insert call to openai here
    return jsonify(action=attempt)

@app.route('/admin')
def admin():
    return('admin')


def camera():
    pass
    #image_enc = requests.get('http://pi-url-for-photo:3000').content
    #image = decrypt.decrypt(image_enc)
    #return image

if(__name__ == '__main__'):
    app.run(debug=True)