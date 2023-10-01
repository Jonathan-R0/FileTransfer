from lib.common.package import InitialHandshakePackage, AckSeqPackage
from lib.server.server_client import ServerClient
from lib.common.config import (
    RECEPTION_TIMEOUT,
    # MAX_ATTEMPTS,
    NORMAL_PACKAGE_SIZE,
    NORMAL_PACKAGE_FORMAT,
    WINDOW_SIZE
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

        # lost_pkg_attempts = 0
        self.socket.set_timeout(RECEPTION_TIMEOUT)
        while not end:  # and lost_pkg_attempts < MAX_ATTEMPTS:
            # Recieve data
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
                    # lost_pkg_attempts = 0
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
                # logging.debug(' A timeout has occurred,
                # no package was recieved')
                logging.debug(' A timeout has occurred, ' +
                              'ending connection and deleting corrupted file')
                self.file.rollback_write()
                break
                ''' lost_pkg_attempts += 1
                if lost_pkg_attempts == MAX_ATTEMPTS and not end:
                    logging.debug(' Max attempts reached, ending connection ' +
                                  'and deleting corrupted file')
                    self.file.rollback_write() '''

        self.socket.set_timeout(None)
        self.end()

    def sr_upload(self) -> None:
        received_chunks = {}
        end = False
        available_seats = WINDOW_SIZE
        last_seq = 0
        # a chequear el while!! como en upload.py
        while not end and available_seats > 0:
            raw_data, address = self.socket.recvfrom(NORMAL_PACKAGE_SIZE)
            _, seq, end, error, data = struct.unpack(NORMAL_PACKAGE_FORMAT,
                                                     raw_data)
            logging.debug(
                    f' Recieved package \n{data}\n from: {address} ' +
                    f'with seq: {seq} and end: {end} with len {len(data)}'
                )
            # if i dont have the package, save it and send ack
            if seq not in received_chunks:
                received_chunks[seq] = data
                self.socket.sendto(
                    address,
                    AckSeqPackage.pack_to_send(seq, seq)
                )
                logging.debug(
                    f' Recieved package from: {address} ' +
                    f'with seq: {seq} and end: {end}'
                )
                available_seats -= 1
            else:
                # If the package was already received, send the same ack
                self.socket.sendto(
                    address,
                    AckSeqPackage.pack_to_send(seq, seq)
                )
            # if the package is next to the first one, write it and add a seat
            # also, check if there are more packages to write
            while (last_seq + 1) in received_chunks:
                last_seq += 1
                self.file.append_chunk(received_chunks[last_seq])
                available_seats += 1
                del received_chunks[last_seq]

            if end:
                break

        self.end()
