# File Transfer

| Padrón | Alumno                    |
|--------|---------------------------|
| 104105 | Jonathan David Rosenblatt |
| 104048 | Lautaro Francetich        |
| 104077 | Nicolás Martín Podesta    |

## Ejecución de los Programas

Para obtener la información de ejecución de cada programa se debe utilizar el flag `-h`

## Ejecución del programa
### Inicializar el servidor

```python
python3.10 start-server.py -v -H host -p port -s /database
```

### Upload file to the server with Stop & Wait

```python
python3.10 upload.py -v -s /source -n file -H host -p port -sw
```

### Download file to the server with Stop & Wait

```python
python3.10 download.py -v -d /destination -n file -H host -p port -sw
```

### Upload file to the server with Selective Repeat

```python
python3.10 upload.py -v -s /source -n file -H host -p port -sr
```

### Download file to the server with Selective Repeat

```python
python3.10 download.py -v -d /destination -n file -H host -p port -sr
```

## Tamaños de Paquete

- Initial Message:

```
+-------------------+---------------------+--------------------+------------------------+
|   carga/descarga  |  is stop and wait   |       fsize        |        filename        |
|      1 byte       |       1 byte        |      4 bytes       |        256 bytes       |
+-------------------+---------------------+--------------------+------------------------+
Total -> 262 bytes
```

- ACK-SEQ Package

```
+-------------------+---------------------+
|        ack        |         seq         |
|      4 bytes      |       4 bytes       |
+-------------------+---------------------+
Total -> 8 bytes
```

- Paquete normal:

```
+-------------------+---------------------+--------------------+------------------------+------------------------+
|        ack        |         seq         |         end        |         error          |          data          |
|      4 bytes      |       4 bytes       |        1 byte      |        4 bytes         |        256 bytes       |
+-------------------+---------------------+--------------------+------------------------+------------------------+
Total -> 269 bytes
```
