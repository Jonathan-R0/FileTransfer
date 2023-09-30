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
        while not end:
            #Recieve data
            raw_data, address = self.socket.recvfrom(NORMAL_PACKAGE_SIZE)
            _, seq, end, error, data = struct.unpack(NORMAL_PACKAGE_FORMAT, raw_data) # TODO handle error
            print(f' Recieved package \n{data.decode()}\n from: {address} with len {len(data)}')

            #Respond to the client that i recieved the data
            self.file.append_chunk(data) # TODO append only when i checked that the chunk is the right one
            print(f' Recieved package from: {address} with seq: {seq} and end: {end}')
            self.socket.sendto(address, AckSeqPackage.pack_to_send(seq, seq))

        self.end()

