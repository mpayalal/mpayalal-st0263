from flask import Flask, request, jsonify
import math
app = Flask(__name__)

BLOCKSIZE = 5000 # Revisar tamaño en Bytes!!

@app.route('/uploadFile', methods = ['POST'])
def upload_file():

    # From the information sent, check how many parts are needed
    postRequest = request.get_json()
    fileSize = postRequest.get("fileSize")
    
    totalParts = math.ceil(fileSize/BLOCKSIZE)

    # Decide where each part will go and save that information

    return jsonify({ 'totalParts': totalParts }), 200

@app.route('/downloadFile', methods = ['POST'])
def download_file():
    pass


if __name__ == '__main__':
    app.run(debug=True, port=5000)