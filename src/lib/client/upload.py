from lib.common.config import ACK_SEQ_SIZE
from lib.common.socket_wrapper import SocketWrapper
from lib.common.package import *
from lib.client.config import *
import logging
import os
import time


class Upload:

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
        attempts = 0
        while attempts < MAX_ATTEMPTS:
            try:
                logging.debug(f' Performing hanshake to {self.host}:{self.port} with file {self.file}')
                self.socket_wrapper.sendto((self.host, self.port),
                                           InitialHandshakePackage.pack_to_send(True, rdt_protocol.is_saw(),
                                                                                os.path.getsize(self.file), self.file))
                logging.debug(f' Receiving ack, seq from {self.host}:{self.port}')
                data, server_address = self.socket_wrapper.recvfrom(ACK_SEQ_SIZE)
                ack, seq = AckSeqPackage.unpack_from_server(data)
                logging.debug(f' Ack: {ack}, Seq: {seq} from {server_address}')
            except Exception as e:
                logging.debug(f' Exception: {e}')
                attempts += 1
                continue
        self.stop_and_wait()

    def stop_and_wait(self) -> None:
        sequence_number = 0
        file_size = os.path.getsize(self.file)
        bytes_sent = 0
        end = False
        attempts = 0
        logging.debug(f' Start to send file {self.file} to {self.host}:{self.port}')
        while not end and attempts < MAX_ATTEMPTS:
            try:
                with open(self.file, 'rb') as file:
                    file.seek(bytes_sent)
                    data = file.read(256)
                if bytes_sent >= file_size:
                    end = True
                logging.debug(f' Sending package number {sequence_number}')
                package = NormalPackage.pack_to_send(0, sequence_number, end, 0, data)
                self.socket_wrapper.sendto((self.host, self.port), package)
                if not self.ack_receive(package, sequence_number):
                    logging.debug(f' File upload failed: too many attempts')
                    break
                bytes_sent += 256
                sequence_number += 1
            except Exception as e:
                logging.debug(f' Exception: {e}')
                attempts += 1
                if attempts == MAX_ATTEMPTS:
                    logging.debug(f' File upload failed: too many attempts')
                continue
    
    def ack_receive(self, package: bytes, sequence_number: int) -> bool:
        was_received = False
        attempts = 0
        while not was_received and attempts < MAX_ATTEMPTS:
            try:
                self.socket_wrapper.settimeout(1.0)
                logging.debug(f' Receiving ack, seq from {self.host}:{self.port}')
                data, server_address = self.socket_wrapper.recvfrom(ACK_SEQ_SIZE)
                ack, seq = AckSeqPackage.unpack_from_server(data)
                logging.debug(f' Ack: {ack}, Seq: {seq} from {server_address}')
                if seq == sequence_number:
                    was_received = True
                    logging.debug(f' Ack was received correctly')
                    self.socket_wrapper.settimeout(None)
            except self.socket_wrapper.timeout:
                logging.debug(f' A timeout has occurred, resend package')
                self.socket_wrapper.sendto((self.host, self.port), package)
                attempts += 1
                continue
        return was_received
        