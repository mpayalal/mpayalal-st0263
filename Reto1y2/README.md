
# Reto 1 y 2

**Curso:** ST0263 - Tópicos Especiales en Telemática
<br>**Profesor:** Edwin Montoya - emontoya@eafit.edu.co
<br>**Estudiante:** Maria Paula Ayala - mpayalal@eafit.edu.co
<br>**Título:** P2P - Comunicación entre procesos mediante API REST, RPC y MOM
<br>**Objetivo:** Diseñar e implementar una red P2P para soportar un sistema distribuido de manejo de archivos.

## 1. Descripción de la actividad
#### 1.1. Aspectos cumplidos:
En este reto se cumplió con la arquitectura P2P no estructurada, la cual se detalla en el apartado [2](https://github.com/mpayalal/mpayalal-st0263/blob/main/Reto1y2/README.md#2-arquitectura-del-sistema), se logró la comunicación entre pServer, pClient y centralServer por medio de API REST. 

Además, el cliente puede conectarse y desconectarse a la red, y subir y descargar archivos, comunicandose siempre por medio de un peer vecino. 

#### 1.2. Aspectos no desarrollados:
No se realizó la comunicación por medio de gRPC y tampoco se guardan los datos de IP ni Puerto dinámicamente, cuando se inician el pServer y el pClient piden esta información por medio de la consola.

Hizo falta también el ping constante para verificar que los peers siguieran activos dentro de la red.

## 2. Arquitectura del sistema


## 3. Descripción del ambiente de desarrollo y técnco
#### 3.1. Desarrollo
Todo el proyecto fue desarrollado en el lenguaje Python. Este tiene una estructura como se puede observar a continuación:

```bash
  Reto1y2
  |
  |- CentralServer
  |  |
  |  |- app.py
  |
  |- Peer
  |  |
  |  |- pClientApp.py
  |  |- pServerApp.py
```
La primera carpeta, CentralServer, contiene solo un archivo, app.py, el cual fue realizado con el framework Flask y utiliza API REST para comunicarse con el pServer. Ahora, para entrar más a detalle, se explicará lo que hace cada ruta dentro de este archivo.

- /login [POST]: Este recibe los datos de IP y Puerto del pServer del cliente que se está conectando. Luego se revisa si ya hay más peers conectados a la red, de ser así, se escoge al último peer conectado como el vecino de este nuevo peer y se crea el objecto Peer con los datos ingresados; después, si había un peer pendiente por vecino se le asigna a este nuevo peer como su vecino. Si no existían peers antes se crea el objeto Peer y se añade a los peers pendientes por vecinos.

- /logout [POST]: Este método recibe el id del peer que se va a desconectar y lo primero que revisa es si este tenía archivos guardados, de ser así lo elimina de la "base de datos", que en este caso es un diccionario. Después revisa si tenía algún vecino asignado o si estaba como vecino de alguien más y los reasigna. Por último, se elimina su información de la "base de datos" de peers. 

- /uplaod [POST]: Recibe el id del peer que quiere subir un archivo y el nombre del archivo que quiere guardar. Luego, se escoge aleatoriamente un peer en el cual guardar este archivo, ignorando al peer que quiere subirlo. Después de escoger a qué peer va, el servidor se comunica con el pServer de ese peer y espera una respuesta de confirmación, si el pServer devuelve una respuesta afirmativa, se guarda el nombre del archivo en la "base de datos" con el id del peer en donde se guardó.

- /sendFiles [GET]: En este método solo se mandan los nombers de los archivos guardados en la "base de datos".

- /sendFileOwner [POST]: Se recibe el nombre del archivo que se quiere descargar, se busca cuál es el peer que tiene guardado este archivo y se envía la URL de este.

- /checkClientNeighbour [POST]: Este método recibe el id del peer que mandó la petición y revisa si este tiene ya asignado algún vecino, de ser así le devuelve la URL de este, si no, devuelve un None.

Ahora, dentro de la carpeta Peer encontramos dos archivos, el primero es pClientApp.py, el cual es con el que el usuario interactúa. Dentro de este encontramos los siguientes métodos:

- check_neighbour(): Llama a su servidor para actualizar, en caso de ser necesario, y guarda la información en la variable de vecino.

- upload(): Primero revisa que tenga un vecino asignado, de ser así, llama al servidor de este vecino y le manda el nombre del archivo que se quiere guardar. Si no tiene un vecino asignado no puede realizar esta operación y debe esperar a que otro peer se conecte.

- download(): Primero revisa que tenga un vecino asignado, si no lo tiene no puede realizar esta operación y debe esperar a que otro peer se conecte a la red. Si ya tiene un vecino asignado, le pide a este los archivos que se encuentran en la "base de datos" de la red y el usuario escoge cuál es el archivo que quiere descargar. Después, le pregunta al servidor del vecino por la URL de dónde se encuentra este archivo, este se lo devuelve y por último el cliente se conecta con el servidor que lo tiene y lo descarga.

- logout(): Se llama al propio servidor para que este realice la desconexión del servidor central y se apaga el cliente.

- display_menu(): Se muestra al usuario el menú de opciones que este puede y se llama al respectivo método según lo que escoja el usuario.

- main: Al momento de iniciar el programa se piden los datos de la IP del servidor central y la IP y el puerto del propio servidor. Después se envía esta información al servidor central para poder conectarse a la red. 

Por úlitmo, tenemos el archivo pServerApp.py, el cual fue realizado con el framework Flask y utiliza API REST para comunicarse con el servidor central. Este archivo actúa más como un intermediaro entre el cliente y el servidor central, por lo que se encuentran las siguientes rutas:

- /askForFiles [GET]: En este método se le solicitan los nombres de los archivos que se encuentren en la "base de datos" al servidor central y se le devuelve esta información al cliente.

- /checkNeighbour [POST]: Se comunica con el servidor central para encontrar la URL del peer vecino y se la envía al cliente.

- /searchFileOwner [POST]: Le soliciata al servidor central la URL del peer en donde se encuentra un archivo en específico y se la devuelve al cliente.

- /saveFile [POST]: El servidor central le envía la información de un archivo y este lo guarda en su "base de datos", que es un arreglo de nombres de archivos.

- /notifyLogout [POST]: Se comunica con el servidor central para avisarle que ese peer se va a desconectar de la red.

- /download [POST]: Revisa que en su "base de datos" esté el archivo que se quiere descargar, si es así, lo devuelve con éxito.

- /fileToUpload [POST]: Se comunica con el servidor central para guardar un nuevo archivo, en donde le envía el id del peer que lo está subiendo y el nombre del archivo.

#### 3.2. Ejecución local

## 4. Descripción del ambiente de ejecución



