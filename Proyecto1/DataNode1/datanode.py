import json
import os
from concurrent import futures
from threading import Thread
import requests
import time

import grpc
import Service_pb2
import Service_pb2_grpc

SERVERURL = "http://127.0.0.1:5000"

class ProductService(Service_pb2_grpc.ProductServiceServicer):
    def read(self, request, context):
        print('request: llegó el archivo correctamente', request.fileName)
        response = Service_pb2.readResponse(status_code=200, response=b"Python server ClientSimpleMethod ok")
        return response

    def write(self, request, context):
        print('request: llegó el archivo correctamente', request.fileName, request.chunkUrl, request.data)
        response = Service_pb2.ResponseSimple(status_code=200)
        return response
    
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
