import os
import json
import requests
import grpc
import Service_pb2
import Service_pb2_grpc

nameNode = "http://127.0.0.1:5000"

def upload():
    filePath = input("Please enter the path of the file you want to upload: ")

    # Check if the file exists
    if not os.path.isfile(filePath):
        print("File not found, please try again")
        return

    # Take the name and size of the file
    with open(filePath, 'rb') as file:
        fileSize = len(file.read())
        fileName = os.path.basename(filePath)
        print(f"File uploaded successfully.")
        print(f"Name: {fileName}, Size: {fileSize} bytes")
    
    # Call NameNode to know how to partition the file
    url = nameNode + "/uploadFile"
    body = json.dumps({ "fileName": fileName, "fileSize": fileSize })
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url=url, data=body, headers=headers)

    if response.status_code == 200:
        responseBody = response.json()
        totalParts = responseBody['totalParts']
        # urlsDataNodesLeader = responseBody['urlsDataNodesLeader']
        # urlsDataNodesFollower = responseBody['urlsDataNodesFollower']

        print(totalParts)

    # Part the file - Juanfe
        
    
    # Send (by threads) each of the parts to their respective DataNodes


def download():
    pass


def read(metadata):
    while(1):
        mode = int(input('Select a mode: \n[1]. Read first chunk \n[2]. Read all file '))
        fileName = list(metadata.keys())[0]
        if mode == 1:
            fileData = metadata[fileName]
            firstChunkUrl = metadata[fileName][list(fileData.keys())[0]]
            file = readOne(fileName, firstChunkUrl)
            return file
        elif mode == 2:
            file = readAll(fileName, metadata)
            return file
        else:
            error = """
            ************************
            ERROR: insert a valid number
            ************************"""
            print(error)

def readOne(fileName, url):
    fileChunk = b''
    with grpc.insecure_channel(url) as channel:
        stub = Service_pb2_grpc.ProductServiceStub(channel)
        response = stub.read(Service_pb2.readRequest(fileName = fileName))
        fileChunk = response.response
    return (fileChunk)

def readAll(fileName, metadata):
    fileData = metadata 
    fileComplete = b''
    for file in fileData[fileName]:
        response = readOne(fileName, fileData[fileName][file])
        fileComplete = fileComplete + response
    return fileComplete

def write(metadata):
    BLOCKSIZE = 1024
    indexOfTheChunk = -1
    fileName = list(metadata.keys())[0]
    fileData = metadata[fileName]
    fileNumberOfParts = len(list(fileData.keys()))
    filePartName = list(fileData.keys())[indexOfTheChunk]
    lastChunkUrl = metadata[fileName][list(fileData.keys())[indexOfTheChunk]]
    with grpc.insecure_channel(lastChunkUrl) as channel:
        stub = Service_pb2_grpc.ProductServiceStub(channel)
        response = stub.clientSingle(Service_pb2.RequestSimple(resource = filePartName))
        print(response.status_code, response.response)
    
    newText = bytes(input('Write what you want to add to the file\n'), 'utf-8') 
    textComplete = response.response + newText
    print(textComplete , type(textComplete))
    
    index = len(textComplete)//BLOCKSIZE
    indexComplete = len(textComplete)/BLOCKSIZE
    i = 0
    partNumber = getPartNumber(filePartName)
    while i <= index:
        if index < indexComplete and i == index:
            indexOfTheChunk = getIndexFromMetadata(indexOfTheChunk, fileNumberOfParts)
            url = metadata[fileName][list(fileData.keys())[indexOfTheChunk]]
            partName = 'part-'+getPartitionNumber(partNumber)
            grpcWrite(url, textComplete[i*BLOCKSIZE:], fileName, partName)
        elif i == 0:
            partName = 'part-'+getPartitionNumber(partNumber)
            grpcWrite(lastChunkUrl, textComplete[0:(i+1)*BLOCKSIZE], fileName, partName)
            partNumber = partNumber + 1
        else:
            indexOfTheChunk = getIndexFromMetadata(indexOfTheChunk, fileNumberOfParts)
            url = metadata[fileName][list(fileData.keys())[indexOfTheChunk]]
            partName = 'part-'+getPartitionNumber(partNumber)
            grpcWrite(lastChunkUrl, textComplete[i*BLOCKSIZE:(i+1)*BLOCKSIZE], fileName, partName)
            partNumber = partNumber + 1
        i = i + 1

def grpcWrite(url, data, fileName, partName):
    with grpc.insecure_channel(url) as channel:
                stub = Service_pb2_grpc.ProductServiceStub(channel)
                response = stub.write(Service_pb2.writeRequest(fileName = fileName, data = data, partName = partName))
                print((response.status_code))
                
def getPartNumber(partName):
    number = int(partName[5:])
    return (number)

def getPartitionNumber(partitionNumber):
    partitionNumberStr = str(partitionNumber)

    partition0s = partitionNumber/1000

    if(partitionNumber//10000 > 0):
        print("Partition number is greater than 4 digits")
    else:
        while(int(partition0s) == 0):
            partitionNumberStr = "0" + partitionNumberStr
            partition0s *= 10

    return partitionNumberStr

def getIndexFromMetadata(index, listLength):
    if index == listLength - 1 or index == -1:
        return (0)
    else:
        return (index + 1)

def display_menu():
    menu = """-------------------------------------
    What do you want to do:
    [1]. upload
    [2]. download
    [3]. read
    [4]. write

    insert the NUMBER and press enter:"""

    try:
        option = int(input(menu))
        
        if(option == 1):
            upload()
        elif(option == 2):
            download()
            print('download')
        elif(option == 3):
            data = '{"archivo.txt": {"part-0001": "localhost:23333","part-0002": "localhost:23334","part-0003": "localhost:23334", "part-0004": "localhost:23333"} }'
            data = json.loads(data)
            print(read(data))
        elif(option == 4):
            data = '{"archivo.txt": {"part-0001": "localhost:23333","part-0002": "localhost:23334","part-0003": "localhost:23334", "part-0004": "localhost:23333"} }'
            data = json.loads(data)
            write(data)
            
        else:
            Error = """
            ************************
            ERROR: insert a valid number
            ************************"""
            print(Error)
            
    except ValueError:
        Error = """
        ************************
        ERROR: insert a number
        ************************"""
        print(Error)


if __name__ == '__main__':

    while(True):
        display_menu()
