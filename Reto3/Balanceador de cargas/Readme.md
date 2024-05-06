# Configuración del dominio y balanceador de cargas

## Instancia e IP elástica
1. Creamos nuesta máquina virtual, en este caso una EC2 t2.micro, Ubuntu 22.04.
2. Nos dirigimos a la sección de IP elásticas, creamos una y la asociamos con la instancia que acabamos de crear. 
3. Vamos al portal de nuestro proveedor del dominio y creamos un registro A para el subdominio reto3.nuestrodominio.com con la IP elástica que acabamos de asociar.
4. Esperamos un momento hasta que este registro esté funcionando correctamente, esto lo podemos verificar en la siguiente página https://toolbox.googleapps.com/apps/dig/#A/

## Certificado SSL

1. Actualizamos ubuntu y descargamos el certbot

```shell
sudo apt update
sudo add-apt-repository ppa:certbot/certbot
sudo apt install letsencrypt -y
sudo apt install nginx -y
```

2. Generamos el certificado

Acá debemos cambiar donde dice "nuestrodominio.com" por el dominio respectivo.

```shell
sudo mkdir -p /var/www/letsencrypt
sudo certbot --server https://acme-v02.api.letsencrypt.org/directory -d *.nuestrodominio.com --manual --preferred-challenges dns-01 certonly
```

3. Al mandar el comando anterior, saldrá un mensaje para crear un registro TXT, por lo que debemos dirigirnos al portal de nuestro proveedor DNS y añadir el registro con los datos proporcionados

4. Esperamos hasta que este funcione correctamente, podemo verificarlo en la misma página mencionada anteriormente https://toolbox.googleapps.com/apps/dig/#TXT/ 

5. Cuando esta funcione damos ENTER en la consola y debe salir un mensaje de éxito.

## Docker y Ngnix

1. Descargamos Docker

```shell
sudo apt update
sudo apt install docker.io -y
sudo apt install docker-compose -y
sudo apt install git -y
sudo systemctl enable docker
sudo systemctl start docker
```

2. Agregamos el usuario al grupo de Docker

Como lo estamos haciendo en máquinas Ubuntu en AWS, el usuario es ubuntu, en caso tal de que se esté haciendo en otro formato debe cambiar donde dice "ubuntu" por el respectivo nombre de usuario

```shell
sudo usermod -aG docker ubuntu
```

3. Cerramos la sesión y volvemos a abrir la terminal

4. Creamos los directorios para el docker compose

```shell
mkdir loadbalancer
mkdir loadbalancer/ssl
```

5. Copiamos el certificado creado anteriormente al directorio anterior

```shell
sudo su
cp /etc/letsencrypt/live/nuestrodominio.com/* /home/ubuntu/loadbalancer/ssl
```

6. Creamos el archivo de configuración de Ngnix

```shell
nano loadbalancer/nginx.conf
```

En este se copia el archivo [ngnix.conf](https://github.com/mpayalal/mpayalal-st0263/blob/main/Reto3/Balanceador%20de%20cargas/ngnix.conf) que se encuentra en este repositorio, cambiando donde dice <wordpress_ip1> y <wordpress_ip2> por las IPs privadas de cada instancia creada anteriormente.

7. Creamos el archivo de configuración SSL

```shell
nano loadbalancer/ssl.conf
```

En este se copia el archivo [ssl.conf](https://github.com/mpayalal/mpayalal-st0263/blob/main/Reto3/Balanceador%20de%20cargas/ssl.conf) que se encuentra en este repositorio, no se debe cambiar ninguna información de este.

8. Creamos el archivo docker compose

```shell
nano loadbalancer/docker-compose.yml
```

En este se copia el archivo [docker-compose.yml](https://github.com/mpayalal/mpayalal-st0263/blob/main/Reto3/Balanceador%20de%20cargas/docker-compose.yml) que se encuentra en este repositorio, no se debe cambiar ninguna información de este.

9. Detenemos los procesos de Ngnix

```shell
ps ax | grep nginx
netstat -an | grep 80

sudo systemctl disable nginx
sudo systemctl stop nginx
exit
```

10. Abrimos de nuevo la terminal y ejecutamos el docker compose

```shell
cd loadbalancer
docker-compose up -d
```

11. Nos dirigimos a internet, ingresamos nuestro dominio y debería estar funcionando correctamente.
