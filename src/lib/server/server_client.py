import logging
import threading
import os

from lib.common.package import (
    InitialHandshakePackage, AckSeqPackage, NormalPackage)
from lib.common.socket_wrapper import SocketWrapper
from lib.common.file_handler import FileHandler


class ServerClient(threading.Thread):
    def __init__(
            self,
            initial_package: InitialHandshakePackage,
            address: bytes | tuple[str, int],
            dirpath: str
            ):
        super().__init__()
        self.file_size = initial_package.file_size
        self.is_saw = initial_package.is_saw
        self.address = address
        self.socket = None
        try:
            path = os.path.join(dirpath, initial_package.file_name
                                                        .decode()
                                                        .rstrip("\0"))
            self.file = FileHandler(open(
                file=path,
                mode='wb' if initial_package.is_upload else 'rb'))
        except FileNotFoundError:
            self.return_error_to_client(404)
        except OSError:
            self.return_error_to_client(500)
        except ValueError:
            self.return_error_to_client(404)

        # TODO cambiar los errores para que no matcheen los codigos de error
        # http mas que nada para evitar quejas por implementar algo de una
        # capa superior.

    def return_error_to_client(self, error: int) -> None:
        self.socket.sendto(self.address,
                           NormalPackage.pack_to_send(0, 0, b'', True, error))

    def create_socket_and_reply_handshake(self) -> None:
        self.create_socket()
        logging.debug(f' Replying to handshake from: {self.address}')
        self.socket.sendto(self.address, AckSeqPackage.pack_to_send(0, 0))

    def create_socket(self) -> None:
        self.socket = SocketWrapper()
        self.socket.bind("", 0)

    def end(self) -> None:
        logging.debug(f' Ending client thread: {self.address}')
        self.socket.close()
        self.file.close()
