# Proyecto 2

**Curso:** ST0263 - Tópicos Especiales en Telemática
<br>**Profesor:** Edwin Montoya - emontoya@eafit.edu.co
<br>**Estudiantes:**
- Maria Paula Ayala - mpayalal@eafit.edu.co
- Juan Felipe Pinzón - jfpinzont@eafit.edu.co
- Camilo Palacio Restrepo - cpalacior@efit.edu.co
  
<br>**Título:** Cluster Kubernetes
<br>**Objetivo:** Implementar un CMS empleando la tecnología de kubernetes, crando un cluster con mínimo 3 máquinas viruales (master y workers) usando microk8s, con su propio dominio y certificado SSL. <br>**Sustentación:** 

## 1. Descripción de la actividad
#### 1.1. Aspectos cumplidos:

- Cluster de kubernetes crado con microk8s 
  - Una instancia Master
  - Dos o más instancias Worker
- Crear nuestro propio dominio (miguapamundi.tech)
- Certificado SSL
- Capa de acceso con microk8s Ingress
- Instancias de Wordpress con sus deployment, service, pv y pvc
- Base de datos MySQL con su deployment, service, pv y pvc
- Un servidor NFS para los archivos en una instancia de externa al cluster

#### 1.2. Aspectos no desarrollados:

Se cumplió con todo lo especificado para este reto.

## 2. Arquitectura del sistema

A continuación se observa el diagrama de la arquitectura usada para nuestro proyecto.

![ArqProy2Tele](ArqProy2Tele.png)

