from flask import Flask, jsonify
from Game_Logic import Game


id = -1


app = Flask(__name__)

current = Game()

#main
@app.route('/')
def index():
    return ("Hi")

@app.route('/join-game')
def joining():
    id+=1
    return jsonify(id=id)

@app.route('/build-road')
def road():
    return ('road')


@app.route('/build-house')
def house():
    return ('build-house')

@app.route('/build-city')
def city():
    return('build-city')

@app.route('/buy-dev-card')
def dev_card():
    return("dev-card")

@app.route('/end-turn')
def end_turn():
    #insert call to pi
    pass

@app.route('/game-info')
def get_game_info():
    return ("game-info")


@app.route('/admin')
def admin():
    return('admin')


if(__name__ == '__main__'):
    app.run(host='0.0.0.0',debug=True)