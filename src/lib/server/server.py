import logging
from threading import Lock

from lib.common.config import NORMAL_PACKAGE_SIZE
from lib.common.package import InitialHandshakePackage
from lib.common.socket_wrapper import SocketWrapper
from lib.server.server_client import ServerClient
from lib.server.server_client_download import ServerClientDownload
from lib.server.server_client_upload import ServerClientUpload


class Server:
    def __init__(self, host: str, port: int, dirpath: str):
        self.host = host
        self.port = port
        self.dirpath = dirpath
        self.clients = []
        self.clients_lock = Lock()
        self.socket_wrapper = SocketWrapper()
        self.socket_wrapper.bind("", self.port)

    def start(self) -> None:
        logging.debug(' Listening...')
        while True:
            data, address = self.listen_to_new_connections()
            logging.debug(' ...')
            initial_package = InitialHandshakePackage(data)
            self.clients_lock.acquire()
            self.push_client(ServerClientUpload(
                                initial_package,
                                address,
                                self.dirpath
                            )
                            if initial_package.is_upload
                            else ServerClientDownload(
                                initial_package,
                                address,
                                self.dirpath
                            ))
            self.clients_lock.release()

    def listen_to_new_connections(self) -> tuple[bytes, ...]:
        return self.socket_wrapper.recvfrom(NORMAL_PACKAGE_SIZE)

    def push_client(self, client: ServerClient) -> None:
        if client.address not in self.clients:
            self.clients.append(client)
            logging.debug(f' New client: {client.address}')
            client.start()

    def end(self) -> None:
        self.socket_wrapper.close()
        for client in self.clients:
            client.end()
            client.join()
