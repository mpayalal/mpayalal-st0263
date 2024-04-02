import json
import os
from concurrent import futures
from threading import Thread
import requests
import time

import grpc
import Service_pb2
import Service_pb2_grpc

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

"""def sendPing(serverURL):
    global nodeNumber
    url = serverURL+"/ping"
    body= json.dumps({"nodeNumber":nodeNumber})
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url=url,data=body,headers=headers)
    
    # Verify the response
    if response.status_code == 200:
        print("[*THREAD*] - Server listened, answered: ", response.json()["message"])
    else:
        print("[*THREAD*] - Error while sending information:", response.status_code)
    

def mainPing():
    global flag
    while(flag):
        sendPing("http://127.0.0.1:5000")
        time.sleep(5)

def logIn(host):
    global nodeNumber
    url = "http://127.0.0.1:5000"+"/log-in"
    body= json.dumps({"ip":host})
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url=url,data=body,headers=headers)

    responseBody = response.json()
    nodeNumber = responseBody["index"]"""

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Service_pb2_grpc.add_ProductServiceServicer_to_server(ProductService(), server)

    host = 'localhost:23333'
    server.add_insecure_port(host)
    #logIn(host)
    print("Service is running... ")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    """flag = True
    nodeNumber = 0
    pingThread = Thread(target=mainPing)
    pingThread.start()"""

    serve()
    #getFile("archivo.txt", "part-0001")
    
    """flag=False
    pingThread.join()"""

