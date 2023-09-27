import logging
import threading

from lib.common.package import InitialHandshakePackage, AckSeqPackage
from lib.common.socket_wrapper import SocketWrapper


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

    def create_socket_and_reply_handshake(self) -> None:
        self.socket = SocketWrapper()
        self.socket.bind(self.address[0], self.address[1])
        logging.debug(f' Replying to handshake from: {self.address}')
        self.socket.sendto(self.address, AckSeqPackage.pack_to_send(0, 0))

    def end(self) -> None:
        self.socket.close()
