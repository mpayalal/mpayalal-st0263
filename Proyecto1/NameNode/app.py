from flask import Flask, request, jsonify
import threading
import time
import json
import math
app = Flask(__name__)

BLOCKSIZE = 5000 # Revisar tamaño en Bytes!!

dataNodeIndex = 0

#-------------------------------------------------#
def readDB():
    with open("DB.json", "r") as dataBase:
        dbData = json.load(dataBase)
    
    return dbData

def updateDB(dbData:dict):
    with open("DB.json", "w") as dataBase:
        dbDataJson = json.dumps(dbData)
        dataBase.write(dbDataJson)
#-------------------------------------------------#
@app.route('/log-in', methods=['POST'])
def logIn():
    global dataNodeIndex
    dataNodeIndex += 1
    req = request.get_json()
    ip = req.get("ip")
    
    dbData = readDB()
    dbData["dataNodes"][dataNodeIndex] = [ip,time.time()]
    updateDB(dbData)
        
    return jsonify({'message':'logged: '+str(dataNodeIndex),'index':dataNodeIndex}),202

@app.route('/ping', methods=['POST'])
def pong():
    dbData = readDB()
    aliveNodes = dbData["dataNodes"]

    req = request.get_json()
    nodeNumber = req.get("nodeNumber")
    
    if nodeNumber in aliveNodes:
        dbData["dataNodes"][nodeNumber][1] = time.time()
        updateDB(dbData)
    else:
        return jsonify({'message':'node not found: '+str(nodeNumber)}),404

    return jsonify({'message':'listening'}),200

def lookForDeaths():
    global flag
    TTL = 5

    while (flag):
        print("[*thread*]")

        dbData = readDB()
        aliveNodes = dbData["dataNodes"]
        deathNodes = []

        for node in aliveNodes:
            timeUntilLastRequest = time.time() - aliveNodes[node][1]

            if timeUntilLastRequest > TTL*3:
                print("node: "+node+" is death")
                
                #makeNewCopy(node)

                deathNodes.append(node)
            else:
                print("node: "+node+" is alive")

        for node in deathNodes:
            dbData["dataNodes"].pop(node)

        if(len(deathNodes)):
            updateDB(dbData)

        time.sleep(10)
#-------------------------------------------------#
@app.route('/ls', methods = ['GET'])
def ls():
    dbData = readDB()
    actualFiles = dbData["files"]

    files = [fileName for fileName in actualFiles]
    numFiles = len(files)

    return jsonify({'numFiles':numFiles,'files':files}),200

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

    app.run(debug=False, port=5000)

    flag = False
    lookForDeathsThread.join()  