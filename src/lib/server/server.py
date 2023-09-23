from threading import Lock
from lib.server.server_client_download import ServerClientDownload
from lib.server.server_client_upload import ServerClientUpload
from lib.common.socket_wrapper import SocketWrapper
import logging

class Server:
    def __init__(self, host: str, port: int, dirpath: str):
        self.host = host
        self.port = port
        self.dirpath = dirpath
        self.clients = []
        self.clients_lock = Lock()
        self.socket_wrapper = SocketWrapper(self.host, self.port)

    def start(self) -> None:
        logging.debug(' Listening...')
        self.socket_wrapper.listen()