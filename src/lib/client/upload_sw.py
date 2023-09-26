from lib.common.package import NormalPackage, HandshakePackage, AckSeqPackage, InitialHandshakePackage
from lib.common.socket_wrapper import SocketWrapper
from lib.common.config import *
import logging
import os

class UploadStopAndWait:

    def __init__(self, host: str, port: int, file_path: str, file_name: str):
        self.host = host
        self.port = port
        self.file_path = file_path
        self.file_name = file_name
        self.socket_wrapper = SocketWrapper()
        self.socket_wrapper.bind(self.host, self.port)
    
    def start(self) -> None:   
        complete_file = os.path.join(self.file_path, self.file_name)
        if not os.path.isfile(complete_file):
            print(f"El archivo {complete_file} no existe.")
            return
        while true:
            first_package = HandshakePackage(True, os.path.getsize(complete_file), self.file_name)
            address = (self.host, self.port)
            data = first_package.pack_data_send()
            self.socket_wrapper.sendto(address, data)
            logging.debug(f' Sent data to {address}: {data}')
            # Y si nunca llega? como me doy cuenta?
            data, recv_address = self.socket_wrapper.recvfrom(NORMAL_PACKAGE_SIZE)
            if (recv_address is not adress):
                # No se si hay que codear algo en este caso
            handshake_package = HandshakePackage(data)
        # Cuando se confirma el primer envio, se lee el archivo y por cada lectura se envia un paquete
        with open(self.file_path + self.file_name, "r") as file:
            file = file.read()

        

    