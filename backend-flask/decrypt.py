from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP



def decrypt(privateKey):

    path = '/usr/project/backend-flask/board.jpg'

    

    fin = open(path, 'rb')

    image = fin.read()
    fin.close()

    image = bytearray(image)
    cipher_rsa = PKCS1_OAEP.new(privateKey)
    image = cipher_rsa.decrypt(image)

    fin = open(path, 'wb')

    fin.write(image)
    fin.close()
