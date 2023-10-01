# Trabajo Practico 1 - File Transfer

| Padrón | Alumno                    |
|--------|---------------------------|
| 104105 | Jonathan David Rosenblatt |
| 104048 | Lautaro Francetich        |
| 104077 | Nicolás Martín Podesta    |


# Informe

## **Introduccion**

El propósito del presente trabajo práctico consiste en desarrollar una aplicación de red dedicada a la transferencia de archivos entre sistemas cliente y servidor. Para alcanzar este fin, resulta esencial comprender los procesos de comunicación en redes, así como el modelo de servicio proporcionado por la capa de transporte a la capa de aplicación. Asimismo, para lograr el objetivo establecido, se adquirirá conocimiento sobre el uso de interfaces de sockets y los principios fundamentales de la transferencia de datos fiable.

## **Hipotesis y suposiciones realizadas**

Para el desarrollo del trabajo se asumio que el cliente y el servidor se encuentran en la misma red local. Esto es, que el cliente y el servidor se encuentran en la misma subred y que no hay routers entre ellos. Esto es importante ya que si hubiera routers entre ellos, el cliente no podria enviarle un mensaje al servidor ya que este no se encuentra en la misma subred.

1. No se pueden realizar descargas de archivos que no existen en el servidor o que esten siendo utilizados por otro cliente.

2. Si se carga/descarga un archivo con un nombre que ya existe en el servidor, este sera reemplazado por el nuevo archivo.

3. Si la descarga desde el servidor al cliente se interrumpe, el cliente se quedara con un archivo incompleto. No asi, en la carga del cliente al servidor, ya que el servidor descarta el archivo incompleto.

4. El tamaño maximo que puede tener un archivo es de 50mb.

5. Los paquetes tienen un tamaño de:
    a. Initial Message: 262 bytes
    b. ACK-SEQ Package: 8 bytes
    c. Data Package: 269 bytes

6. El tamaño de la ventana para selective repeat es de 10 paquetes.

7. El tamaño maximo del nombre de un archivo es de 256 bytes.

8. Se pueden tener hasta 100 clientes

## **Implementacion**

### Protocolo 

Para llevar a cabo una transferencia de archivos eficiente, es imperativo contar con un protocolo de envío de datos sólido, especialmente al utilizar el Protocolo de Datagramas de Usuario (UDP). UDP es un protocolo de comunicación sin conexión que no garantiza la entrega de los datos ni confirma su recepción. En este contexto, implementar un protocolo de envío se vuelve crucial para asegurar la integridad y confiabilidad de los datos transferidos. Este protocolo establece las reglas y formatos que deben seguir los datos durante su transmisión, lo que proporciona una estructura coherente para el proceso de envío y recepción. Así, al contar con un protocolo de envío adecuado para los datos en una conexión UDP, se maximiza la eficiencia y se garantiza la llegada segura de la información a su destino.

#### **Handshake**

El proceso de Handshake desempeña un papel crucial en las transferencias de archivos a través de conexiones UDP, proporcionando un método estructurado y confiable para la comunicación entre el cliente y el servidor. Este protocolo se caracteriza por un intercambio bidireccional de mensajes entre ambas partes, estableciendo así una conexión segura antes de la transmisión de datos. Durante el Handshake, el cliente inicia el proceso enviando un mensaje al servidor, quien, a su vez, responde con un acknowledgment. Es esencial destacar que el cliente aguarda este acknowledgment del servidor para proceder con el envío o la descarga del archivo correspondiente.

El formato del mensaje del Handshake se compone de 262 bytes, divididos en un encabezado (header) de 6 bytes y un sector de información de 256 bytes. El encabezado contiene cuatro elementos fundamentales:

1. **Carga/Descarga**: Un byte que indica si el cliente está cargando (upload) o descargando (download) un archivo.
2. **Stop and Wait**: Un byte que especifica si el cliente está utilizando el método Stop and Wait o Selective Repeat para la transmisión de datos.
3. **Tamaño del Archivo**: Cuatro bytes que indican el tamaño del archivo que se va a enviar.
4. **Nombre del Archivo**: Doscientos cincuenta y seis bytes que contienen el nombre del archivo a ser transferido.