Además que encontramos el siguiente link para acceder a una mejor visualización:
[Enlace Arquitectura](https://drive.google.com/file/d/1yIdAA2IHkWAKPc8P4sF3KsXP04a8TMH-/view?usp=sharing)

## 3. Descripción del ambiente de desarrollo y técnico

Para este proyecto, como se ha mencionado anteriormente, se realizaron diferentes servicios e instancias, cada uno de estos fue hecho en una instancia E2 en Google Cloud Service, con una imagen de Ubuntu 22.04 LTS y el tipo de instancia es e2.medium. A continuación se detallan los pasos de cada uno de los servicios.

### 1. Creacion de las instancias 
Se modifica el disco de arranque de las máquinas virtuales y configuro el firewall

![disco-arr](image-3.png)

![firewall](image-4.png)

Se actualiza la máquina virtual 

```shell
sudo apt-get update
```

Se instala Microk8s en ubuntu 

```shell
sudo snap install microk8s --classic
```
Miramos el estado de kubernetes
```shell
microk8s status --wait-ready
```
Nos va a aparecer que no tenemos los permisos, entonces nos procedemos a crear el directorio `./kube` y copiamos los comandos que nos aparecen; luego reiniciamos la máquina para que se tomen los permisos necesarios

![status](image-5.png)

encendemos los servicios necesarios
```shell
microk8s enable dashboard dns registry istio ingress
```
### 2. Creación del cluster
En la instancia maestro se crea el comando para unirse al cluster
```shell
microk8s add-node
```
debe aparecer un mensaje así
![add-node](image-6.png)

en las intancias worker se debe pegar el comando de join que apareció en el maestro
![join cluster](image-7.png)

observamos que en el maestro se puedan ver todos los nodos 
```shell
microk8s kubectl get nodes
```
Debería aparecer algo así

![cluster](image-8.png)

### 3. Configuración del NFS-Server

Creamos una máquina Ubuntu 22.04 con un disco de arranque de 20Gi y habilitamos el tréfico http, https y las verificaciones de balanceador de cargas

Una vez creada, la actualizamos e instalamos el servidor de NFS

```shell
sudo apt-get update
sudo apt-get install nfs-kernel-server
```

Posterior a esto, procedemos a crear el directorio que compartiremos a los clientes NFS y le otorgaremos los permisos necesarios

```shell
sudo mkdir -p /srv/nfs
sudo chown nobody:nogroup /srv/nfs
sudo chmod 0777 /srv/nfs
```

Luego editamos el archivo exports para permitir el vínculo de este directorio

```shell
sudo mv /etc/exports /etc/exports.bak
echo '/srv/nfs *(rw,sync,no_subtree_check)' | sudo tee /etc/exports
```

Finalmente reiniciamos el servicio y verificamos que esté funcionando correctamente

```shell
sudo systemctl restart nfs-kernel-server
sudo systemctl status nfs-kernel-server
```

### 4. Instalación de los drivers CSI para NFS

Desde nuestra máquina **MASTER** habilitamos el paquete de helm3 y desde este tomamos los drivers

```shell
microk8s enable helm3
microk8s helm3 repo add csi-driver-nfs https://raw.githubusercontent.com/kubernetes-csi/csi-driver-nfs/master/charts
microk8s helm3 repo update
```

Descargamos el helm chart del namespace de kube-system

```shell
microk8s helm3 install csi-driver-nfs csi-driver-nfs/csi-driver-nfs \
    --namespace kube-system \
    --set kubeletDir=/var/snap/microk8s/common/var/lib/kubelet
```

Luego esperamos hasta que estén los pods, lo cual verificaremos con el comando

```shell
microk8s kubectl wait pod --selector app.kubernetes.io/name=csi-driver-nfs --for condition=ready --namespace kube-system
```

Hasta que salga un output similar al siguiente:
```shell
pod/csi-nfs-controller-67bd588cc6-7vvn7 condition met
pod/csi-nfs-node-qw8rg condition met
pod/csi-nfs-node-a9d8w condition met
pod/csi-nfs-node-ñ2ie2 condition met
```

En este punto deberán estar disponibles los drivers CSI

```shell
microk8s kubectl get csidrivers
```

Y debe verse un output similar al siguiente:
```shell
NAME             ATTACHREQUIRED   PODINFOONMOUNT   STORAGECAPACITY   TOKENREQUESTS   REQUIRESREPUBLISH   MODES        AGE
nfs.csi.k8s.io   false            false            false             <unset>         false               Persistent   39m
```

posteriormente creamos los archivos `sc-nfs.yaml` y `pvc-nfs.yaml`:

```yaml
# sc-nfs.yaml
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-csi
provisioner: nfs.csi.k8s.io
parameters:
  server: 0.0.0.0 #ip del nfs-server
  share: /srv/nfs
reclaimPolicy: Delete
volumeBindingMode: Immediate
mountOptions:
  - hard
  - nfsvers=4.1
```
```yaml
# pvc-nfs.yaml
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  storageClassName: nfs-csi
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 5Gi
```

y los aplicamos 

```shell
microk8s kubectl apply -f - < sc-nfs.yaml
microk8s kubectl apply -f - < pvc-nfs.yaml
```

y una vez se corran dichos comandos deberá haberse vinculado(bound) nuestro pvc. Además podremos ver en el servidor NFS el pvc en nuestro directorio compartido:

![pvc en nfs](pvc_nfs.png)

## 4. Descripción del ambiente de EJECUCIÓN

# Referencias

- [Install MicroK8s](https://microk8s.io/#install-microk8s)
- [Create a MicroK8s cluster](https://microk8s.io/docs/clustering)
- [Use NFS for Persistent Volumes on MicroK8s](https://microk8s.io/docs/how-to-nfs)
- [Kubernetes Tutorial for BEGINNERS | Pods Deployments Services Ingress Explained | MicroK8s Install](https://youtu.be/3T6skoL3RTA?si=x-UUe6LjNKz6C4MR)
- [Bitnami package for MySQL](https://hub.docker.com/r/bitnami/mysql)
- [Bitnami package for WordPress](https://hub.docker.com/r/bitnami/wordpress)
- [Example: Deploying WordPress and MySQL with Persistent Volumes](https://kubernetes.io/docs/tutorials/stateful-application/mysql-wordpress-persistent-volume/)
- [Gemini AI](https://g.co/gemini/share/1f1cfb7d6152)