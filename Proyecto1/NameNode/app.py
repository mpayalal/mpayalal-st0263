from flask import Flask, request, jsonify
import threading
import time
import json
import math
app = Flask(__name__)

BLOCKSIZE = 5000 # Revisar tamaño en Bytes!!

dataNodeIndex = 0

#-------------------------------------------------#
@app.route('/log-in', methods=['POST'])
def logIn():
    global dataNodeIndex
    req = request.get_json()
    ip = req.get("ip")

    with open("BD.json", "r") as archivo:
        datos = json.load(archivo)

    datos["datanodes"][dataNodeIndex] = [ip,time.time()]

    dataNodeIndex += 1

    with open("BD.json", "w") as archivo:
        archivo.write(datos)
        
    return jsonify({'message':'logged: '+str(dataNodeIndex),'index':dataNodeIndex}),202

@app.route('/ping', methods=['POST'])
def pong():
    with open("BD.json", "r") as archivo:
        datos = json.load(archivo)
    aliveNodes = datos["dataNodes"]
    req = request.get_json()
    nodeNumber = req.get("nodeNumber")

    if nodeNumber in aliveNodes:
        aliveNodes[nodeNumber][1] = time.time()
    else:
        return jsonify({'message':'node not found: '+str(nodeNumber)}),404

    print(aliveNodes)
    return jsonify({'message':'listening'}),200

def lookForDeaths():
    global flag
    with open("BD.json", "r") as archivo:
        datos = json.load(archivo)
    aliveNodes = datos["dataNodes"]
    TTL = 5

    while (flag):
        print("[*thread*]")
        for node in aliveNodes:
            timeUntilLastRequest = time.time() - aliveNodes[node][1]

            if timeUntilLastRequest > TTL*3:
                print("node: "+str(node)+" is death")#quitar
            else:
                print("node: "+str(node)+" is alive")
        time.sleep(10)
#-------------------------------------------------#

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
    flag = True
    lookForDeathsThread = threading.Thread(target=lookForDeaths)
    lookForDeathsThread.start()

    app.run(debug=True, port=5000)

    flag = False
    lookForDeathsThread.join()  