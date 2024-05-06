# Reto 3

**Curso:** ST0263 - Tópicos Especiales en Telemática
<br>**Profesor:** Edwin Montoya - emontoya@eafit.edu.co
<br>**Estudiantes:**
- Maria Paula Ayala - mpayalal@eafit.edu.co
- Juan Felipe Pinzón - jfpinzont@eafit.edu.co
- Camilo Palacio Restrepo - cpalacior@efit.edu.co
  
<br>**Título:** Aplicación Monolítica con Balanceo y Datos Distribuidos (BD y archivos)
<br>**Objetivo:** Implementar un CMS empleando la tecnología de contenedores, con su propio dominio y certificado SSL. <br>**Sustentación:** https://www.youtube.com/watch?v=UZ7cgyIR71Q

## 1. Descripción de la actividad
#### 1.1. Aspectos cumplidos:

- Wordpress desplegado con Docker
- Crear nuestro propio dominio (miguapamundi.tech)
- Certificado SSL
- Balanceador de cargas con Ngnix y Docker
- Dos instancias de Wordpress
- Una base de datos MySQL
- Un servidor NFS para los archivos

#### 1.2. Aspectos no desarrollados:

Se cumplió con todo lo especificado para este reto.

## 2. Arquitectura del sistema

A continuación se observa el diagrama de la arquitectura usada para nuestro proyecto.

![tele - Frame 1](https://github.com/mpayalal/mpayalal-st0263/assets/85038378/1826086f-20be-4a66-a1e2-d0180e522d1a)


## 3. Descripción del ambiente de desarrollo y técnico

Para este proyecto, como se ha mencionado anteriormente, se realizaron diferentes servicios, cada uno de estos fue hecho en una instancia EC2 en Amazon Web Services, con ina imágen de Ubuntu 22.04 LTS y el tipo de instancia es t2.micro. A continuación se detallan los pasos de cada uno de los servicios.

1. [NFS](https://github.com/mpayalal/mpayalal-st0263/tree/main/Reto3/NFS)

2. [Base de datos](https://github.com/mpayalal/mpayalal-st0263/tree/main/Reto3/Base%20de%20datos)

3. [Wordpress](https://github.com/mpayalal/mpayalal-st0263/tree/main/Reto3/WordPress)

4. [Balanceador de cargas](https://github.com/mpayalal/mpayalal-st0263/tree/main/Reto3/Balanceador%20de%20cargas)

## 4. Referencias

- [Repositorio de clase](https://github.com/st0263eafit/st0263-241/tree/main/docker-nginx-wordpress-ssl-letsencrypt)
- Boucheron, B. (2020, 11 junio). Cómo configurar NFS Mount en Ubuntu 20.04. DigitalOcean. https://www.digitalocean.com/community/tutorials/how-to-set-up-an-nfs-mount-on-ubuntu-20-04-es
- Akamai Developer. (2023, 15 marzo). How to Install and Configure an NFS Linux Server and Client [Vídeo]. YouTube. https://www.youtube.com/watch?v=zmDIfJtCKCk
