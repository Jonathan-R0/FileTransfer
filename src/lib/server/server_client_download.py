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

        self.socket.set_timeout(TIMEOUT)
        
        while not end:
            try:
                #send the next chunk
                chunk, end = self.file.read_next_chunk(seq)
                if end or len(chunk) == 0:
                    logging.debug(f' Sending last chunk: {chunk} with size: {len(chunk)} and end: {end}')
                
                self.socket.sendto(self.address, NormalPackage.pack_to_send(ack, seq, chunk, end, 0))

                #recieve, check if the package is the one and update ack and seq
                raw_data, _ = self.socket.recvfrom(ACK_SEQ_SIZE)
                new_ack, new_seq = AckSeqPackage.unpack_from_client(raw_data)
                logging.debug(f' Recieved ack: {new_ack} and seq: {new_seq}')
                if new_seq == seq == new_ack:
                    seq += 1
                    ack += 1
                else:
                    pass # TODO handle late or lost package
            except TimeoutError:
                logging.debug(' A timeout has occurred, no ack was recieved')
        
        self.socket.set_timeout(None)
        self.end()
        