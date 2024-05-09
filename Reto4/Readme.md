# Reto 4

**Curso:** ST0263 - Tópicos Especiales en Telemática
<br>**Profesor:** Edwin Montoya - emontoya@eafit.edu.co
<br>**Estudiantes:**
- Maria Paula Ayala - mpayalal@eafit.edu.co
- Juan Felipe Pinzón - jfpinzont@eafit.edu.co
- Camilo Palacio Restrepo - cpalacior@efit.edu.co
  
<br>**Título:** Kubernetes
<br>**Objetivo:** Desplegar la misma aplicación del Reto 3 en un cluster de alta disponibilidad en Kubernetes.<br>**Sustentación:** https://www.youtube.com/watch?v=RNcaMWI4ixE


## 1. Descripción de la actividad
#### 1.1. Aspectos cumplidos:

- Wordpress desplegado en Kubernetes
- Crear nuestro propio dominio (reto4.miguapamundi.tech)
- Balanceador de cargas de Kubernetes
- Dos pods de Wordpress
- Una base de datos MySQL en GCP
- Un servidor NFS para los archivos

#### 1.2. Aspectos no desarrollados:

- Certificado SSL

## 2. Arquitectura del sistema

A continuación se observa el diagrama de la arquitectura usada para nuestro proyecto.

![ArqReto4Tele drawio](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/ff29a99e-f6f3-4a87-b8dc-5a5a58f5120e)


## 3. Descripción del ambiente de desarrollo y técnico

