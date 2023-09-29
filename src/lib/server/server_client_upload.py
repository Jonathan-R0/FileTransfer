from lib.common.package import InitialHandshakePackage
from lib.server.server_client import ServerClient
from lib.common.config import *

class ServerClientUpload(ServerClient):
    def __init__(self, initial_package: InitialHandshakePackage, address: bytes | tuple[str, int], dirpath: str):
        super().__init__(initial_package, address, dirpath)

    def start(self) -> None:
        self.create_socket_and_reply_handshake()
        end = False
        while not end:
            raw_data, address = self.socket.recvfrom(NORMAL_PACKAGE_SIZE)
            print(f' Recieved package \n{raw_data.decode()}\n from: {address} with len {len(raw_data)}')
            _, seq, end, error, data = struct.unpack(NORMAL_PACKAGE_FORMAT, raw_data) # TODO handle error
            file_handler.append_chunk(data)
            print(f' Recieved package from: {address} with seq: {seq} and end: {end}')
            socket.sendto(address, AckSeqPackage.pack_to_send(seq, seq))
        self.end()

