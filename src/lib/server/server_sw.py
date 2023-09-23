from threading import Lock
from lib.server.server_client_download import ServerClientDownload
from lib.server.server_client_upload import ServerClientUpload
from lib.common.package import Package
from lib.common.socket_wrapper import SocketWrapper
import logging

class ServerStopAndWait:
    def __init__(self, host: str, port: int, dirpath: str):
        self.host = host
        self.port = port
        self.dirpath = dirpath
        self.clients = []
        self.clients_lock = Lock()
        self.socket_wrapper = SocketWrapper(self.host, self.port)

    def start(self) -> None:
        logging.debug(' Listening...')
        while True:
            data, address = self.socket_wrapper.recvfrom()
            logging.debug(f' Received data from {address}: {data}')
            try:
                package = Package.parse_data(data)
            except:
                logging.debug(' Invalid package')
                continue

            if package.is_initial_message():
                self.handle_initial_message(package, address)
            else:
                self.handle_data(package, address)



            

            