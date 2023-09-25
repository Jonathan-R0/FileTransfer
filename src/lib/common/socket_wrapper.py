import socket


class SocketWrapper:

    def __init__(self):
        """Crea un socket UDP."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def bind(self, host: str, port: int) -> None:
        """El bind conecta el socket a un host y un puerto."""
        self.socket.bind((host, port))

    def sendto(self, address: str, data: str | bytes) -> None:
        """Envia un mensaje a la direccion especificada."""
        if isinstance(data, str):
            data = data.encode()
        self.socket.sendto(data=data, address=address)

    # El tamaño del mensaje deberia ser diferente segun el protocolo de envio?
    def recvfrom(self, buffer_size: int) -> tuple[str, ...]:
        """Recibe un mensaje de un cliente."""
        data, address = self.socket.recvfrom(buffer_size)
        return data.decode(), address

    def listen(self) -> tuple[str, ...]:
        """Escucha a un cliente."""
        data, address = self.recvfrom(1024)
        return data, address

    def close(self) -> None:
        """Cierra el socket."""
        self.socket.close()
