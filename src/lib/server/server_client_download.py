from lib.common.package import InitialHandshakePackage
from lib.server.server_client import ServerClient
from lib.common.package import AckSeqPackage, NormalPackage
from lib.common.config import *
import logging

class ServerClientDownload(ServerClient):
    def __init__(self, initial_package: InitialHandshakePackage, address: bytes | tuple[str, int], dirpath: str):
        super().__init__(initial_package, address, dirpath)

    def start(self) -> None:
        end = False
        ack = 0
        seq = 1
        self.create_socket_and_reply_handshake()
        
        while not end:
            chunk, end = self.read_next_chunk(seq)
            if end or len(chunk) == 0:
                logging.debug(f' Sending last chunk: {chunk} with size: {len(chunk)}')
            if len(chunk) == 0:
                break
            self.socket.sendto(self.address, NormalPackage.pack_to_send(ack, seq, chunk, end, 0))
            raw_data, _ = self.socket.recvfrom(ACK_SEQ_SIZE)
            new_ack, new_seq = AckSeqPackage.unpack_from_client(raw_data)
            logging.debug(f' Recieved ack: {new_ack} and seq: {new_seq}')
            if new_seq == seq == new_ack:
                seq += 1
                ack += 1
            else:
                pass # TODO handle late or lost package
        self.end()

    def read_next_chunk(self, seq: int) -> tuple[bytes, bool]:
        self.file.seek((seq - 1) * DATA_SIZE)
        chunk = self.file.read(DATA_SIZE)
        logging.debug(f' Read chunk {chunk} with size: {len(chunk)}')
        return chunk, len(chunk) < DATA_SIZE
        