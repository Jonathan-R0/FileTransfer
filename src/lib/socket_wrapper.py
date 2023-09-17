import socket

class SocketWrapper:
    
    # Crea un socket UDP
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # El bind conecta el socket a un host y un puerto
    def bind(self, host, port):
        self.socket.bind((host, port))

    # Envia un mensaje a la direccion especificada
    def sendto(self, data, address):
        if isinstance(data, str):
            data = data.encode()
        self.socket.sendto(data, address)

    # Recibe un mensaje de un cliente
    # El tamaño del mensaje deberia ser diferente segun el protocolo de envio?
    def recvfrom(self, buffer_size):
        data, address = self.socket.recvfrom(buffer_size)
        return data.decode(), address

    # Cierra el socket
    def close(self):
        self.socket.close()