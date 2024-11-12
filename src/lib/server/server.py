import logging
from threading import Lock

from lib.common.config import (
    NORMAL_PACKAGE_SIZE,
    MAX_NUMBER_OF_CLIENTS
)
from lib.common.package import InitialHandshakePackage
from lib.common.socket_wrapper import SocketWrapper
from lib.server.server_client import ServerClient
from lib.server.server_client_download import ServerClientDownload
from lib.server.server_client_upload import ServerClientUpload


class Server:
    def __init__(self, host: str, port: int, dirpath: str):
        self.dirpath = dirpath
        self.clients = []
        self.clients_lock = Lock()
        self.socket_wrapper = SocketWrapper()
        self.socket_wrapper.bind(host, port)

    def start(self) -> None:
        logging.debug(' Listening...')
        while True:
            try:
                data, address = self.listen_to_new_connections()
                self.cleanup_old_clients()
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
            except KeyboardInterrupt:
                logging.debug(' Stopping server...')
                self.end()
                break

    def listen_to_new_connections(self) -> tuple[bytes, ...]:
        return self.socket_wrapper.recvfrom(NORMAL_PACKAGE_SIZE)

    def cleanup_old_clients(self) -> None:
        self.clients_lock.acquire()
        for client in [c[1] for c in self.clients]:
            if not client.is_alive():
                self.clients.remove((client.address, client))
                client.join()
        self.clients_lock.release()

    def push_client(self, client: ServerClient) -> None:
        if len(self.clients) >= MAX_NUMBER_OF_CLIENTS:
            logging.debug(' Max number of clients reached')
            return
        if client.address not in {c[0] for c in self.clients}:
            self.clients.append((client.address, client))
            client.start()

    def end(self) -> None:
        self.socket_wrapper.close()
        for client in [c[1] for c in self.clients]:
            client.end()
            client.join()
