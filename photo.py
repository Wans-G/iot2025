from picamera2 import Picamera2, Preview
from libcamera import Transform
from time import sleep

def capture():
    picam2 = Picamera2()
    picam2.preview_configuration.sensor.output_size = (2562,1944)
    picam2.preview_configuration.transform = Transform(hflip=True, vflip=True)

    picam2.configure("preview")

    picam2.start()
    sleep(2)

    picam2.capture_file("board.jpg")


    picam2.close()

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
    



capture()
preparePhoto()

