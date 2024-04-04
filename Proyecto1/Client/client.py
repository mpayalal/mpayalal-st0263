import os
import json
import grpc
import math
import requests
import Service_pb2
import Service_pb2_grpc

nameNode = "http://127.0.0.1:5000"
BLOCKSIZE = 1024 # Bytes

def create_file():
    filePath = input("Please enter the path of the file you want to upload: ")

    # Check if the file exists
    if not os.path.isfile(filePath):
        print("File not found, please try again")
        return

    # Take the name and size of the file, and find how many partitions are needed.
    with open(filePath, 'rb') as file:
        fileSize = len(file.read())
        fileName = os.path.basename(filePath)
        totalParts = math.ceil(fileSize/BLOCKSIZE)
        print(f"File uploaded successfully.")
        print(f"Name: {fileName}, Size: {fileSize} bytes")
    
    # Call NameNode to know the datanodes where to send the information
    url = nameNode + "/createFile"
    body = json.dumps({ "fileName": fileName, "totalParts": totalParts })
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url=url, data=body, headers=headers)

    if response.status_code == 200:
        responseBody = response.json()
        urlsDataNodesPrincipal = responseBody['urlsDataNodesPrincipal']
        urlsDataNodesCopy = responseBody['urlsDataNodesCopy']
    
    print(responseBody)

    # Part the file and send it

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
        with grpc.insecure_channel(fileData[fileName][file]) as channel:
            stub = Service_pb2_grpc.ProductServiceStub(channel)
            response = stub.read(Service_pb2.readRequest(fileName = fileName))
            fileComplete = fileComplete + response.response
    return fileComplete
#--------------------------------------------------------------#    
def ls():
    # Call NameNode to know which files are up in the system
    url = nameNode + "/ls"

    response = requests.get(url=url)

    if response.status_code == 200:
        responseBody = response.json()
        numFiles = responseBody['numFiles']

        if numFiles == 0:
            print("There are no files yet")
        else:
            files = responseBody['files']
            index = 1
            for file in files:
                print("["+str(index)+"]. "+file)
                index+=1
    else:
        print("Something happened, status code: ",response.status_code)
#--------------------------------------------------------------#    
def getParts(fileName):
    url = nameNode + "/getParts"
    body= json.dumps({"fileName":fileName})
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url=url,data=body,headers=headers)

    if response.status_code == 200:
        responseBody = response.json()
        parts = responseBody["parts"]

        return parts
    elif response.status_code == 404:
        print("File not found, check it before and try it again")
        return None
    else:
        print("Something happened, status code: ",response.status_code)
        return None

def openFile():
    fileName = input("Type the name (including the extension) of the file you want to open:")

    parts = getParts(fileName)

    if (parts):
        print(parts)
        print(type(parts))
        menu = """-------------------------------------
        How do you want to open the file:
        [1]. read by chunks mode
        [2]. read all the file
        [3]. write mode

        insert the NUMBER and press enter:"""

        try:
            option = int(input(menu))

            fileData = {fileName:parts}

            if(option == 1):
                #readByChunks(fileData)
                pass
            elif(option == 2):
                #readAll(fileData)
                pass
            elif(option == 3):
                #write(fileData) -> acá no se si pones todo el archivo o solo el último chunk
                pass
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

def display_menu():
    menu = """-------------------------------------
    What do you want to do:
    [0]. list files
    [1]. create a new file
    [2]. read
    [3]. open file

    insert the NUMBER and press enter:"""

    try:
        option = int(input(menu))
        
        if(option == 0):
            ls()
        elif(option == 1):
            create_file()
        elif(option == 2):
            data = '{"archivo.txt": {"chunk-1": "localhost:23333","chunk-2": "localhost:23334","chunk-3": "localhost:23334", "chunk-4": "localhost:23333"} }'
            data = json.loads(data)
            print(read(data))
        elif(option == 3):
            openFile()
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
