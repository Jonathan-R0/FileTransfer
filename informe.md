
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

