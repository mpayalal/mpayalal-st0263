from flask import Flask, request, jsonify
import threading
import time
import json
import random
app = Flask(__name__)

BLOCKSIZE = 1024 # Bytes

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
            for node in deathNodes:            dbData["dataNodes"].pop(node)
            if(len(deathNodes)):            updateDB(dbData)
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
@app.route('/getParts', methods = ['POST'])
def getParts():
    dbData = readDB()
    actualFiles = dbData["files"]

    req = request.get_json()
    fileName = req.get("fileName")

    if fileName in actualFiles:
        parts = {}
        for part in actualFiles[fileName]:
            idOwnerDataNode = actualFiles[fileName][part][0]
            ownerDataNode = dbData['dataNodes'][idOwnerDataNode]
            ipOwnerDataNode = ownerDataNode[0]
            parts[part] = ipOwnerDataNode
        return jsonify({'parts':parts}),200
    else:
        return jsonify({'parts':None}),404
#-------------------------------------------------#

# Arrange the datanodes in descending order according to the amount of files they ha
def files_per_node(dataNodeFiles):
    filesPerNode = {}
    for node, files in dataNodeFiles.items():
        totalFiles = sum(len(parts) for parts in files.values())
        filesPerNode[node] = totalFiles
    
    print(filesPerNode)
    sortedNodes = sorted(filesPerNode, key=filesPerNode.get)

    return sortedNodes

# Function to find how many parts should be in each node
def distribute_parts_to_nodes(sortedNodes, totalParts):
    totalNodes = len(sortedNodes)
    partsPerNode = totalParts // totalNodes
    remainder = totalParts % totalNodes

    partsDistribution = {node: partsPerNode for node in sortedNodes}
    for i in range(remainder):
        partsDistribution[sortedNodes[i]] += 1

    return partsDistribution

# Function to choose randomly where the copy of the files will be saved
def choose_random_nodes(partsDistribution, sortedNodes):
    dataNodesCopy = []
    for node, parts in partsDistribution.items():
        if parts > 0:
            for _ in range(parts):
                available_nodes = [n for n in sortedNodes if n != node]
                random_node = random.choice(available_nodes)
                dataNodesCopy.append(random_node)
    return dataNodesCopy

@app.route('/createFile', methods = ['POST'])
def create_file():

    # From the information sent, check how many parts are needed
    postRequest = request.get_json()
    totalParts = postRequest.get("totalParts")

    # Decide where each part will be saved
    dbData = readDB()
    dataNodeFiles = dbData["dataNodeFiles"]
    infoDataNodes =  dbData["dataNodes"]
    sortedNodes = files_per_node(dataNodeFiles)
    partsDistribution = distribute_parts_to_nodes(sortedNodes, totalParts)

    urlsDataNodesPrincipal = []
    urlsDataNodesCopy = []

    # Take the url for the principal DataNodes
    for node, parts in partsDistribution.items():
        nodeInfo = infoDataNodes[node]
        nodeUrl = nodeInfo[0]
        urlsDataNodesPrincipal.extend([nodeUrl] * parts)
    
    # Randomly select where each copy will be saved
    dataNodesCopy = choose_random_nodes(partsDistribution, sortedNodes)

    for i in range(len(dataNodesCopy)):
        nodeInfo = infoDataNodes[dataNodesCopy[i]]
        nodeUrl = nodeInfo[0]
        urlsDataNodesCopy.append(nodeUrl)

    return jsonify({ 'urlsDataNodesPrincipal': urlsDataNodesPrincipal, 'urlsDatasNodeCopy': urlsDataNodesCopy }), 200

if __name__ == '__main__':
    flag = True
    lookForDeathsThread = threading.Thread(target=lookForDeaths)
    lookForDeathsThread.start()

    app.run(debug=False, port=5000)

    flag = False
    lookForDeathsThread.join()  