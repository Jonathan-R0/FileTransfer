import logging
import threading
import os

from lib.common.package import InitialHandshakePackage, AckSeqPackage, NormalPackage
from lib.common.socket_wrapper import SocketWrapper
from lib.common.config import *


class ServerClient(threading.Thread):
    def __init__(self, initial_package: InitialHandshakePackage, address: bytes | tuple[str, int], dirpath: str):
        super().__init__()
        self.address = address
        self.file_size = initial_package.file_size
        self.is_saw = initial_package.is_saw
        self.address = address
        self.socket = None
        try:
            self.file = open(os.path.join(dirpath, initial_package.file_name), 'wb')
        except OSError as e:
            self.return_error_to_client(500)
        except ValueError as e:
            self.return_error_to_client(404)

    def return_error_to_client(self, error: int) -> None:
        self.socket.sendto(self.address, NormalPackage.pack_to_send(0, 0, b'', True, error))

    def create_socket_and_reply_handshake(self) -> None:
        self.socket = SocketWrapper()
        self.socket.bind("", 0)
        logging.debug(f' Replying to handshake from: {self.address}')
        self.socket.sendto(self.address, AckSeqPackage.pack_to_send(0, 0))

    def separate_file_into_chunks(self) -> list[bytes]:
        chunks = []
        while True:
            chunk = self.file.read(256)
            if not chunk:
                break
            chunks.append(chunk)
        return chunks

    def send_chunk_sw(self, seq: int, end_flag: bool) -> tuple[int, int]:
        self.socket.sendto(self.address, NormalPackage.pack_to_send(0, seq, self.separate_file_into_chunks()[seq], end_flag, 0))
        ackseq_data = self.socket.recvfrom(ACK_SEQ_SIZE)
        ack_recieved, seq_recieved = AckSeqPackage.unpack_from_client(ackseq_data)
        return ack_recieved, seq_recieved

    def end(self) -> None:
        self.socket.close()
        self.file.close()
        logging.debug(f' Client {self.address} ended')
