import os
import json
import requests

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

def display_menu():
    menu = """-------------------------------------
    What do you want to do:
    [1]. upload
    [2]. download

    insert the NUMBER and press enter:"""

    try:
        option = int(input(menu))

        if (option < 1 or option > 2):
            Error = """
            ************************
            ERROR: insert a valid number
            ************************"""
            print(Error)

        elif(option == 1):
            upload()

        elif(option == 2):
            download()

    except ValueError:
        Error = """
        ************************
        ERROR: insert a number
        ************************"""
        print(Error)


if __name__ == '__main__':

    while(True):
        display_menu()
