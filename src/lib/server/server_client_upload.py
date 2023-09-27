from src.lib.common.package import InitialHandshakePackage
from src.lib.server.server_client import ServerClient


class ServerClientUpload(ServerClient):
    def __init__(self, initial_package: InitialHandshakePackage, address: bytes | tuple[str, int], dirpath: str):
        super().__init__(initial_package, address, dirpath)

    def start(self) -> None:
        self.create_socket()
        pass


