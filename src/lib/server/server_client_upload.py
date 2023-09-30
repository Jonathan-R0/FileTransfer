from lib.common.package import InitialHandshakePackage, AckSeqPackage
from lib.server.server_client import ServerClient
from lib.common.config import (
    TIMEOUT,
    MAX_ATTEMPTS,
    NORMAL_PACKAGE_SIZE,
    NORMAL_PACKAGE_FORMAT
)
import logging
import struct


class ServerClientUpload(ServerClient):
    def __init__(
            self,
            initial_package: InitialHandshakePackage,
            address: bytes | tuple[str, int],
            dirpath: str
            ):
        super().__init__(initial_package, address, dirpath)

    def start(self) -> None:
        self.create_socket_and_reply_handshake()
        self.sw_upload() if self.is_saw else self.sr_upload()

    def sw_upload(self) -> None:
        end = False
        last_seq = 0
        lost_pkg_attempts = 0
        self.socket.set_timeout(TIMEOUT)
        while not end and lost_pkg_attempts < MAX_ATTEMPTS:
            try:
                raw_data, address = self.socket.recvfrom(NORMAL_PACKAGE_SIZE)
                _, seq, end, error, data = struct.unpack(NORMAL_PACKAGE_FORMAT,
                                                         raw_data)
                logging.debug(
                    f' Recieved package \n{data}\n from: {address} ' +
                    f'with seq: {seq} and end: {end} with len {len(data)}'
                )

                if seq == last_seq + 1:
                    last_seq = seq
                    self.file.append_chunk(data)
                    logging.debug(
                        f' Recieved package from: {address} ' +
                        f'with seq: {seq} and end: {end}'
                    )
                    self.socket.sendto(
                        address,
                        AckSeqPackage.pack_to_send(seq, seq)
                    )
                else:
                    logging.debug(
                        f' Recieved package from: {address} with seq: ' +
                        f'{seq} and end: {end} but missed previous package'
                    )
                    self.socket.sendto(
                        address,
                        AckSeqPackage.pack_to_send(last_seq, last_seq)
                    )

            except TimeoutError:
                logging.debug(' A timeout has occurred, ' +
                              'no package was recieved')
                lost_pkg_attempts += 1
                if lost_pkg_attempts == MAX_ATTEMPTS and not end:
                    logging.debug(' Max attempts reached, ending connection ' +
                                  'and deleting corrupted file')
                    self.file.rollback_write()

        self.socket.set_timeout(None)
        self.end()

    def sr_upload(self) -> None:
        pass
