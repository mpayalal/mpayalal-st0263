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


def read(metadata, mode):
    mode = mode
    fileName = list(metadata.keys())[0]
    if mode == 1:
        readSequential(fileName, metadata)
    elif mode == 2:
        readAll(fileName, metadata)
    else:
        error = """
        ************************
        ERROR: insert a valid number
        ************************"""
        print(error)


def readOne(fileName, url, partName):
    fileChunk = b''
    with grpc.insecure_channel(url) as channel:
        stub = Service_pb2_grpc.ProductServiceStub(channel)
        print(partName)
        response = stub.read(Service_pb2.readRequest(fileName = fileName, partName = partName))
        fileChunk = response.response
    return (fileChunk)

def readSequential(fileName, metadata):
    fileData = metadata[fileName]
    listOfParts = list(fileData.keys())
    partIndex = 0
    while 1:
        print(readOne(fileName, fileData[listOfParts[partIndex]], listOfParts[partIndex]))
        action = int(input("""
        Which part do you want to read:
        [1]. next part
        [2]. previous part
        [0]. to exit
        Insert the NUMBER and press enter: """))
        if action == 1:
            if partIndex == len(listOfParts)-1:
                print('This is the last part')
            else:
                partIndex = partIndex + 1
        elif action == 2:
            if partIndex == 0:
                print('This is the first part')
            else:
                partIndex = partIndex - 1
        elif action == 0:
            print('entra al break')
            break
        else:
            error = """
            ************************
            ERROR: insert a valid number
            ************************"""
            print(error)

def readAll(fileName, metadata):
    fileData = metadata 
    fileComplete = b''
    for file in fileData[fileName]:
        response = readOne(fileName, fileData[fileName][file], file)
        fileComplete = fileComplete + response
    print(fileComplete)
#--------------------------------------------------------------#
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
        response = stub.clientSingle(Service_pb2.RequestSimple(resource = filePartName, fileName=fileName))
        print(response.status_code)
    
    newText = bytes(input('Write what you want to add to the file\n'), 'utf-8')
    textComplete = response.response + newText.decode('unicode-escape').encode('utf-8')
    
    print("longitud del testo:", len(textComplete))
    
    index = len(textComplete)//BLOCKSIZE
    indexComplete = len(textComplete)/BLOCKSIZE
    print(index, indexComplete)
    i = 0
    partNumber = getPartNumber(filePartName)
    while i <= index:
        if i == 0: 
            partName = 'part-'+getPartitionNumber(partNumber)
            grpcWrite(lastChunkUrl, textComplete[0:(i+1)*BLOCKSIZE], fileName, partName)
            partNumber = partNumber + 1
            
        elif index < indexComplete and i == index:
            indexOfTheChunk = getIndexFromMetadata(indexOfTheChunk, fileNumberOfParts)
            url = metadata[fileName][list(fileData.keys())[indexOfTheChunk]]
            partName = 'part-'+getPartitionNumber(partNumber)
            grpcWrite(url, textComplete[i*BLOCKSIZE:], fileName, partName)
            partNumber = partNumber + 1
        else:
            indexOfTheChunk = getIndexFromMetadata(indexOfTheChunk, fileNumberOfParts)
            url = metadata[fileName][list(fileData.keys())[indexOfTheChunk]]
            partName = 'part-'+getPartitionNumber(partNumber)
            grpcWrite(url, textComplete[i*BLOCKSIZE:(i+1)*BLOCKSIZE], fileName, partName)
            partNumber = partNumber + 1
        i = i + 1

def grpcWrite(url, data, fileName, partName):
    with grpc.insecure_channel(url) as channel:
                stub = Service_pb2_grpc.ProductServiceStub(channel)
                response = stub.write(Service_pb2.writeRequest(fileName = fileName, data = data, partName = partName))
                print((response.status_code))
                
def getPartNumber(partName):
    number = int(partName[5:9])
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
            
            print(fileData)

            if(option == 1):
                read(fileData, option)
                pass
            elif(option == 2):
                read(fileData, option)
                pass
            elif(option == 3):
                write(fileData)
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
    [1]. upload
    [2]. download
    [3]. read
    [4]. open file

    insert the NUMBER and press enter:"""

    try:
        option = int(input(menu))
        
        if(option == 0):
            ls()
        elif(option == 1):
            upload()
        elif(option == 2):
            download()
            print('download')
        elif(option == 3):
            data = '{"archivo.txt": {"chunk-1": "localhost:23333","chunk-2": "localhost:23334","chunk-3": "localhost:23334", "chunk-4": "localhost:23333"} }'
            data = json.loads(data)
            print(read(data))
        elif(option == 4):
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