El reto se realizó en GCP y utilizamos el paso a paso que nos proporciona [Google cloud](https://cloud.google.com/kubernetes-engine/docs/tutorials/persistent-disk?hl=es-419), el cual explicaremos también a continuación:

### Preparación del espacio de trabajo

Lo primero que haremos es crear un proyecto en la consola de GCP, para nuestro caso se llama _Tele-Reto4-2_, activamos la Cloud Shell y dentro de esta habilitamos la API de administrador de GKE y Cloud SQL, lo cual se hace con el siguiente comando:

```bash
gcloud services enable container.googleapis.com sqladmin.googleapis.com
```

### Configuración del entorno de trabajo

En esta sección configuraremos unas variables que vamos a utilizar a través del tutorial y también vamos a clonar el repositorio que contiene los manifiestos que necesitamos.

1. Vamos a configurar la zona que queremos utilizar para Google Cloud CLI, en nuestro caso es _us-west1_, si desean usar una zona diferente se debe cambiar este valor

```bash
gcloud config set compute/region us-west1
```

2. Vamos a crear una variable de entorno para el id del proyecto de Google Cloud, este se encuentra en la información del proyecto, en nuestro caso es _tele-reto4-2_

```bash
export PROJECT_ID=tele-reto4-2
```

3. Clonamos el repositorio con los manifiestos

```bash
git clone https://github.com/GoogleCloudPlatform/kubernetes-engine-samples
```

4. Cambiamos al directorio que usaremos

```bash
cd kubernetes-engine-samples/quickstarts/wordpress-persistent-disks
```

5. Creamos una variable de entorno para el directorio de trabajo

```bash
WORKING_DIR=$(pwd)
```

### Creación del clúster de GKE

Vamos a crear un clúster de Google Kubernetes Engine en donde va a estar nuestra aplicación de Wordpress

1. Nos dirigimos a la sección de _Kubernetes Engine_, en esta debemos habilitarla y después vamos a la opción de crear un nuevo clúster estándar

2. Le ponemos un nombre, en nuestro caso _cluster-reto4-2_ y en la ubicación dejamos la opción "Zonal"

![image](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/30625715-f298-4298-ae16-127f6e1410cd)

3. Nos dirigimos a la sección "default pool" y luego a "Nodos", en esta ecogemos como tipo de imagen "Ubuntu con containerd" y el tipo de máquina E2-small

![image](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/a7fff9dc-da25-4d96-9835-90869e4362bc)
![image](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/e2b75d6c-f063-46c4-aa41-b47640be1e47)

4. Las demás especificaciones pueden quedar default y se crea el clúster. Esto puede tardar unos minutos, cuando veamos que el estado del clúster está con un visto bueno continuamos con el tutorial

![image](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/9d3f82cd-9b21-4f6e-86af-6952570b04b9)

5. Volvemos a la consola y nos vamos a conectar al clúster que acabamos de crear con el siguiente comando, recordar cambiar el nombre del cluster y la región en caso de ser necesario

```bash
gcloud container clusters get-credentials cluster-reto4-2 --region us-west1
```

### Creación del NFS y PV - PVC

Para este apartado nos basamos en el tutorial que provee [Google coud](https://cloud.google.com/filestore/docs/csi-driver?hl=es-419#deployment)

1. Antes de empezar debemos habilitar la API de Cloud Filestore y la API de Google Kubernetes Engine, para esto pueden entrar al siguiente enlace: [Habilita las API](https://console.cloud.google.com/flows/enableapi?apiid=container.googleapis.com%2Cfile.googleapis.com&hl=es-419&_ga=2.180154595.671953939.1715183695-1082497697.1714848645&_gac=1.118745723.1714961732.CjwKCAjw3NyxBhBmEiwAyofDYYHyvqIxZaEmvGafpJTSskf7rpX_rBdXg4XCTYYAMNdtWLzAnI6kYxoC1hgQAvD_BwE)

2. Habilitamos el controlador de CSI de Filestore en el clúster creado anteriormente

```bash
gcloud container clusters update $CLUSTER_NAME \
   --update-addons=GcpFilestoreCsiDriver=ENABLED
```

3. Creamos una instancia de Filestore en GCP, para esto buscamos la sección _Filestore_ y seleccionamos la opción de _Crear instancia_

4. Llenamos los siguientes datos:
    - Nombre de la instancia, en este caso va a ser _nfs-reto4_
    - Nivel del servicio, nosotros usaremos el básico por temas de costos
    - Tipo de almacenamiento es HDD
    - La región se debe escoger la misma con la que se viene trabajando
    - Se escoge la red VPC en la que nos encontremos, en nuestro caso es la default
    - Se asigna un nombre al archivo compartido, para nosotros es nfs_files

![image](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/018737bd-5e37-4d24-9f85-ffdb3ecb56b2)
![image](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/e5dd9378-f79a-41af-9b27-69fe6666d478)
![image](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/4cfcdea1-47b2-40c5-847a-bf29546588bf)

5. Creamos la instancia y esperamos a que esta se encuentre con el visto bueno

![image](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/a9bc5ac1-7a1b-49ba-be32-b7876700af2e)
![image](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/806a15cc-7073-4092-8387-253c3116aac8)

6. Creamos el archivo _nfs-pv-pvc.yaml_

```bash
sudo nano nfs-pv-pvc.yaml
```

Y en este se pondrá la siguiente información:

```bash
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs-pv
spec:
  storageClassName: ""
  capacity:
    storage: 1Ti
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  volumeMode: Filesystem
  csi:
    driver: filestore.csi.storage.gke.io
    volumeHandle: "modeInstance/us-central1-a  /nfs-reto4/nfs_files"
    volumeAttributes:
      ip: 10.56.30.210
      volume: nfs_files
---
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: podpvc
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: ""
  volumeName: nfs-pv
  resources:
    requests:
      storage: 1Ti
```

En las siguientes líneas se debe adaptar la información a los datos que hayas utilizado en el paso 4, vendría siendo

```bash
volumeHandle: "modeInstance/region_escogida  /nombre_instancia/nombre_archivo_compartido" 
volumeAttributes:
      ip: ip_instancia
      volume: nombre_archivo_compartido
```
La IP de la instancia se encuentra en la siguiente parte:

![image](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/d926235f-f973-42bc-8f73-deb21ee276f9)

7. Corremos el manifiesto que acabamos de crear

```bash
kubectl apply -f nfs-pv-pvc.yaml
```

8. Verificamos que se haya creado correctamente haciendo

```bash
kubectl get pvc
```

Al hacer este comando debe salir una pequeña tabla en donde el estado debe decir BOUND, si es así podemos continuar con los siguientes pasos

### Creación de la base de datos

Vamos a crear una instancia de MySQL en Cloud SQL, que es el servicio de base de datos que nos ofrece GCP

1. Creamos la instancia llamada mysql-wordpress-instance por medio de la consola

```bash
INSTANCE_NAME=mysql-wordpress-instance
gcloud sql instances create $INSTANCE_NAME
```

2. Creamos una variable de entorno para guardar el nombre de la conexión de la instancia que acabamos de crear

```bash
export INSTANCE_CONNECTION_NAME=$(gcloud sql instances describe $INSTANCE_NAME \
    --format='value(connectionName)')
```

3. Dentro de la instancia vamos a crear una base de datos para Wordpress

```bash
gcloud sql databases create wordpress --instance $INSTANCE_NAME
```

4. Vamos a crear los datos para poder entrar a la base de datos de wordpress, en este caso vamos a usar el usuario _wordpress_ y una contraseña aleatoria:

```bash
CLOUD_SQL_PASSWORD=$(openssl rand -base64 18)
gcloud sql users create wordpress --host=% --instance $INSTANCE_NAME \
    --password $CLOUD_SQL_PASSWORD
```

Para poder conocer la contraseña que se ha creado debemos hacer el siguiente comando

```bash
echo $CLOUD_SQL_PASSWORD
```

Y debemos guardar este dato en algún lugar seguro pues si cerramos la terminal se va a perder la contraseña

En este momento si nos dirigimos a la sección _SQL_ en la interfaz de GCP podremos ver la instancia _mysql-wordpress-instance_, y si entramos a esta y nos dirigimos al apartado _Cloud SQL Studio_ podemos entrar a la base de datos de wordpress con las credenciales que creamos en los pasos anteriores.

### Configuración para crear Wordpress

Ahora vamos a configurar una cuenta de servicio para que la aplicación de Wordpress que vamos a crear pueda acceder a la instancia de MySQL, esto lo lograremos a través de un proxy de Cloud SQL

1. Creamos una cuenta de servicio

```bash
SA_NAME=cloudsql-proxy
gcloud iam service-accounts create $SA_NAME --display-name $SA_NAME
```

2. Creamos una variable de entorno para guardar el correo de la cuenta de servicio

```bash
SA_EMAIL=$(gcloud iam service-accounts list \
    --filter=displayName:$SA_NAME \
    --format='value(email)')
```

3. Agregamos la función _cloudsql.client_ a la cuenta de servicio

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --role roles/cloudsql.client \
    --member serviceAccount:$SA_EMAIL
```

4. Creamos una clave para la cuenta de servicio

```bash
gcloud iam service-accounts keys create $WORKING_DIR/key.json \
    --iam-account $SA_EMAIL
```

Ahora vamos a crear 2 secretos de Kubernetes para las credenciales que necesitamos

5. Creamos un secreto para las credenciales de MySQL

```bash
kubectl create secret generic cloudsql-db-credentials \
    --from-literal username=wordpress \
    --from-literal password=$CLOUD_SQL_PASSWORD
```

6. Creamos un secreto para las credenciales de la cuenta de servicio

```bash
kubectl create secret generic cloudsql-instance-credentials \
    --from-file $WORKING_DIR/key.json
```

### Implementación de Wordpress

1. Reemplazamos la variable de entorno INSTANCE_CONNECTION_NAME en el archivo wordpress_cloudsql.yaml haciendo el siguiente comando

```bash
cat $WORKING_DIR/wordpress_cloudsql.yaml.template | envsubst > \
    $WORKING_DIR/wordpress_cloudsql.yaml
```

2. Este manifiesto cuenta con solo 1 replica para la aplicación, sin embargo, como nosotros queremos tener 2 replicas editamos el manifiesto

```bash
sudo nano wordpress_cloudsql.yaml
```

Y en el apartado de replicas cambiamos el 1 por 2

3. Implementamos el manifiesto

```bash
kubectl create -f $WORKING_DIR/wordpress_cloudsql.yaml
```

4. Revisamos que la implementación haya funcionado correctamente, debemos ver el cambio de estado a _Running_

```bash
kubectl get pod -l app=wordpress --watch
```

### Exponemos el servicio de Wordpress

1. Creamos el servicio de tipo LoadBalancer

```bash
kubectl create -f $WORKING_DIR/wordpress-service.yaml
```

2. La creación del servicio toma unos segundos, así que esperamos a que este tenga asignada una IP externa

```bash
kubectl get svc -l app=wordpress --watch
```

3. Copiamos la IP Externa que se le haya asignado al servicio e ingresamos a esta por medio de internet

```bash
http://ip-externa
```

### Configuración de Wordpress

Al entrar al link anterior se deben llenar unos campos para poder entrar a la páigna del administrador de wordpress, en los campos de usuario y contraseña poner los datos creados para la base de datos de wordpress y ya puedes crear tu página web.

### Configuración del dominio

Cuando ya tengas tu página web funcionando dirigete a tu servidor DNS y crea un registro A con el nombre del subdominio que deseas, en nuestro caso es reto4, y lo vinculas a la IP Externa del servicio de wordpress. 

Espera unos segundos y ya podrás acceder a tu página web por medio de tu dominio.

### Evidencia

A continuación de muestra una captura de pantalla de nuestra página funcionando

![image](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/b3779b96-6b9c-4499-a466-8831025e5690)


## 4. Referencias

- https://cloud.google.com/kubernetes-engine/docs/tutorials/persistent-disk?hl=es-419
- https://cloud.google.com/filestore/docs/csi-driver?hl=es-419#deployment
- https://github.com/GoogleCloudPlatform/kubernetes-engine-samples/tree/main/quickstarts/wordpress-persistent-disks
