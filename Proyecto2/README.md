# Proyecto 2

**Curso:** ST0263 - Tópicos Especiales en Telemática
<br>**Profesor:** Edwin Montoya - emontoya@eafit.edu.co
<br>**Estudiantes:**
- Maria Paula Ayala - mpayalal@eafit.edu.co
- Juan Felipe Pinzón - jfpinzont@eafit.edu.co
- Camilo Palacio Restrepo - cpalacior@efit.edu.co
  
<br>**Título:** Cluster Kubernetes
<br>**Objetivo:** Implementar un CMS empleando la tecnología de kubernetes, crando un cluster con mínimo 3 máquinas viruales (master y workers) usando microk8s, con su propio dominio y certificado SSL. <br>**Sustentación:** https://www.youtube.com/watch?v=zdYERn8ba7U

## 1. Descripción de la actividad
#### 1.1. Aspectos cumplidos:

- Cluster de kubernetes crado con microk8s 
  - Una instancia Master
  - Dos instancias Worker
- Crear nuestro propio dominio (proyecto2.miguapamundi.tech)
- Certificado SSL
- Capa de acceso con microk8s Ingress
- Instancias de Wordpress con sus deployment, service, pv y pvc
- Base de datos MySQL con su deployment, service, pv y pvc
- Un servidor NFS para los archivos en una instancia de externa al cluster

#### 1.2. Aspectos no desarrollados:

Se cumplió con todo lo especificado para este proyecto.

## 2. Arquitectura del sistema

A continuación se observa el diagrama de la arquitectura usada para nuestro proyecto.

