# Configuración del NFS
## Servidor
Debemos crear nuesta máquina virtual, en este caso una EC2 t2.micro, Ubuntu 22.04. 

Una vez inicializada dicha máquina nos procedemos a actualizar los paquetes y a instalar el NFS para el servidor usando los siguientes comandos en consola:

```shell
sudo apt update
sudo apt install nfs-kernel-server -y
```

Creamos el directorio que vamos a compartir, en este caso:

```shell
sudo mkdir /var/nfs/toShare1 -p
```

Cambiamos el propietario y los permisos del directorio que vamos a compartir:

```shell
sudo chown nobody:nogroup /var/nfs/toShare1
sudo chmod 777 /var/nfs/toShare1
```

Luego ajustamos los archivos de configuración exports:

```shell
sudo nano /etc/exports
```

Allí agregamos la siguiente configuración (vale aclarar que debería ir en lugar del * la ip de la máquina que lo montaría posteriormente, sin embargo para evitar estar cambiando la configuración mientras tumbabamos máquinas y creabamos otras, decidimos dejarlo así para efectos del proyecto);

```nano
/var/nfs/toShare1 *(rw,sync,no_subtree_check)
```

Reiniciamos el servicio NFS y verificamos que esté activo

```shell
sudo systemctl restart nfs-kernel-server
sudo systemctl status nfs-kernel-server
```

Finalmente habilitamos el FireWall

```shell
sudo ufw enable
sudo ufw allow nfs
```

> Con esto ya debería ser suficiente para dejar expuesto el directorio /var/nfs/toShare1 para consumo de un cliente NFS

## Cliente 
Debemos crear nuesta máquina virtual, en este caso una EC2 t2.micro, Ubuntu 22.04. 

Una vez inicializada dicha máquina nos procedemos a actualizar los paquetes y a instalar el NFS para el cliente usando los siguientes comandos en consola:

```shell
sudo apt update
sudo apt install nfs-common -y
```

Creamos el directorio donde vamos a montar el directorio compartido, en este caso:

```shell
sudo mkdir /nfs/wordpress -p
```

Una vez se tenga esto, montamos el directorio compartido del servidor NFS con el siguiente comando, para este caso:

```shell
sudo mount [ip-privada-server]:/var/nfs/toShare1 /nfs/wordpress
```

>donde reemplazamos [ip-privada-server] por la ip privada de la máquina que hostea el NFS

posterior a esto podremos verificar que quedó montado nuestro directorio al usar el comando

```shell
df -h
```

>Si luego de todo esto no funciona el montaje del directorio, se recomienda revisar las reglas del grupo de seguridad. 

Y listo, una vez finalizado este proceso en ambas máquinas que correrán el wordpress ya se puede crear un wordpress que comparta el directorio /var/nfs/toShare1 del server NFS a través del directorio local /nfs/wordpress

# Referencias
- Boucheron, B. (2020, 11 junio). Cómo configurar NFS Mount en Ubuntu 20.04. DigitalOcean. https://www.digitalocean.com/community/tutorials/how-to-set-up-an-nfs-mount-on-ubuntu-20-04-es
- Akamai Developer. (2023, 15 marzo). How to Install and Configure an NFS Linux Server and Client [Vídeo]. YouTube. https://www.youtube.com/watch?v=zmDIfJtCKCk
