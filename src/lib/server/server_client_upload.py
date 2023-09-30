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
        self.socket.settimeout(TIMEOUT) #TODO revisar si esto esta bien
        while not end:
            #Recieve data
            try:
                raw_data, address = self.socket.recvfrom(NORMAL_PACKAGE_SIZE)
                _, seq, end, error, data = struct.unpack(NORMAL_PACKAGE_FORMAT, raw_data)
                logging.debug(f' Recieved package \n{data.decode()}\n from: {address} with seq: {seq} and end: {end} with len {len(data)}')


                #Respond to the client that i recieved the data if the data is the next one
                if last_seq + 1 == seq:
                    self.file.append_chunk(data)
                    logging.debug(f' Recieved package from: {address} with seq: {seq} and end: {end}')
                    self.socket.sendto(address, AckSeqPackage.pack_to_send(seq, seq))
                    last_seq == seq
                else :
                    self.socket.sendto(address, AckSeqPackage.pack_to_send(seq,last_seq))
                    logging.debug(f' Recieved package from: {address} with seq: {seq} and end: {end} but the last one was {last_seq}')

            except TimeoutError:
                logging.debug(' A timeout has occurred, no package was recieved')

        self.socket_wrapper.socket.settimeout(None)
        self.end()

