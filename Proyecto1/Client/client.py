from dotenv import dotenv_values
import Service_pb2_grpc
import Service_pb2
import requests
import json
import grpc
import math
import os

# Get .env variables
env_vars = dotenv_values(".env")

# Access variables
BLOCKSIZE = int(env_vars.get("BLOCKSIZE"))
NAMENODE = env_vars.get("NAMENODE")

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
        print(f"File upload in progress.")
        print(f"Name: {fileName}, Size: {fileSize} bytes")
    
    # Call NameNode to know the datanodes where to send the information
    url = NAMENODE + "/createFile"
    body = json.dumps({ "fileName": fileName, "totalParts": totalParts })
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url=url, data=body, headers=headers)

    if response.status_code == 200:
        responseBody = response.json()
        urlsDataNodesPrincipal = responseBody['urlsDataNodesPrincipal']
        urlsDataNodesCopy = responseBody['urlsDataNodesCopy']
    
        print(responseBody)

        # Part the file and send it
        partition(filePath, fileName, BLOCKSIZE, urlsDataNodesPrincipal, urlsDataNodesCopy)

    elif response.status_code == 500:
        responseBody = response.json()
        print(responseBody['message'])

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

def createPartition(partitionNumber,fileName,content, urlPrincipal, urlCopy):
    partitionName = "part-" + getPartitionNumber(partitionNumber)

    with grpc.insecure_channel(urlPrincipal) as channel:
        stub = Service_pb2_grpc.ProductServiceStub(channel)
        response = stub.sendFile(Service_pb2.fileRequest(content = content, urlCopy = urlCopy, fileName = fileName, partitionName = partitionName))
        print((response.status_code))
    
    if response.status_code == 200:
        url = NAMENODE + "/updateFilesDB"
        body = json.dumps({ "urlPrincipal": urlPrincipal, "fileName": fileName, "partitionName": partitionName })
        headers = {'Content-Type': 'application/json'}

        responseNameNode = requests.post(url=url, data=body, headers=headers)
        print(responseNameNode.status_code)

def createSinglePartition(partitionNumber,fileName,content, urlPrincipal, urlCopy):
    partitionName = "part-" + getPartitionNumber(partitionNumber)

    grpcWrite(urlPrincipal, content, fileName, partitionName)
    
    url = NAMENODE + "/updateFilesDB"
    body = json.dumps({ "urlPrincipal": urlPrincipal, "fileName": fileName, "partitionName": partitionName })
    headers = {'Content-Type': 'application/json'}

    responseNameNode = requests.post(url=url, data=body, headers=headers)
    print(responseNameNode.status_code)

def partition(file, fileName, blockSize, urlsDataNodesPrincipal, urlsDataNodesCopy):
    partitionNumber = 1

    with open(file, 'rb') as f:
        index = 0
        while True:
            block = f.read(blockSize)

            if not block:
                break
            
            createPartition(partitionNumber, fileName, block, urlsDataNodesPrincipal[index], urlsDataNodesCopy[index])
            partitionNumber += 1
            index += 1

#--------------------------------------------------------------#
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
def getCopyLastChunkUrl(fileName,partName):
    # Call NameNode to get the datanode that contains the copy chunk
    url = NAMENODE + "/getCopyURL"
    body = json.dumps({ "fileName": fileName, "partName":partName})
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url=url, data=body, headers=headers)

    if response.status_code == 200:
        responseBody = response.json()
        return responseBody['URL']
    else:
        return None

def saveWrittenPartitions(indexOfTheChunk,metadata,fileName,fileData,fileNumberOfParts,partNumber,content):
    urls = []

    indexOfTheChunk = getIndexFromMetadata(indexOfTheChunk, fileNumberOfParts)
    url = metadata[fileName][list(fileData.keys())[indexOfTheChunk]]
    urls.append(url)

    while True:
        indexOfTheChunk = getIndexFromMetadata(indexOfTheChunk, fileNumberOfParts)
        url = metadata[fileName][list(fileData.keys())[indexOfTheChunk]]
        
        if(urls[0] != url): #to search for a different node
            urls.append(url)
            createPartition(partNumber,fileName,content,urls[0],urls[1])
            break

        if(indexOfTheChunk == 0): #if there are no more nodes
            createSinglePartition(partNumber,fileName,content,url)
            break

    return indexOfTheChunk

def write(metadata):
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
    
    print("longitud del texto:", len(textComplete))
    
    index = len(textComplete)//BLOCKSIZE
    indexComplete = len(textComplete)/BLOCKSIZE
    print(index, indexComplete)
    i = 0
    partNumber = getPartNumber(filePartName)

    copyLastChunkUrl = getCopyLastChunkUrl(fileName,filePartName)
    if(copyLastChunkUrl == None):
        print("There was a problem, aborting")
        return
    
    while i <= index:

        if i == 0: 
            partName = 'part-'+getPartitionNumber(partNumber)
            grpcWrite(lastChunkUrl, textComplete[0:(i+1)*BLOCKSIZE], fileName, partName)
            grpcWrite(copyLastChunkUrl, textComplete[0:(i+1)*BLOCKSIZE], fileName, partName)
        elif index < indexComplete and i == index:
            indexOfTheChunk = saveWrittenPartitions(indexOfTheChunk,metadata,fileName,fileData,fileNumberOfParts,partNumber,textComplete[i*BLOCKSIZE:])
        else:
            indexOfTheChunk = saveWrittenPartitions(indexOfTheChunk,metadata,fileName,fileData,fileNumberOfParts,partNumber,textComplete[i*BLOCKSIZE:(i+1)*BLOCKSIZE])

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

def getIndexFromMetadata(index, listLength):
    if index == listLength - 1 or index == -1:
        return (0)
    else:
        return (index + 1)

def ls():
    # Call NameNode to know which files are up in the system
    url = NAMENODE + "/ls"

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
    url = NAMENODE + "/getParts"
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
    [1]. create a new file
    [2]. open file

    insert the NUMBER and press enter:"""

    try:
        option = int(input(menu))
        
        if(option == 0):
            ls()
        elif(option == 1):
            create_file()
        elif(option == 2):
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
