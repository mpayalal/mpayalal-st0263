# Configuración de la instancia wordpress
## Configuraciones generales 
Debemos crear 2 máquinas virtuales, en este caso una EC2 t2.micro, Ubuntu 22.04. 

Una vez inicializada cada máquina nos procedemos a actualizar los paquetes y a instalar docker y docker compose usando los siguientes comandos en consola:

```shell
sudo apt-get update
sudo apt install docker.io -y
sudo apt install docker-compose -y
```

Permitimos a la máquina el comenzar docker automaticamente y agregar el usuario ubuntu al grupo de docker con los siguientes comandos:

```shell
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -a -G docker ubuntu
```

Clonamos el repositorio donde están los archivos y nos ponemos en la carpeta donde están los archivos yml:

```shell
git clone https://github.com/st0263eafit/st0263-241.git
cd st0263-241/docker-nginx-wordpress-ssl-letsencrypt/
```

Copiamos el archivo que queremos construir con docker a la carpeta principal del usuario ubuntu:

```shell
sudo cp docker-compose-solo-wordpress.yml /home/ubuntu/wordpress
```

Debemos regresar a la carpeta principal del usuario ubuntu donde se encuentra wordpress. Si te encuentras en el paso aterior es escribir 'cd ../..'.
Luego debemos entrar a modificar el archivo wordpress (DB-HOST debe ser la ip privada de la base de datos, mientras que el NAME, USER y PASSWORD deben ser las mismas que lsa configuradas en la base de datos. Se deben borrar los volumes más externos y al interno se debe cambiar por nfs/wordpress:/var/www/html) y cambiarle el nombre a docker-compose.yml:

```shell
sudo nano wordpress
```

construimos el contenedor de docker usando el siguiente comando

```shell
sudo docker-compose up --build -d
```
# Referencias
- Linux post-installation steps for Docker Engine.
  https://docs.docker.com/engine/install/linux-postinstall/
- How To Use Systemctl to Manage Systemd Services and Units
  https://www.digitalocean.com/community/tutorials/how-to-use-systemctl-to-manage-systemd-services-and-units
- https://github.com/st0263eafit/st0263-241/tree/main
  
### ¡¡Listo, tienes tus instamcias de wordpress corriendo!!