En respuesta al mensaje del cliente, el servidor emite un acknowledgment de 8 bytes, que consta de dos componentes clave:

1. **ACK (Acknowledgment Number)**: Cuatro bytes que representan el número de acknowledgment.
2. **SEQ (Sequence Number)**: Cuatro bytes que denotan el número de secuencia.

En el contexto del Handshake, tanto el número de acknowledgment como el número de secuencia se establecen en 0, indicando que este es el primer mensaje que se envía en la transacción. Este enfoque estructurado y formal en el intercambio de información garantiza una transferencia de archivos segura y confiable a través de conexiones UDP.

#### **Transferencia de Archivos mediante Segmentación de Datos y Paquetes**

En el contexto de la transferencia de archivos, la información se segmenta en paquetes de 269 bytes, adaptándose dinámicamente al tamaño total de los datos. Estos paquetes se envían al servidor o al cliente, quienes los reciben y los almacenan en un archivo correspondiente. Una vez que se ha completado el proceso de Handshake y se ha establecido la conexión segura, la transferencia de archivos tiene lugar. Los paquetes que contienen datos están estructurados de la siguiente manera:

1. **ACK (Acknowledgment Number)**: Cuatro bytes que indican el número de acknowledgment, confirmando la recepción del paquete.
2. **SEQ (Sequence Number)**: Cuatro bytes que indican el número de secuencia del paquete, identificando su posición en la secuencia de datos.
3. **END (End of File)**: Un byte que indica si este es el último paquete de la secuencia o si hay más por seguir.
4. **ERROR (Error Code)**: Cuatro bytes que señalan si ha ocurrido algún error durante la transferencia, proporcionando un código específico para identificar el tipo de error.
5. **DATA**: Doscientos cincuenta y seis bytes que contienen la información del archivo a ser transferido.

Estos paquetes son transmitidos al servidor o al cliente, quienes los reciben y los almacenan en un archivo local. Una vez que el paquete es recibido con éxito, el cliente o el servidor envía un acknowledgment al otro para confirmar la recepción correcta del paquete. En el caso de que el paquete no llegue correctamente, el cliente o el servidor no emite el acknowledgment, lo que indica al host emisor que debe reenviar el paquete para garantizar una transferencia sin errores.

Es esencial destacar que, aunque reenviar el paquete es una práctica común para asegurar la integridad de la transferencia, se establece un límite máximo de intentos para evitar posibles bucles infinitos. Cuando se alcanza este límite, se concluye la transferencia, asegurando así un manejo efectivo de los errores y una transmisión segura y eficiente de los archivos entre el cliente y el servidor.


### **Implementación de Stop and Wait y Selective Repeat en el Protocolo de Transferencia de Archivos**

**STOP AND WAIT:**

En nuestra implementación del protocolo Stop and Wait, se utiliza un tamaño de ventana de 1. Esto implica que el cliente está limitado a enviar un único paquete a la vez y debe aguardar la recepción del acknowledgment por parte del servidor antes de poder enviar el siguiente paquete. En caso de que el acknowledgment no llegue dentro de un intervalo de tiempo predefinido, el cliente procede a reenviar el paquete. 

Por otro lado, si el servidor recibe un paquete que no es el esperado, simplemente lo ignora y espera la llegada del paquete correcto antes de responder.

**SELECTIVE REPEAT:**

Por otro lado, en la implementación de Selective Repeat, se establece una ventana de tamaño 10 para el envío de paquetes. Esto significa que el cliente tiene la capacidad de enviar hasta 10 paquetes simultáneamente, esperando a que el servidor le envíe los acknowledgments correspondientes. En caso de que el servidor reciba un paquete incorrecto, lo ignora y espera por el paquete correcto. Si el cliente no recibe un acknowledgment dentro del tiempo especificado, reenvía el paquete correspondiente.

