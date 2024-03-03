from flask import Flask,jsonify,request
import requests
import json

server = Flask(__name__)

fileList = []
serverURL="http://"

@server.route('/askForFiles', methods=['GET'])
def ask_for_files():

    url = serverURL + "/sendFiles"

    response = requests.get(url=url)
    
    # Verify the response
    if response.status_code == 200:
        responseBody = response.json()
        filesList = responseBody['filesList']
        return jsonify({'message':'returned list', "filesList":filesList}), 200
    
    else:
        print("Error while sending information:", response.status_code)
        return jsonify({'message':'Error while sending information'}), response.status_code

@server.route('/checkNeighbour', methods=['POST'])
def check_neighbour():

    url = serverURL + "/checkClientNeighbour"
    idResponse = request.get_json()
    id = idResponse.get("id")
    body = json.dumps({"id":id})
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url=url, data=body, headers=headers)
    
    # Verify the response
    if response.status_code == 200:
        responseBody = response.json()
        neighbourURL = responseBody['neighbourURL']
        return jsonify({'message':'Actual neighbour', "neighbourURL":neighbourURL}), 200
   
    else:
        print("Error while sending information:", response.status_code)
        return jsonify({'message':'Error while sending information'}), response.status_code

@server.route('/searchFileOwner', methods=['POST'])
def search_file_owner():

    url = serverURL + "/sendFileOwner"

    fileResponse = request.get_json()
    selectedFile = fileResponse.get("selectedFile")
    body = json.dumps({"selectedFile":selectedFile})
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url=url, data=body, headers=headers)
    
    # Verify the response
    if response.status_code == 200:
        responseBody = response.json()
        ownerURL = responseBody['ownerURL']
        return jsonify({'message':'Owner found', "ownerURL":ownerURL}), 200
    
    else:
        print("Error while sending information:", response.status_code)
        return jsonify({'message':'Error while sending information'}), response.status_code

@server.route('/saveFile', methods=['POST'])
def save_file():

    fileResponse = request.get_json()
    fileName = fileResponse.get("fileName")
        
    fileList.append(fileName)
    print(fileList)

    return jsonify({'message':'file saved correctly'}), 200

@server.route('/notifyLogout', methods=['POST'])
def notify_logout():

    url = serverURL + "/logout"
    bodyRequest = request.get_json()
    body = json.dumps({"id":bodyRequest.get("id")})
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url=url, data=body, headers=headers)

    # Verify the response
    if response.status_code == 200:
        responseBody = response.json()
        print(responseBody['message'])
        return jsonify({'message':responseBody['message']}), 200
    
    else:
        return jsonify({'message':"Error while sending information"}), response.status_code

@server.route('/download', methods=['POST'])
def download():

    fileResponse = request.get_json()
    fileName = fileResponse.get("selectedFile")
        
    print(fileList)

    if fileName in fileList:
        return jsonify({'message':fileName+' downloaded, Thanks'}), 200
    
    else:
        return jsonify({'message':fileName+' is not here, something is wrong'}), 404

@server.route('/fileToUpload', methods=['POST'])
def file_to_upload():

    fileResponse = request.get_json()
    idUploader = fileResponse.get("idUploader")
    fileName = fileResponse.get("fileName")
    
    url = serverURL + "/upload"
    body = json.dumps({"idUploader":idUploader,"fileName":fileName})
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url=url, data=body, headers=headers)
    responseBody = response.json()

    return jsonify({'message':responseBody["message"]}), response.status_code 

if __name__ == '__main__':

    serverIp = input("Central server IP: ")
    serverURL += serverIp + ":5000"

    server.run(debug=True, port=int(input("My Port:")))