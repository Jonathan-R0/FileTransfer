from lib.common.config import ACK_SEQ_SIZE
from lib.common.socket_wrapper import SocketWrapper
from lib.common.package import *
from lib.client.config import rdt_protocol
import logging
import os


class UploadStopAndWait:

    def __init__(self, host: str, port: int, file_path: str, file_name: str):
        self.host = host
        self.port = port
        self.file = os.path.join(file_path, file_name)
        self.socket_wrapper = SocketWrapper()
        self.socket_wrapper.bind(self.host, 5050)

    def start(self) -> None:
        if not os.path.isfile(self.file):
            logging.debug(f'The file {self.file} does not exist.')
            return
        logging.debug(f' Performing hanshake to {self.host}:{self.port} with file {self.file}')
        self.socket_wrapper.sendto((self.host, self.port),
                                   InitialHandshakePackage.pack_to_send(True, rdt_protocol.is_saw(),
                                                                        os.path.getsize(self.file), self.file))
        logging.debug(f' Receiving ack, seq from {self.host}:{self.port}')
        data, server_address = self.socket_wrapper.recvfrom(ACK_SEQ_SIZE)
        ack, seq = AckSeqPackage.unpack_from_server(data)
        logging.debug(f' Ack: {ack}, Seq: {seq} from {server_address}')
