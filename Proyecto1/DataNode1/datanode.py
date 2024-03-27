import json
import os
from concurrent import futures
from threading import Thread

import grpc
import Service_pb2
import Service_pb2_grpc

HOST = 'localhost:23333'

class ProductService(Service_pb2_grpc.ProductServiceServicer):
    def read(self, request, context):
        print('request: llegó el archivo correctamente', request.fileName)
        response = Service_pb2.readResponse(status_code=200, response=b"Python server ClientSimpleMethod ok")
        return response

    def write(self, request, context):
        print('request: llegó el archivo correctamente', request.fileName, request.chunkUrl, request.data)
        response = Service_pb2.ResponseSimple(status_code=200)
        return response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Service_pb2_grpc.add_ProductServiceServicer_to_server(ProductService(), server)
    server.add_insecure_port(HOST)
    print("Service is running... ")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()