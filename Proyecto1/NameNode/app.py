from flask import Flask, request, jsonify
from dotenv import dotenv_values
import Service_pb2_grpc
import Service_pb2
import threading
import random
import grpc
import time
import json

# Get .env variables
env_vars = dotenv_values(".env")

# Access variables
BLOCKSIZE = int(env_vars.get("BLOCKSIZE"))
PORT = int(env_vars.get("PORT"))
TTL = int(env_vars.get("TTL"))

#set global variables
app = Flask(__name__)
dataNodeIndex = 0
lock = threading.Lock()

#-------------------------------------------------#
def readDB():
    with open("DB.json", "r") as dataBase:
        dbData = json.load(dataBase)
    
    return dbData

def updateDB(dbData:dict,lock=lock):
    with lock:
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
    firstCopyFlag = False
    
    dbData = readDB()
    actualNodes = dbData["dataNodes"]
    #check to make a copy
    if(len(actualNodes) == 1):
        lonelyNodeId = next(iter(actualNodes))
        firstCopyFlag = True
    #log-in
    dbData["dataNodes"][dataNodeIndex] = [ip,time.time()]
    dbData["dataNodeFiles"][dataNodeIndex] = {}
    updateDB(dbData)

    if(firstCopyFlag):
        return jsonify({'message':'logged: '+str(dataNodeIndex),'index':dataNodeIndex, "lonelyNodeId":lonelyNodeId}),202
    else:
        return jsonify({'message':'logged: '+str(dataNodeIndex),'index':dataNodeIndex}),202

@app.route('/copyLonelyNode', methods=['POST'])
def copyLonelyNode():
    req = request.get_json()
    lonelyNodeId = req.get("lonelyNodeId")
    actualNodeURL = req.get("actualNodeURL")
    dbData=readDB()
    actualNodes = dbData["dataNodes"]

    #get the files that the other node has
    lonelyFiles = dbData["dataNodeFiles"][lonelyNodeId]
    print(lonelyFiles,"\n\n\n")
    #make a copy for each file 
    lonelyNodeURL = actualNodes[lonelyNodeId][0]
    print(lonelyNodeURL,"\n\n\n")

    for fileName in lonelyFiles:
        for partName in lonelyFiles[fileName]:
            print(actualNodeURL,"\n\n\n")
            print(fileName,"\n\n\n")
            print(partName,"\n\n\n")
            with grpc.insecure_channel(lonelyNodeURL) as channel:
                stub = Service_pb2_grpc.ProductServiceStub(channel)
                response = stub.distributeFiles(Service_pb2.distributeFilesRequest(urlCopy = actualNodeURL, fileName = fileName, partitionName = partName))
                print(response.status_code)

    return jsonify({'message':'logged COMPLETED: '+str(dataNodeIndex)}),202

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

    while (flag):
        print("[*thread*]")

        dbData = readDB()
        aliveNodes = dbData["dataNodes"]
        deathNodes = []

        for node in aliveNodes:
            timeUntilLastRequest = time.time() - aliveNodes[node][1]

            if timeUntilLastRequest > TTL*3:
                print("node: "+node+" is death")
                #needs to make a copy
                deathNodes.append(node)
            else:
                print("node: "+node+" is alive")

        for node in deathNodes:            
            dbData["dataNodes"].pop(node)

        if(len(deathNodes)):            
            updateDB(dbData)

        for node in deathNodes:
            makeNewCopy(node,deathNodes)

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

@app.route('/getCopyURL', methods = ['POST'])
def getCopyURL():
    dbData = readDB()

    req = request.get_json()
    fileName = req.get("fileName")
    partName = req.get("partName")

    partitionLocations = dbData["files"][fileName][partName]
    copyNodeOwner = partitionLocations[-1]

    copyURL = dbData["dataNodes"][copyNodeOwner][0]
    
    return jsonify({'URL':copyURL}),200
#-------------------------------------------------#

# Arrange the datanodes in descending order according to the amount of files they have
def filesPerNode(dataNodeFiles):
    filesPerNode = {}
    for node, files in dataNodeFiles.items():
        totalFiles = sum(len(parts) for parts in files.values())
        filesPerNode[node] = totalFiles
    
    print(filesPerNode)
    sortedNodes = sorted(filesPerNode, key=filesPerNode.get)

    return sortedNodes

# Function to find how many parts should be in each node
def distributePartsToNodes(sortedNodes, totalParts):
    totalNodes = len(sortedNodes)
    partsPerNode = totalParts // totalNodes
    remainder = totalParts % totalNodes

    partsDistribution = {node: partsPerNode for node in sortedNodes}
    for i in range(remainder):
        partsDistribution[sortedNodes[i]] += 1

    return partsDistribution

# Function to choose randomly where the copy of the files will be saved
def chooseRandomNodes(partsDistribution, sortedNodes):
    dataNodesCopy = []
    for node, parts in partsDistribution.items():
        if parts > 0:
            for _ in range(parts):
                available_nodes = [n for n in sortedNodes if n != node]
                random_node = random.choice(available_nodes)
                dataNodesCopy.append(random_node)
    return dataNodesCopy

