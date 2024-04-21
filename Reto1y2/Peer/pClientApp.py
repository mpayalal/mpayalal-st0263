import requests
import json

id = None
neighbour = None
pServerURL = "http://"


def check_neighbour():
    url = pServerURL + "/checkNeighbour"
    body = json.dumps({"id":id})
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url=url, data=body, headers=headers)

    # Verify the response
    if response.status_code == 200:
        responseBody = response.json()
        neighbour = responseBody.get("neighbourURL")
        print(responseBody['message']) 
        return neighbour
    
    else:
        print("Error while sending information:", response.status_code)
        return None

def upload():
    neighbour = check_neighbour()
    if neighbour != None:
        url = neighbour + "/fileToUpload"
        print(url)

        fileName = input("Write the file name:")
        body = json.dumps({"idUploader":id, "fileName":fileName})
        headers = {'Content-Type': 'application/json'}

        response = requests.post(url=url, data=body, headers=headers)

        # Verify the response
        if response.status_code == 200:
            responseBody = response.json()
            print(responseBody['message']) 
        
        else:
            print("Error while sending information:", response.status_code)

    else:
        Error = """
        ************************
        ERROR: You don't have a neighbour yet
        ************************"""
        print(Error)

def download():
    neighbour = check_neighbour()
    if neighbour != None:
        url = neighbour + "/askForFiles"

        response = requests.get(url=url)
        
        # Verify the response
        if response.status_code == 200:
            responseBody = response.json()
            filesList = responseBody['filesList']
            
            indexList = 0
            print("")
            for file in filesList:
                print( "[" + str(indexList) + "] -> " + file)
                indexList+=1

            try:
                option = int(input("Choose the file that you want to download:"))

                if (option < 0 or option > len(filesList)-1):
                    Error = """
                    ************************
                    ERROR: insert a valid number
                    ************************"""
                    print(Error)
                else:
                    url = neighbour + "/searchFileOwner"
                    body = json.dumps({"selectedFile":filesList[option]})
                    headers = {'Content-Type': 'application/json'}

                    response = requests.post(url=url, data=body, headers=headers)

                    # Verify the response
                    if response.status_code == 200:
                        responseBody = response.json()
                        ownerURL = responseBody['ownerURL']
                        
                        url = ownerURL + "/download"
                        body = json.dumps({"selectedFile":filesList[option]})
                        headers = {'Content-Type': 'application/json'}

                        response = requests.post(url=url, data=body, headers=headers)

                        responseBody = response.json()
                        print(responseBody.get("message"))

                    else:
                        print("Error while sending information:", response.status_code)


            except ValueError:
                Error = """
                ************************
                ERROR: insert a number
                ************************"""
                print(Error)

        else:
            print("Error while sending information:", response.status_code)
    
    else:
        Error = """
        ************************
        ERROR: You don't have a neighbour yet
        ************************"""
        print(Error)

def logout():
    url = pServerURL + "/notifyLogout"
    body = json.dumps({"id":id})
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url=url, data=body, headers=headers)

    # Verify the response
    if response.status_code == 200:
        responseBody = response.json()
        print(responseBody['message']) 
        exit(0)
    else:
        print("Error while sending information:"+ str(response.status_code) + ". Try again")

def display_menu():
    menu = """-------------------------------------
    What do you want to do:
    [1]. upload
    [2]. download
    [3]. logout

    insert the NUMBER and press enter:"""

    try:
        option = int(input(menu))

        if (option < 1 or option > 3):
            Error = """
            ************************
            ERROR: insert a valid number
            ************************"""
            print(Error)

        elif(option == 1):
            upload()

        elif(option == 2):
            download()

        elif(option == 3):
            logout()

    except ValueError:
        Error = """
        ************************
        ERROR: insert a number
        ************************"""
        print(Error)

if __name__ == '__main__':

    serverIp = input("Central server IP: ")
    url = "http://" + serverIp + ":5000/login"

    pServerIp = input("My server IP: ")
    pServerPort = input("My server Port:")
    pServerURL += pServerIp + ":" + pServerPort
    body = json.dumps({"ip":pServerIp, "port":pServerPort})

    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(url=url, data=body, headers=headers)

    # Verify the response
    if response.status_code == 200:
        responseBody = response.json()
        print(responseBody['message'])

        id = responseBody['id']
        neighbour = responseBody['neighbour']

        while(True):
            display_menu()

    else:
        print("Error while sending information:", response.status_code)