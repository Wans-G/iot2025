import firebase_admin
import firebase_admin.firestore
from firebase_admin import credentials
import sys
from pathlib import Path

#Setting up location for image of board
current_dir = Path(__file__).resolve().parent
project_dir = current_dir.parent

# Add project root to sys.path BEFORE attempting to import from it
sys.path.insert(0, str(project_dir))

# Now this import should work
from game_logic.Game_Logic import Game

class gameDatabase():
    def __init__(self):
        cred = credentials.Certificate("FirebaseKey.json")
        firebase_admin.initialize_app(cred)
        self.db = firebase_admin.firestore.client()
        self.coll = self.db.collection("IOTProject")

    def __del__(self):
        self.db.close()

    def saveGame(self, gameID:str, game:Game):
        self.coll.document(gameID).set({"game": game.gameInfo()})

        for i in range(4):
            info = game.playerInfo(i)
            self.coll.document(gameID).update({str(info["Player"]): info})

    def loadGame(self, gameID:str, game:Game):
        game.loadGame(self.coll.document(gameID).get().to_dict())

def main():
    game = Game()

    database = gameDatabase()

    database.loadGame("Game2", game)

    database.saveGame("Duplicate", game)

if __name__ == "__main__":
    main()