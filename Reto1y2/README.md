
# Reto 1 y 2

**Curso:** ST0263 - Tópicos Especiales en Telemática
<br>**Profesor:** Edwin Montoya - emontoya@eafit.edu.co
<br>**Estudiantes:**
- **Autora:** Maria Paula Ayala - mpayalal@eafit.edu.co
- **Coautor:** Juan Felipe Pinzón - jfpinzont@eafit.edu.co
  
<br>**Título:** P2P - Comunicación entre procesos mediante API REST, RPC y MOM
<br>**Objetivo:** Diseñar e implementar una red P2P para soportar un sistema distribuido de manejo de archivos.
<br>**Sustentación:** https://www.youtube.com/watch?v=rR_rQgQtQvM

## 1. Descripción de la actividad
#### 1.1. Aspectos cumplidos:
En este reto se cumplió con la arquitectura P2P no estructurada basada en servidor de directorio y localización, la cual se detalla en el [apartado 2](https://github.com/mpayalal/mpayalal-st0263/blob/main/Reto1y2/README.md#2-arquitectura-del-sistema). En este se logró la comunicación entre las entidades del peer (pServer y pClient) y el servidor central por medio del middleware API REST. 
 
Además, el cliente puede conectarse y desconectarse a la red, y subir y descargar archivos, comunicandose siempre por medio de un peer vecino que funciona como intermediario. 

#### 1.2. Aspectos no desarrollados:
Según lo solicitado para este reto, faltó implementar los siguientes aspectos:
- La comunicación por medio del middleware gRPC.
- Los datos de IP y Puerto de los peers no se guardan ni leen dinámicamente, esta información se pide por medio de la consola cuando se inicializan.
- No se verifica que los peers sigan activos dentro de la red, se asume que siguen conectados a menos de que hagan logout.
- Si un peer se sale de la red, se borran sus archivos para siempre. Si se vuelve a conectar tendría que volver a subir sus archivos otra vez.

## 2. Arquitectura del sistema

Como se mencionó anteriormente, la arquitectura es P2P no estructurada, en donde se encuentra un servidor central, que es el encargado de recibir las peticiones y devolver la infromación necesaria, y cada peer cuenta con su propio cliente y servidor. A continuación se ve un diagrama en donde se ven los tipos de consulta que realiza cada elemento dentro de la red.

![WhatsApp Image 2024-03-03 at 19 52 30](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/c028ad17-0720-475f-8a03-9108a61554f7)

Es importante aclarar que cada comunicación manda su respectiva respuesta al elemento que realizó la consulta.

## 3. Descripción del ambiente de desarrollo y técnico
#### 3.1. Desarrollo
Todo el proyecto fue desarrollado en el lenguaje Python. Este tiene una estructura como se puede observar a continuación:

```bash
  Reto1y2/
  |
  |- CentralServer/
  |  |
  |  |- app.py
  |
  |- Peer/
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
Antes de empezar a correr el programa, debes verificar que cuentes con una versión 3.x de Python, si no lo tienes debes instalarlo.

Cuando ya tengas instalado python debes instalar Flask y requests, esto se hace de la siguiente manera:

```bash
  pip install Flask

  pip install requests
```

Cuando ya se tengan estas librerias descargadas ya podemos correr el proyecto. Lo primero que vamos a hacer es abrir 1 terminal en donde correremos el servidor central, y vamos a abrir otras terminales para que cada una sea un peer, estas las dividimos en 2 para tener cliente y servidor juntos. 

![image](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/3286c303-8560-4a6f-a88b-29237f48e9fd)
![image](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/377bfc9e-eabe-4a38-8c70-0f161050a167)

Cuando ya tenemos todo dividido, en la terminal del servidor central lo inciamos así:

```bash
  py app.py
```
Y va a salir un mensaje avisando en qué dirección está corriendo, como es local, siempre va a ser http://127.0.0.1:5000. 

Luego nos dirigimos a la terminal del Peer 0 y vamos a ejecutar primero el pServer, este nos va a pedir los datos de la IP del servidor central, que es 127.0.0.1, y el puerto para el pServer, para el ejemplo vamos a utilizar el *5001*, por lo que la ejecución en la consola se vería así:

```bash
  py pServerApp.py

  Central server IP: 127.0.0.1
  My Port:5001
    * Serving Flask app 'pServerApp'
    * Debug mode: on
  WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
    * Running on http://127.0.0.1:5001
  Press CTRL+C to quit   
    * Restarting with stat
```
Ahí mismo salga este mensaje va a volver a pedir los mismos datos, así que volvemos a ingresar la misma información y ya está corriendo el pServer del peer 0 en la dirección http://127.0.0.1:5001.

``` bash
  Central server IP: 127.0.0.1
  My Port:5001
    * Debugger is active!
    * Debugger PIN: 118-598-234
```

Ahora vamos a prender el cliente, en este también nos van a pedir la información del servidor central y del servidor. Entonces quedaría así:

``` bash
  py pClientApp.py

  Central server IP: 127.0.0.1
  My server IP: 127.0.0.1
  My server Port:5001

```
Cuando se haga esto ya saldrá el menú de actividades de lo que se puede hacer. En este caso, como es el único peer en la red solo podrá hacer logout, igualmente, si el usuario escoge la opción 1 o 2, que son upload y download respectivamente, le saldrá un mensaje avisando que no tiene peers todavía, como se puede ver a continuación.

![image](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/99973835-4054-48f5-abcd-bff397c846b1)

El siguiente paso sería entonces crear otro peer de la misma manera, cambiando solo el valor del puerto del pServer, este podría ser *5002*, y ya si se podría cargar y descargar archivos. Para esto solo se debe escoger la opción del menú y dependiendo de la acción escogida, el mismo sistema va pidiendo los datos necesarios. Para ver un ejemplo más detallado diriganse al siguiente video: https://www.youtube.com/watch?v=UlKCfl2k3os