En situaciones donde el cliente recibe un paquete duplicado, reenvía el acknowledgment del paquete que ya ha recibido previamente. Si el paquete recibido es el esperado, se almacena para su posterior procesamiento y se emite el acknowledgment correspondiente. Esta implementación permite una gestión eficiente y segura de la transferencia de archivos, garantizando la integridad y la confiabilidad del proceso, ya sea mediante el enfoque de Stop and Wait o Selective Repeat.

## Pruebas

ACA van las pruebassssssssssssssssssssssssssssssss XD

## Preguntas

### Arquitectura Cliente Servidor

La arquitectura cliente servidor consiste de tener un proceso ejecutandose constantemente en el servidor la cual recibe requests de otros procesos que se ejecutan en un cliente. El cliente esta preparado para saber comunicarse con el servidor mediante un protocolo preestablecido. El ciclo de vida de interacciones consiste de que se establezca una conexion y el servidor pueda responder las consultas que le realice el proceso cliente

### La Funcion de un Protocolo de Capa de Aplicacion

La funcion de un protocolo de capa de aplicacion es comunicar distintos hosts a traves de la red. Establece la comunicacion entre los end hosts. 

### Protocolo utilizado

Nuestro protocolo consta de realizar RDT. Primero realizamos un handshake, donde el cliente le envia al host un mensaje inicial y este debe responderle con un acknowledgment.

Luego en funcion de la operacion a realizar se ejecuta una parte diferente del proceso.

Si estamos haciendo un upload con stop and wait el cliente enviara en un loop chunks del archivo a la vez que, entre cada paquete que envia, estara esperando el acknowledgment del servidor para saber que este llego correctamente. Si se usa el protocolo de selective repeat utilizamos una ventana de $N$ paquetes para hacer mas eficiente la espera de los ack.

En cambio si estamos haciendo un download, es el cliente que espera los paquetes y responde con los acknowledgments. Una explicacion mas detallada del protocolo se encuentra en la seccion de implementacion del informe.

### Diferencias Entre TCP y UDP

Con respecto a las caracteristicas y servicios que ofrece cada uno, sabemos que UPD provee una comunicacion libre y bidireccional entre procesos. Ademas otro feature que posee es un simple chequeo de errores mediante un checksum. TCP en cambio realiza una transferencia de datos que por default es RDT (reliable data transfer), es decir, los paquetes llegan integros, sin errores, en el orden correcto y sin duplicados. TCP tambien ofrece control de flujo y congestion.

TCP ademas posee un pequeño delay debido al establecimiento de la conexion RDT con respecto a UDP. 

El header de UDP es de 8 bytes mientras que el header de TCP es de 20 bytes.

UDP es preferible sobre TCP para aplicaciones donde no es un problema importante la perdida poco comun de paquetes. Por ejemplo en servicios de audio o video, donde no molesta perder alguna parte de un frame de una transmision. De lo contrario, si la comunicacion debe ser confiable, se utiliza TCP.

## Dificultades Encontradas

Fue dificil debuggear instancias de problemas relacionadas con la perdida de paquetes. Resulto complicado producto de varios casos borde que no habiamos tenido en cuenta y por la extensa logica empleada en los archivos.

Tambien resulto interesante y no por ello facil, definir la estrucutura de los paquetes. Siempre evitamos agregar datos para que este sea lo mas ligero posible. A veces esto no se podia hacer, por ejemplo con el paquete normal que posee un booleano de finalizacion.

Nos resulto finalmente extremadamente complicado dividir las tareas entre los integrantes del grupo, mayoritariamente en el desarrollo inicial del proyecto. Esto, junto con que fuimos tres personas desarrollando el trabajo (dado que nuestro cuarto integrante abandono la materia) dificulto mucho el proceso.

## Conclusiones

Aprendimos que para el manejo de redes, es util utilizar metodos de ejecucion concurrente pero que deben ser cuidadosamente analizados para evitar crear vulnerabilidades en el host. Por ejemplo, podria pasar que si no verificamos la cantidad de clientes ejecutandose concurrentemente, un atacante podria enviar muchos requests en paralelo, lo cual agotaria los recursos del server producto de que cada thread necesita recursos de la maquina.

Pudimos implementar correctamente los dos protocolos Stop and Wait y Selective Repeat.
