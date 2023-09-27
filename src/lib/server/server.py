import logging
from threading import Lock
from typing import Tuple

from src.lib.common.config import NORMAL_PACKAGE_SIZE
from src.lib.common.package import InitialHandshakePackage
from src.lib.common.socket_wrapper import SocketWrapper
from src.lib.server.server_client import ServerClient
from src.lib.server.server_client_download import ServerClientDownload


class Server:
    def __init__(self, host: str, port: int, dirpath: str):
        self.host = host
        self.port = port
        self.dirpath = dirpath
        self.clients = []
        self.clients_lock = Lock()
        self.socket_wrapper = SocketWrapper()
        self.socket_wrapper.bind(self.host, self.port)

    def start(self) -> None:
        logging.debug(' Listening...')
        while True:
            data, address = self.listen_to_new_connections()
            initial_package = InitialHandshakePackage(data)
            self.clients_lock.acquire()
            self.push_client(ServerClientDownload(initial_package, address, self.dirpath) if initial_package.is_upload
                             else ServerClientDownload(initial_package, address, self.dirpath))
            self.clients_lock.release()

    def listen_to_new_connections(self) -> Tuple[bytes, ...]:
        return self.socket_wrapper.recvfrom(NORMAL_PACKAGE_SIZE)

    def push_client(self, client: ServerClient) -> None:
        if client.address not in self.clients:
            self.clients.append(client)
            client.start()

    def end(self) -> None:
        self.socket_wrapper.close()
        for client in self.clients:
            client.end()
            client.join()
