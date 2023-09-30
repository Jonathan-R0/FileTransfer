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
                #Posible bug en perdida de paquetes: que pasa si mandan un initial handshake package
                #porque el ack no llego al cliente? Hay que hacer un id de mensaje, para saber si es
                #un ack o un paquete normal
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

        self.socket.set_timeout(None) #Si termina el server, no se si hace falta esta linea
        self.end()

