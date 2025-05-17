from picamera2 import Picamera2, Preview
from libcamera import Transform
from time import sleep

def capture():
    picam2 = Picamera2()
    picam2.preview_configuration.sensor.output_size = (2562,1944)
    picam2.preview_configuration.transform = Transform(hflip=False, vflip=False)

    picam2.configure("preview")

    picam2.start()
    sleep(2)

    picam2.capture_file("board.jpg")


    picam2.close()

