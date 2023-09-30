from lib.common.package import InitialHandshakePackage, AckSeqPackage
from lib.server.server_client import ServerClient
from lib.common.file_handler import FileHandler
from lib.common.config import *
import logging
import struct

class ServerClientUpload(ServerClient):
    def __init__(self, initial_package: InitialHandshakePackage, address: bytes | tuple[str, int], dirpath: str):
        super().__init__(initial_package, address, dirpath)

    def start(self) -> None:
        self.create_socket_and_reply_handshake() 
        end = False
        last_seq = 0
        self.socket.set_timeout(TIMEOUT)
        while not end:
            #Recieve data
            try:
                raw_data, address = self.socket.recvfrom(NORMAL_PACKAGE_SIZE) 
                _, seq, end, error, data = struct.unpack(NORMAL_PACKAGE_FORMAT, raw_data)
                logging.debug(f' Recieved package \n{data}\n from: {address} with seq: {seq} and end: {end} with len {len(data)}')


                #Respond to the client that i recieved the data if the data is the next one
                if seq == last_seq +1:
                    last_seq = seq
                    self.file.append_chunk(data)
                    logging.debug(f' Recieved package from: {address} with seq: {seq} and end: {end}')
                    self.socket.sendto(address, AckSeqPackage.pack_to_send(seq, seq))
                else:
                    logging.debug(f' Recieved package from: {address} with seq: {seq} and end: {end} but missed previous package')
                    self.socket.sendto(address, AckSeqPackage.pack_to_send(last_seq, last_seq))
                
            except TimeoutError:
                logging.debug(' A timeout has occurred, no package was recieved')

                
        self.socket.set_timeout(TIMEOUT)
        self.end()