![ArqProy2Tele](https://github.com/mpayalal/mpayalal-st0263/assets/85038450/6eb68244-332e-4222-b2d0-cada9021a3ed)

Además encontramos el siguiente link para acceder a una mejor visualización:
[Enlace Arquitectura](https://drive.google.com/file/d/1yIdAA2IHkWAKPc8P4sF3KsXP04a8TMH-/view?usp=sharing)

## 3. Descripción del ambiente de desarrollo y técnico

Para este proyecto, como se ha mencionado anteriormente, se realizaron diferentes servicios e instancias, cada uno de estos fue hecho en una instancia E2 en Google Cloud Service, con una imagen de Ubuntu 22.04 LTS y el tipo de instancia es e2.medium. A continuación se detallan los pasos de cada uno de los servicios.

### 1. Creación de las instancias 
Se modifica el disco de arranque de las máquinas virtuales y configuro el firewall

![image-3](https://github.com/mpayalal/mpayalal-st0263/assets/85038450/3bbe40cf-1c85-43fc-8ea0-58d81cb83e34)

![image-4](https://github.com/mpayalal/mpayalal-st0263/assets/85038450/20bdf759-d73a-40c6-9e89-717cf84421ad)

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

![image-5](https://github.com/mpayalal/mpayalal-st0263/assets/85038450/7599c5aa-8bd5-40bc-919e-9d7a5bf7c111)

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

![image-6](https://github.com/mpayalal/mpayalal-st0263/assets/85038450/d65ff6f2-8c4d-4f95-a8e9-21913b8000f7)

en las intancias worker se debe pegar el comando de join que apareció en el maestro

![image-7](https://github.com/mpayalal/mpayalal-st0263/assets/85038450/22197fd4-4e8f-458e-924e-3fba0a650f71)

observamos que en el maestro se puedan ver todos los nodos 
```shell
microk8s kubectl get nodes
```
Debería aparecer algo así

![image-8](https://github.com/mpayalal/mpayalal-st0263/assets/85038450/de75cb1b-be9b-4658-a393-727bc7da7f6c)

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

![pvc_nfs](https://github.com/mpayalal/mpayalal-st0263/assets/85038450/a0f51d1f-1eab-4f02-9750-ada0f2dade94)

### 5. Configuración de manifiestos MySQL, Wordpress e Ingress

En esta sección vamos a crear los manifiestos para los diferentes servicios que se utilizaran en el proyecto, todos los que vamos a mostrar a continuación se encuentran en la carpeta Scripts con los datos que utilizamos puntualmente para este proyecto.

Primero vamos a crear el servicio de MySQL, para esto creamos el archivo `mysql-pv-pvc.yaml`

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mysql-pv
spec:
  storageClassName: nfs-csi
  capacity:
    storage: 5Gi
  volumeMode: Filesystem
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  nfs:
    server: 0.0.0.0 #ip del nfs-server
    path: /srv/nfs #cambiar por la ruta escogida
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
  labels:
    app: mysql
spec:
  storageClassName: nfs-csi
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 5Gi
```
> En este archivo se debe poner la IP privada del servidor NFS que creamos en el paso 3 y también la ruta creada para los archivos compartidos.

Ahora aplicamos este manifiesto para comprobar que funcione correctamente

```shell
microk8s kubectl apply -f mysql-pv-pvc.yaml
```

Para verificar hacemos

```shell
microk8s kubectl get pvc
```

Y debe salir con el estado BOUND, como se ve a continuación

![image](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/e49a2f4b-3bdf-4cbf-9dea-7521654e7681)


Continuamos ahora creando el manifiesto del servicio y deployment de MySQL, `mysql-deployment.yaml`, para esto utilizamos la imagen de [bitnami/mysql](https://hub.docker.com/r/bitnami/mysql)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql
  labels:
    app: wordpress
spec:
  ports:
    - port: 3306
  selector:
    app: wordpress
    tier: mysql
  clusterIP: None
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wordpress-mysql
  labels:
    app: wordpress
spec:
  selector:
    matchLabels:
      app: wordpress
      tier: mysql
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: wordpress
        tier: mysql
    spec:
      containers:
      - image: docker.io/bitnami/mysql:8.0
        name: mysql
        env:
        - name: MYSQL_ROOT_PASSWORD
          value: <contraseña>
        - name: MYSQL_DATABASE
          value: <base_de_datos>
        - name: MYSQL_USER
          value: <usuario>
        - name: MYSQL_PASSWORD
          value: <contraseña>
        ports:
        - containerPort: 3306
          name: mysql
        volumeMounts:
        - name: mysql-persistent-storage
          mountPath: /var/lib/mysql
      volumes:
      - name: mysql-persistent-storage
        persistentVolumeClaim:
          claimName: mysql-pvc
```
> Se deben llenar los datos de usuario, contraseña y nombre de base de datos

Aplicamos el manifiesto y confirmamos que se haya creado correctamente revisando el estado del pod, el cual debe salir RUNNING

```shell
microk8s kubectl apply -f mysql-deployment.yaml

microk8s kubectl get pods
```

Si se quiere revisar a fondo que la base de datos se haya creado correctamente podemos correr el siguiente comando, cambiando los datos que están en <> por los de tu proyecto

```shell
microk8s kubectl exec -it <nombre_del_pod> -- mysql -u<usuario> -p<contraseña>
```

Acá ya estaremos dentro de la terminal de mysql, ahora entonces corremos

```shell
SHOW DATABASES;
```

Nos debe salir entre las opciones la base de datos que creamos en el manifiesto, en nuestro caso se llama wordpress, acá la podemos observar:

![image](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/816ffafd-b68a-4562-b9bb-63b0ceb523e6)

Ya viendo esto podemos estar seguros de su creación, nos salimos de esta terminal haciendo un `exit` y continuamos ahora creando los manifiestos de wordpress.

Crearemos también un manifiesto para el pv-pvc y un para el servicio-deployment, los archivos se ven a continuación:

`wordpress-pv-pvc.yaml`
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: wordpress-pv
spec:
  capacity:
    storage: 5Gi
  volumeMode: Filesystem
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: nfs-csi
  nfs:
    server: 0.0.0.0 #ip del nfs-server
    path: /srv/nfs #cambiar por la ruta escogida
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: wordpress-pvc
  labels:
    app: wordpress
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: nfs-csi
  resources:
    requests:
      storage: 5Gi
```
> En este archivo se debe poner la IP privada del servidor NFS que creamos en el paso 3 y también la ruta creada para los archivos compartidos.

`wordpress-deployment.yaml`, para esto utilizamos la imagen de [wordpress](https://hub.docker.com/_/wordpress)
```shell
apiVersion: v1
kind: Service
metadata:
  name: wordpress
  labels:
    app: wordpress
spec:
  ports:
  - port: 80
  selector:
    app: wordpress
    tier: frontend
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wordpress
  labels:
    app: wordpress
spec:
  replicas: 2
  selector:
    matchLabels:
      app: wordpress
      tier: frontend
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: wordpress
        tier: frontend
    spec:
      containers:
      - image: wordpress
        name: wordpress
        env:
        - name: WORDPRESS_DATABASE_HOST
          value: <host_base_de_datos>
        - name: WORDPRESS_DATABASE_PASSWORD
          value: <contraseña>
        - name: WORDPRESS_DATABASE_USER
          value: <usuario>
        - name: WORDPRESS_DATABASE_NAME
          value: <base_de_datos>
        - name: WORDPRESS_DEBUG
          value: "1"
        ports:
        - containerPort: 80
          name: wordpress
        volumeMounts:
        - name: wordpress-persistent-storage
          mountPath: /var/www/html
      volumes:
      - name: wordpress-persistent-storage
        persistentVolumeClaim:
          claimName: wordpress-pvc
```
> Se deben llenar los datos de usuario, contraseña, nombre de base de datos y host de base de datos, este último es el nombre del servicio que creamos para mysql, y los otros son los mismos que se escribieron en el manifiesto de deployment para mysql.

Ahora aplicamos estos manifiestos y revisamos que tanto el pvc y los pods se hayan creado correctamente

```shell
microk8s kubectl apply -f wordpress-pv-pvc.yaml

microk8s kubectl get pvc
```

```shell
microk8s kubectl apply -f wordpress-deployment.yaml

microk8s kubectl get pods
```

Después de que todo lo anterior esté funcionando correctamente, creamos el manifiesto del ingress para poder acceder a nuestro proyecto, `ing-wordpress.yaml`

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: http-ingress
  labels:
    app: wordpress
spec:
  rules:
  - http:
      paths:
      - pathType: Prefix
        path: "/"
        backend:
          service:
            name: wordpress
            port:
              number: 80
```
Aplicamos este manifiesto

```shell
microk8s kubectl apply -f ing-wordpress.yaml
```

Ahora si ingresamos a la **IP pública** de la máquina **MASTER** nos encontraremos con la página de configuración de Wordpress, llenamos los datos y ya tenemos nuestra página funcionando.

![image](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/9d441db1-2522-4ae6-9d9b-30456e09e6dd)
![image](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/cbc729ee-e476-4044-b9c9-836a8d6823d8)

### 6. Certificación SSL

*Antes de comenzar con este paso en tu servidor DNS debes agregar el registro para la IP pública de la máquina MASTER*

Primero vamos a instalar el cert-manager

```shell
microk8s kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.3.1/cert-manager.yaml
```

Para revisar que se instaló correctamente debemos ver 3 pods corriendo al hacer el siguiente comando

```shell
microk8s kubectl get pods -n=cert-manager
```

![image](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/e07ccbf5-b0bb-4666-ac81-3a612c4ffc12)

Ahora vamos a crear 2 claves .pem para los archivos `cluster-issuer-staging.yaml` y `cluster-issuer.yaml`, esto lo hacemos de la siguiente manera:

```shell
openssl genrsa -out letsencrypt-staging.pem 2048

openssl genrsa -out letsencrypt-private-key.pem 2048
```

Luego creamos un secreto en Kubernetes con estas claves

```shell
sudo microk8s kubectl create secret generic letsencrypt-staging --from-file=letsencrypt-staging.pem

microk8s kubectl create secret generic letsencrypt-private-key --from-file=letsencrypt-private-key.pem
```

Después creamos los manifiestos mencionados anteriormente

`cluster-issuer-staging.yaml`

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
#change to your email
    email: tucorreo@gmail.com
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    privateKeySecretRef:
      name: letsencrypt-staging
    solvers:
    - http01:
        ingress:
          class: public
```

`cluster-issuer.yaml`

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    # The ACME server URL
    server: https://acme-v02.api.letsencrypt.org/directory
    # Email address used for ACME registration
    email: tucorreo@gmail.com
    # Name of a secret used to store the ACME account private key
    privateKeySecretRef:
      name: letsencrypt-private-key
    # Enable the HTTP-01 challenge provider
    solvers:
      - http01:
          ingress:
            class: public
```

Aplicamos ambos manifiestos

```shell
microk8s kubectl apply -f cluster-issuer-staging.yaml

microk8s kubectl apply -f cluster-issuer.yaml
```

Seguimos ahora con la creación del manifiesto del nuevo ingress el cual hará la petición del certificado para nuestro dominio

`ingress-routes.yaml`

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-routes
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-staging"
spec:
  tls:
  - hosts:
#change to your domain
    - tudominio.com
    secretName: tls-secret
  rules:
#change to your domain
  - host: tudominio.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: wordpress
            port:
              number: 80
```

Aplica el manifiesto y verificamos que el certificado haya sido creado exitosamente

```shell
microk8s kubectl apply -f ingress-routes.yaml

microk8s kubectl get certificate
```
> Al hacer el segundo comando, el estado debe pasar de falso a verdadero, esto toma entre 1 a 2 minutos, si pasado este tiempo no pasa a veradero revisa las configuraciones y vuelve a intentarlo

![image](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/0ddba1fe-1460-46dc-b1af-914edd403a47)

Si ya salió verdadero cambiamos en el archivo `ingress-routes.yaml` el cluster-issuer de staging a prod, debe quedar así:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-routes
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
#change to your domain
    - tudominio.com
    secretName: tls-secret
  rules:
#change to your domain
  - host: tudominio.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: wordpress
            port:
              number: 80
```

Volvemos a aplicarlo y revisar que pase a Verdadero

```shell
microk8s kubectl apply -f ingress-routes.yaml

microk8s kubectl get certificate
```

Ya podrás entrar a tu página por medio de https.

![image](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/3add5e90-9565-47c8-a7f1-ac3e7723724e)
![image](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/619a59d4-3ea1-46a1-b4b6-5bf832a5a7e3)

# Referencias

- [Install MicroK8s](https://microk8s.io/#install-microk8s)
- [Create a MicroK8s cluster](https://microk8s.io/docs/clustering)
- [Use NFS for Persistent Volumes on MicroK8s](https://microk8s.io/docs/how-to-nfs)
- [Kubernetes Tutorial for BEGINNERS | Pods Deployments Services Ingress Explained | MicroK8s Install](https://youtu.be/3T6skoL3RTA?si=x-UUe6LjNKz6C4MR)
- [Bitnami package for MySQL](https://hub.docker.com/r/bitnami/mysql)
- [Package for WordPress](https://hub.docker.com/_/wordpress)
- [Example: Deploying WordPress and MySQL with Persistent Volumes](https://kubernetes.io/docs/tutorials/stateful-application/mysql-wordpress-persistent-volume/)
- [Letsencrypt for microk8s](https://stackoverflow.com/questions/67430592/how-to-setup-letsencrypt-with-kubernetes-microk8s-using-default-ingress)
- [Gemini AI](https://g.co/gemini/share/1f1cfb7d6152)
