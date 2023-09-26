import threading

from src.lib.common.package import InitialHandshakePackage
from src.lib.common.socket_wrapper import SocketWrapper


class ServerClient(threading.Thread):
    def __init__(self, initial_package: InitialHandshakePackage, address: bytes | tuple[str, int], dirpath: str):
        super().__init__()
        self.address = address
        self.dirpath = dirpath
        self.file_name = initial_package.file_name
        self.file_size = initial_package.file_size
        self.is_saw = initial_package.is_saw
        self.address = address
        self.socket = None

    def create_socket(self) -> None:
        self.socket = SocketWrapper()
        self.socket.bind(self.address[0], self.address[1])

    def end(self) -> None:
        self.socket.close()
