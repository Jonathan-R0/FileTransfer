# File Transfer

| Padrón | Alumno                    |
|--------|---------------------------|
| 104105 | Jonathan David Rosenblatt |
| 104048 | Lautaro Francetich        |
| 104077 | Nicolás Marín Podesta     |
| 81027  | Gino Monterroso Carrillo  |

## Ejecución de los Programas

Para obtener la información de ejecución de cada programa se debe utilizar el flag `-h`

### Upload

```bash
python src/upload.py -v -H host -p 8080 -s path -n name
```

### Download

```bash
python src/download.py -v -H host -p 8080 -d path -n name
```

### Server

```bash
python src/start-server.py -v -H host -p 5050 -s path
```
