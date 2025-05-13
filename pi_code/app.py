#This is the Flask app to run on the PI. 

from flask import Flask, jsonify, send_file, make_response
from flask_cors import CORS
import photo
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_0AEP


app = Flask(__name__)
CORS(app)

publicKey = None

@app.route("/initial/<public>", methods=['POST'])
def initial(public):
    global publicKey
    publicKey = public

@app.route("/take-photo", methods=['POST'])
def take_photo():
    try:
        photo.capture()
        cipher_rsa = PKCS1_0AEP.new(publicKey)
        path = path = "/usr/project/board.jpg"
        fin = open(path, 'rb')
        image = fin.read()
        fin.close()
        image = bytearray(image)
        encrypted_image = cipher_rsa.encrypt(image)
        fin = open(path, 'wb')
        fin.write(encrypted_image)
        fin.close()
        return jsonify(action=True)
    except:
        return jsonify(action=False)


@app.route("/get-photo", methods=['GET'])
def get_photo():
    try:
        
        path = "/usr/project/board.jpg"
        response = make_response(send_file(path, mimetype='image/jpeg'))
        response.headers.add('Access-Control-Allow-Origin','*')
        return response
    except:
        return jsonify(error="Failed to get the photo"),500


if(__name__ == '__main__'):
    app.run(host="172.23.23.61", port=5000,debug=True)