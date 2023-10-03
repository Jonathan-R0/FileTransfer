import logging
import threading
import os

from lib.common.package import (
    InitialHandshakePackage, AckSeqPackage, NormalPackage)
from lib.common.socket_wrapper import SocketWrapper
from lib.common.file_handler import FileHandler
from lib.common.error_codes import (
    FILE_NOT_FOUND_ERROR_CODE,
    FILE_OPENING_OS_ERROR_CODE,
    FILE_ALREADY_EXISTS_ERROR_CODE,
    handle_error_codes_client
)


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
        self.failed = False
        try:
            path = os.path.join(dirpath, initial_package.file_name
                                                        .decode()
                                                        .rstrip("\0"))
            self.file = FileHandler(
                                    path,
                                    initial_package.is_upload,
                                    'wb' if initial_package.is_upload else 'rb'
                                )
        except FileNotFoundError:
            self.return_error_to_client(FILE_NOT_FOUND_ERROR_CODE)
        except OSError:
            self.return_error_to_client(FILE_OPENING_OS_ERROR_CODE)
        except ValueError:
            self.return_error_to_client(FILE_ALREADY_EXISTS_ERROR_CODE)

    def return_error_to_client(self, error: int) -> None:
        handle_error_codes_client(error)
        self.failed = True
        self.create_socket()
        self.socket.sendto(self.address,
                           NormalPackage.pack_to_send(0, 0, b'ERROR', True, error))
        self.socket.close()

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
        if not self.failed:
            self.file.close()
