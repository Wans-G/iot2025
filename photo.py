from picamera2 import Picamera2, Preview
from libcamera import Transform
import requests
from time import sleep

def capture():
    picam2 = Picamera2()
    picam2.preview_configuration.sensor.output_size = (2562,1944)
    picam2.preview_configuration.transform = Transform(hflip=True, vflip=True)

    picam2.configure("preview")

    picam2.start()
    sleep(2)

    image = picam2.capture_image()


    picam2.close()
    return image

def preparePhoto():
    path = "/usr/project/board.jpg"
    
    fin = open(path, 'rb')

    key = 23

    image = fin.read()
    fin.close()

    image = bytearray(image)

    for index, value in enumerate(image):
        image[index] = value ^ key
    
    fin = open(path, 'wb')

    fin.write(image)
    fin.close()

def pleaseWork():
    print("Run")
    return "pleaseWork returned this"
    
while(1):
    url = "http://172.23.23.61:3000"
    my_game_obj
    waiting = requests.post("http://172.23.23.61:3000", json={'image':pleaseWork()})

    