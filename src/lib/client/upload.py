from lib.common.config import *
from lib.common.socket_wrapper import SocketWrapper
from lib.common.file_handler import FileHandler
from lib.common.package import *
from lib.client.config import *
import logging
import os
import time


class Upload:

    def __init__(self, server_address: (str,str), file_path: str, file_name: str):
        self.server_address = server_address
        self.file = os.path.join(file_path, file_name)
        self.socket_wrapper = SocketWrapper()
        self.socket_wrapper.bind("", 0)
        self.file_handler = FileHandler(open(file=self.file, mode='rb'))

    def start(self) -> None:
        if not os.path.isfile(self.file):
            logging.debug(f'The file {self.file} does not exist.')
            return
        if not self.complete_handshake():
            logging.debug(f' Handshake failed')
            return
        self.stop_and_wait()

    def complete_handshake(self) -> None:    
        attempts = 0
        while attempts < MAX_ATTEMPTS:
            try:
                logging.debug(f' Performing hanshake to {self.server_address[0]}:{self.server_address[1]} with file {self.file}')
                package = InitialHandshakePackage.pack_to_send(True, rdt_protocol.is_saw(), 
                                                                    self.file_handler.size(), self.file) # es el path o solo el nombre del file?
                self.socket_wrapper.sendto(self.server_address, package)
                if not self.ack_receive(package, 0):
                    break
            except Exception as e:
                logging.debug(f' Exception: {e}')
                attempts += 1
                continue
    
    def ack_receive(self, package: bytes, sequence_number: int) -> bool:
        was_received = False
        attempts = 0
        while not was_received and attempts < MAX_ATTEMPTS:
            try:
                self.socket_wrapper.socket.settimeout(1.0) # Quizas se puede disminuir
                logging.debug(f' Receiving ack, seq from {self.server_address[0]}:{self.server_address[1]}')
                data, server_address = self.socket_wrapper.recvfrom(ACK_SEQ_SIZE)
                if (server_address != self.server_address):
                    continue
                ack, seq = AckSeqPackage.unpack_from_server(data)
                logging.debug(f' Ack: {ack}, Seq: {seq} from {self.server_address}')
                if seq == sequence_number:
                    was_received = True
                    logging.debug(f' Ack was received correctly')
            except TimeoutError:
                logging.debug(f' A timeout has occurred, resend package')
                self.socket_wrapper.sendto(self.server_address, package)
                attempts += 1
                continue
            except Exception as e:
                logging.debug(f' Exception: {e}')
                attempts += 1
                continue
        self.socket_wrapper.socket.settimeout(None)
        return was_received

    def stop_and_wait(self) -> None:
        sequence_number = 0
        file_size = os.path.getsize(self.file)
        bytes_sent = 0
        end = False
        attempts = 0
        logging.debug(f' Start to send file {self.file} to {self.server_address[0]}:{self.server_address[1]}')
        while not end and attempts < MAX_ATTEMPTS:
            try:
                chunk, end = file_handler.read_next_chunk(seq)
                if end or len(chunk) == 0:
                    logging.debug(f' Sending last chunk: {chunk} with size: {len(chunk)}')
                if len(chunk) == 0:
                    break
                package = NormalPackage.pack_to_send(0, sequence_number, end, 0, data)
                self.socket_wrapper.sendto(self.server_address, package)
                if not self.ack_receive(package, sequence_number):
                    logging.debug(f' File upload failed: too many attempts')
                    break
                bytes_sent += DATA_SIZE
                sequence_number += 1
            except Exception as e:
                logging.debug(f' Exception: {e}')
                attempts += 1
                if attempts == MAX_ATTEMPTS:
                    logging.debug(f' File upload failed: too many attempts')
                continue
        