def decrypt():

    path = '/usr/project/board.jpg'

    key = 23

    fin = open(path, 'rb')

    image = fin.read()
    fin.close()

    image = bytearray(image)

    for index, value in enumerate(image):
        image[index] = value ^ key

    fin = open(path, 'wb')

    fin.write(image)
    fin.close()
