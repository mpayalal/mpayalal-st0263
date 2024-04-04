import os
import time
import json
import requests
from concurrent import futures
from threading import Thread

import grpc
import Service_pb2
import Service_pb2_grpc

SERVERURL = "http://127.0.0.1:5000"

class ProductService(Service_pb2_grpc.ProductServiceServicer):
    def read(self, request, context):
        print('request: llegó el archivo correctamente', request.fileName, request.partName)
        dataToSend = getFile(request.fileName, request.partName)
        response = Service_pb2.readResponse(status_code=200, response=dataToSend)
        return response

    def write(self, request, context):
        print('request: llegó el archivo correctamente', request.fileName, request.partName, request.data)
        writeFile(request.fileName, request.partName, request.data)
        response = Service_pb2.writeResponse(status_code=200)
        return response
    
    def clientSingle(self, request, context):
        print('request: llegó el archivo correctamente', request.resource, request.fileName)
        dataToSend = getFile(request.fileName, request.resource)
        response = Service_pb2.ResponseSimple(status_code=200, response = dataToSend)
        return response
    
    def sendFile(self, request, context):
        print('request: llegó el archivo correctamente', request.urlCopy, request.fileName, request.partitionName, request.content)
        saveFile(request.content, request.fileName, request.partitionName)
        createCopy(request.urlCopy, request.content, request.fileName, request.partitionName)
        response = Service_pb2.fileResponse(status_code=200)
        return response
    
    def copyPart(self, request, context):
        print('request: llegó el archivo correctamente')
        saveFile(request.content, request.fileName, request.partitionName)
        response = Service_pb2.fileResponse(status_code=200)
        return response

def getFile(fileName, filePart):
    filePath = 'files'
    partsPath = os.path.join(filePath,fileName)
    file = os.path.join(partsPath,filePart)
    print(file)

    with open(file, 'rb') as f:
        fileData = f.read()
        return(fileData)
    
def writeFile(fileName, filePart, data):
    filePath = 'files'
    partsPath = os.path.join(filePath,fileName)
    file = os.path.join(partsPath,filePart)

    with open(file, 'wb') as f:
        print(data)
        f.write(data)
        f.close

def sendPing(serverURL):
    global nodeNumber
    url = serverURL+"/ping"
    body= json.dumps({"nodeNumber":nodeNumber})
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url=url,data=body,headers=headers)
    
    # Verify the response
    if response.status_code == 200:
        print("[*THREAD*] - Server listened, answered: ", response.json()["message"])
    else:
        print("[*THREAD*] - Error while sending information:",response.json()["message"]," - code: ", response.status_code)
    
def saveFile(content, fileName, partitionName):
    partitionsPath = os.path.join("Partitions",fileName)
    if not os.path.exists(partitionsPath):
        os.mkdir(partitionsPath)
    
    partitionPath = os.path.join("Partitions", fileName, partitionName)

    with open(partitionPath, 'ab') as f:
        f.write(content)


def createCopy(urlCopy, content, fileName, partitionName):
    with grpc.insecure_channel(urlCopy) as channel:
        stub = Service_pb2_grpc.ProductServiceStub(channel)
        response = stub.copyPart(Service_pb2.copyRequest(content = content, fileName = fileName, partitionName = partitionName))
        print((response.status_code))
    
    if response.status_code == 200:
        url = SERVERURL + "/updateFilesDB"
        body = json.dumps({ "urlPrincipal": urlCopy, "fileName": fileName, "partitionName": partitionName })
        headers = {'Content-Type': 'application/json'}

        responseNameNode = requests.post(url=url, data=body, headers=headers)
        print(responseNameNode.status_code)

def mainPing():
    global flag
    while(flag):
        sendPing(SERVERURL)
        time.sleep(5)

def logIn(host):
    global nodeNumber
    url = SERVERURL+"/log-in"
    body= json.dumps({"ip":host})
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url=url,data=body,headers=headers)

    responseBody = response.json()
    nodeNumber = str(responseBody["index"])

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Service_pb2_grpc.add_ProductServiceServicer_to_server(ProductService(), server)

    host = 'localhost:'+input("add the port:")
    logIn(host)
    server.add_insecure_port(host)

    print("Service is running... ")

    pingThread = Thread(target=mainPing)
    pingThread.start()

    server.start()
    server.wait_for_termination()
    
    flag=False
    pingThread.join()

if __name__ == "__main__":
    flag = True
    nodeNumber = "0"

    serve()

