from flask import Flask,jsonify,request
from time import time
import requests
import random
import json

class Peer:

    id = 0

    def __init__(self, ip, port, neighbour):

        self.id = Peer.id
        self.ip = ip
        self.port = port
        self.lastPing = time()
        self.neighbour = neighbour

        Peer.id += 1

server = Flask(__name__)

## FILES MANAGEMENT

# Dictionary <nameFile:[peerOwner]>
filesInPeers = {}

# Dictionary <peerOwner:[nameFile]>
peerHasFiles = {}

## PEERS MANAGEMENT

# Dictionary <idPeer:objPeer>
peers = {}

# Index when it enters to the system
peersIndexes = []

# Peer that didnt find a neighbour
pendingPeers = []

# Dictionary <idPeer:[idPeerWhoHasMeAsNeighbour]>
neighboursOfPeers = {}

def printDebug():
    for id in peers:
        peer = peers[id]
        print("id:"+str(peer.id)+"-N:"+str(peer.neighbour))

def printDebugFiles():

    for file in filesInPeers:
        print("file:"+file+"-List:")
        print(filesInPeers[file])
    print("----------------------------")
    for peer in peerHasFiles:
        print("Peer:"+str(peer)+"-List:")
        print(peerHasFiles[peer])

@server.route('/login', methods=['POST'])
def peer_login():
    newPeer = request.get_json()
    ip = newPeer.get("ip")
    port = newPeer.get("port")

    if len(peers) == 0:
        peer = Peer(ip, port, None)
        peers[peer.id] = peer
        peersIndexes.append(peer.id)
        pendingPeers.append(peer.id)

        printDebug() #DEBUG
        return jsonify({'message':'pending for neighbour assignment','id':peer.id,'neighbour':None}), 200
    
    else:
        indexNeighbour = peersIndexes[-1]

        peer = Peer(ip, port, indexNeighbour)
        peers[peer.id] = peer
        peersIndexes.append(peer.id)

        if indexNeighbour in neighboursOfPeers:
            neighboursOfPeers[indexNeighbour].append(peer.id)
        
        else:
            neighboursOfPeers[indexNeighbour] = [peer.id,]
        

        if len(pendingPeers) != 0:
            pendingPeer = peers[pendingPeers[-1]]

            if peer.id in neighboursOfPeers:
                neighboursOfPeers[peer.id].append(indexNeighbour)
            
            else:
                neighboursOfPeers[peer.id] = [indexNeighbour, ]

            pendingPeer.neighbour = peer.id
            pendingPeers.pop()

        printDebug() #DEBUG
        neighbour = peers[peer.neighbour]
        neighbourURL = "http://" + neighbour.ip + ":" + str(neighbour.port)
        return jsonify({'message':'Assigned neighbour [' + str(indexNeighbour) + ']', 'id':peer.id, 'neighbour':neighbourURL}), 200

@server.route('/logout', methods=['POST'])
def peer_logout():
    
    # remove files from de peer that leaves
    byePeer = request.get_json()
    id = byePeer.get('id')

    if id in peerHasFiles:
        for file in peerHasFiles[id]:
            filesInPeers[file].remove(id)

            if len(filesInPeers[file]) == 0:
                filesInPeers.pop(file)

        peerHasFiles.pop(id)

    peersIndexes.pop(peersIndexes.index(id))

    # reset neighbours
    print(neighboursOfPeers)
    if id in neighboursOfPeers:
        for peerId in neighboursOfPeers[id]:

            peer = peers[peerId]

            if len(peersIndexes) > 1:
                if peersIndexes[-1] != peer.id:
                    peer.neighbour = peersIndexes[-1]
                
                else:
                    peer.neighbour = peersIndexes[-2]

                if peer.neighbour in neighboursOfPeers:
                    neighboursOfPeers[peer.neighbour].append(peer.id)
                
                else:
                    neighboursOfPeers[peer.neighbour] = [peer.id,]

            else:
                peer.neighbour = None
                pendingPeers.append(peer.id)

        neighboursOfPeers.pop(id)

    if(peers[id].neighbour != None):
        neighboursOfPeers[peers[id].neighbour].pop(neighboursOfPeers[peers[id].neighbour].index(id))
        
    peers.pop(id)

    print(neighboursOfPeers)
    printDebug() #DEBUG
    printDebugFiles()
    return jsonify({'message':'Left peer [' + str(id) + ']'}), 200

@server.route('/upload', methods=['POST'])
def peer_upload():

    fileInformation = request.get_json()
    idUploader = fileInformation.get("idUploader")
    fileName = fileInformation.get("fileName")

    randomPosition = random.randint(0, len(peersIndexes)-1)
    
    if peersIndexes[randomPosition] == idUploader:
        if randomPosition == 0:
            idToUpload = peersIndexes[randomPosition+1]
        
        else:
            idToUpload = peersIndexes[randomPosition-1]
    
    else:
        idToUpload = peersIndexes[randomPosition]

    peerToUpload = peers[idToUpload]
    pServerURL = "http://" + peerToUpload.ip + ":" + str(peerToUpload.port)
    url = pServerURL + "/saveFile"
    body = json.dumps({"fileName":fileName})
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url=url, data=body, headers=headers)

    # Verify the response
    if response.status_code == 200:
        
        if fileName in filesInPeers:
            filesInPeers[fileName].append(idToUpload)
        
        else:
            filesInPeers[fileName] = [idToUpload,]

        if idToUpload in peerHasFiles:
            peerHasFiles[idToUpload].append(fileName)
        
        else:
            peerHasFiles[idToUpload] = [fileName,]

        printDebugFiles()

        return jsonify({'message':'Saved file ' + fileName + ' in peer[' + str(idToUpload) + ']'}), 200

    else:
        print("Error while sending information:", response.status_code)
        return jsonify({'message':'Error while sending information'}), response.status_code

@server.route('/sendFiles', methods=['GET'])
def send_files():

    filesList = [file for file in filesInPeers]

    return jsonify({'message':'returned list', "filesList":filesList}), 200

@server.route('/sendFileOwner', methods=['POST'])
def send_file_owner():

    fileResponse = request.get_json()
    file = fileResponse.get("selectedFile")

    ownerId = filesInPeers[file][0]
    owner = peers[ownerId]
    ownerURL = "http://" + owner.ip + ":" + str(owner.port)
    print(ownerURL)

    return jsonify({'message':'Owner found', "ownerURL":ownerURL}), 200

@server.route('/checkClientNeighbour', methods=['POST'])
def check_client_neighbour():

    clientRequest = request.get_json()
    clientId = clientRequest.get("id")

    peer = peers[clientId]

    neighbourId = peer.neighbour
    
    if neighbourId != None:
        neighbour = peers[neighbourId]
        neighbourURL = "http://" + neighbour.ip + ":" + str(neighbour.port)

    else:
        neighbourURL=None

    print(neighbourURL)
    return jsonify({'message':'Actual Neighbour', "neighbourURL":neighbourURL}), 200

if __name__ == '__main__':
    server.run(debug=True, port=5000)