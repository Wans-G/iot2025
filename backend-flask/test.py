import requests
import time
from pathlib import Path


current_dir = Path(__file__).resolve().parent
project_dir = current_dir.parent
game_logic_folder = project_dir / 'game_logic'
photo_file = game_logic_folder / 'board.jpg'



r = requests.post('http://172.23.23.61:5000/take-photo')
time.sleep(7)
r2 = requests.get('http://172.23.23.61:5000/get-photo')
image = bytearray(r2.content)
file = open(photo_file, 'wb')
file.write(image)
file.close()
'''
print("starting to shoot a photo")
r = requests.post('http://192.168.0.177:5000/take-photo')
time.sleep(7)
print('took photo')
r2 = requests.get('http://192.168.0.177:5000/get-photo')
image = bytearray(r2.content)
#game_logic_folder
#photo_file
file = open(photo_file, 'wb')
file.write(image)
file.close()
'''