@app.route('/createFile', methods = ['POST'])
def createFile():

    # From the information sent, check how many parts are needed
    postRequest = request.get_json()
    totalParts = postRequest.get("totalParts")

    # Decide where each part will be saved
    dbData = readDB()
    dataNodeFiles = dbData["dataNodeFiles"]
    infoDataNodes =  dbData["dataNodes"]

    if(len(infoDataNodes) < 2):
        return jsonify({ 'message': "Not enough DataNodes to save the files"}), 500
    
    sortedNodes = filesPerNode(dataNodeFiles)
    partsDistribution = distributePartsToNodes(sortedNodes, totalParts)

    urlsDataNodesPrincipal = []
    urlsDataNodesCopy = []

    # Take the url for the principal DataNodes
    for node, parts in partsDistribution.items():
        nodeInfo = infoDataNodes[node]
        nodeUrl = nodeInfo[0]
        urlsDataNodesPrincipal.extend([nodeUrl] * parts)
    
    # Randomly select where each copy will be saved
    dataNodesCopy = chooseRandomNodes(partsDistribution, sortedNodes)

    for i in range(len(dataNodesCopy)):
        nodeInfo = infoDataNodes[dataNodesCopy[i]]
        nodeUrl = nodeInfo[0]
        urlsDataNodesCopy.append(nodeUrl)

    return jsonify({ 'urlsDataNodesPrincipal': urlsDataNodesPrincipal, 'urlsDataNodesCopy': urlsDataNodesCopy }), 200

@app.route('/updateFilesDB', methods = ['POST'])
def updateFilesDB():
    postRequest = request.get_json()
    urlPrincipal = postRequest.get("urlPrincipal")
    partitionName = postRequest.get("partitionName")
    fileName = postRequest.get("fileName")

    dbData = readDB()

    for node, (url, lastTime) in dbData["dataNodes"].items():
        if url == urlPrincipal:
            nodeId = node
            break
    
    # Update files
    if fileName in dbData["files"]:
        if partitionName in dbData["files"][fileName]:
            FirstOrLast = random.randint(0,1)
            if(FirstOrLast):
                dbData["files"][fileName][partitionName].append(nodeId)
            else:
                dbData["files"][fileName][partitionName].insert(0,nodeId)
        else:
            dbData["files"][fileName][partitionName] = [nodeId]
    else:
        dbData["files"][fileName] = {partitionName: [nodeId]}

    # Update dataNodeFiles 
    if nodeId in dbData["dataNodeFiles"]:
        if fileName in dbData["dataNodeFiles"][nodeId]:
            FirstOrLast = random.randint(0,1)
            if(FirstOrLast):
                dbData["dataNodeFiles"][nodeId][fileName].append(partitionName)
            else:
                dbData["dataNodeFiles"][nodeId][fileName].insert(0,partitionName)

        else:
            dbData["dataNodeFiles"][nodeId][fileName] = [partitionName]
    else:
        dbData["dataNodeFiles"][nodeId] = {fileName: [partitionName]}

    updateDB(dbData)
    return jsonify({"message": "Data Base correctly updated"}), 200
#-------------------------------------------------#
def keepAliveNodes(dataNodeFiles, deathNodes):
    for node in deathNodes:
        if(node in dataNodeFiles):
            dataNodeFiles.pop(node)

    return dataNodeFiles

def makeNewCopy(nodeId,deathNodes):
    dbData = readDB()
    copyFlag = True
    dataNodes = dbData["dataNodes"]
    numberAliveNodes = len(dataNodes)

    if(numberAliveNodes == 0):
        print("no datanodes to keep save the files")
        dbData = {"dataNodes": {}, "files": {}, "dataNodeFiles": {}}
        updateDB(dbData)
        return
    
    if(numberAliveNodes == 1):
        print("not enough datanodes to keep save the files")
        copyFlag = False

    dataNodeFiles = dbData["dataNodeFiles"]
    deathDataNodeFiles = dataNodeFiles[nodeId]
    filesInDataNodes = dbData["files"]

    if(copyFlag):
        aliveDataNodeFiles = keepAliveNodes(dataNodeFiles,deathNodes)
        sortedNodes = filesPerNode(aliveDataNodeFiles)
        indexSelectedNode = 0

    for fileName in deathDataNodeFiles:
        for partName in deathDataNodeFiles[fileName]:
            #clear from db and get the owner URL  
            filesInDataNodes[fileName][partName].remove(nodeId)
            ownerId = filesInDataNodes[fileName][partName][0]
            ownerURL = dataNodes[ownerId][0]

            if(copyFlag):
                #select the following node
                selectedNodeId = sortedNodes[indexSelectedNode]
                #check that is not the same owner
                if(ownerId == selectedNodeId):
                    #increase the index of the selected node (or restart)
                    indexSelectedNode += 1
                    if indexSelectedNode == numberAliveNodes:
                        indexSelectedNode = 0

                    selectedNodeId = sortedNodes[indexSelectedNode]
                #send the order to copy the info
                selectedNodeURL = dataNodes[selectedNodeId][0]
                with grpc.insecure_channel(ownerURL) as channel:
                    stub = Service_pb2_grpc.ProductServiceStub(channel)
                    response = stub.distributeFiles(Service_pb2.distributeFilesRequest(urlCopy = selectedNodeURL, fileName = fileName, partitionName = partName))
                    print(response.status_code)

                    #update the DB
                    if(response.status_code == 200):
                        filesInDataNodes[fileName][partName].append(selectedNodeId)

                        if fileName in aliveDataNodeFiles[selectedNodeId]:
                            aliveDataNodeFiles[selectedNodeId][fileName].append(partName)
                        else:
                            aliveDataNodeFiles[selectedNodeId][fileName] = [partName,]

                #increase the index of the selected node (or restart)
                indexSelectedNode += 1
                if indexSelectedNode == numberAliveNodes:
                    indexSelectedNode = 0

    dbData["dataNodeFiles"] = keepAliveNodes(dataNodeFiles,[nodeId,])
    dbData["files"] = filesInDataNodes
    updateDB(dbData)

#-------------------------------------------------#

if __name__ == '__main__':
    flag = True
    lookForDeathsThread = threading.Thread(target=lookForDeaths)
    lookForDeathsThread.start()

    app.run(debug=False, port=PORT)

    flag = False
    lookForDeathsThread.join()  