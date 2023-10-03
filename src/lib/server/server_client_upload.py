from lib.common.package import (
    InitialHandshakePackage,
    AckSeqPackage,
    NormalPackage
)
from lib.server.server_client import ServerClient
from lib.common.config import (
    RECEPTION_TIMEOUT,
    NORMAL_PACKAGE_SIZE,
    WINDOW_SIZE
)
import logging
from hashlib import md5
import struct


class ServerClientUpload(ServerClient):
    def __init__(
            self,
            initial_package: InitialHandshakePackage,
            address: bytes | tuple[str, int],
            dirpath: str
            ):
        super().__init__(initial_package, address, dirpath)

    def run(self) -> None:
        if self.failed:
            return
        self.create_socket_and_reply_handshake()
        self.socket.set_timeout(RECEPTION_TIMEOUT)
        try:
            raw_data, address = self.socket.recvfrom(NORMAL_PACKAGE_SIZE)
        except TimeoutError:
            self.end()
            return
        logging.debug(f' New client: {address}')
        self.socket.set_timeout(None)
        self.sw_upload(raw_data, address) if self.is_saw else self.sr_upload()

    def sw_upload(self, raw_data: bytes, address: tuple) -> None:
        if self.failed:
            return
        end = False
        last_seq = 0
        self.socket.set_timeout(RECEPTION_TIMEOUT)
        while True:
            try:
                if last_seq > 0:
                    raw_data, \
                        address = self.socket.recvfrom(NORMAL_PACKAGE_SIZE)
                _, seq, end, _, checksum, data = \
                    NormalPackage.unpack_from_client(raw_data)
                if any(data) and checksum != \
                        md5(struct.pack('256s', data)).digest():
                    logging.debug(' Checksum error for package ' +
                                  f'with seq: {seq}. Ignoring...')
                    continue

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
                if not end:
                    logging.debug(' A timeout has occurred, ' +
                                  'ending connection and ' +
                                  'deleting corrupted file')
                    self.file.rollback_write()
                break
        logging.debug(f' Client {self.address} ended')
        self.end()

    def sr_upload(self) -> None:
        if self.failed:
            return
        end = False
        received_chunks = {}
        base = 1
        has_end_pkg = False
        self.socket.set_timeout(RECEPTION_TIMEOUT)
        while True:
            try:
                # Recibo el paquete
                raw_data, address = self.socket.recvfrom(NORMAL_PACKAGE_SIZE)
                _, seq, end, _, checksum, data = \
                    NormalPackage.unpack_from_client(raw_data)
                if any(data) and checksum != \
                        md5(struct.pack('256s', data)).digest():
                    logging.debug(' Checksum error for package ' +
                                  f'with seq: {seq}. Ignoring... {any(data)}')
                    continue
                if end:
                    has_end_pkg = True
                logging.debug(f'Received package from: {address} with seq:' +
                              f' {seq} and end: {end} with len {len(data)}')

                # Si no tenia el paquete que me mandaron y esta
                # dentro de la ventana, lo guardo y mando confirmacion
                if seq not in received_chunks and \
                        base <= seq < base + WINDOW_SIZE:
                    received_chunks[seq] = data
                    self.socket.sendto(address,
                                       AckSeqPackage.pack_to_send(seq, seq))
                    logging.debug(f'Sending ack for seq: {seq}')
                elif seq in received_chunks:
                    # Si ya tenia el paquete, mando confirmacion de nuevo
                    self.socket.sendto(address,
                                       AckSeqPackage.pack_to_send(seq, seq))
                    logging.debug(f'Sending ack for seq: {seq}')
                elif seq < base:
                    self.socket.sendto(self.address,
                                       AckSeqPackage.pack_to_send(seq, seq))
                    logging.debug(f'Sending ack for seq: {seq}')
                # Chequeo si el paquete esta en sequencia
                # y lo agrego al archivo
                while base in received_chunks:
                    received_chunk = received_chunks[base]
                    del received_chunks[base]
                    self.file.append_chunk(received_chunk)
                    base += 1
            except TimeoutError:
                if not len(received_chunks) == 0 or \
                          (not has_end_pkg and len(received_chunks) == 0):
                    logging.debug(' A timeout has occurred, ' +
                                  'ending connection')
                    self.file_handler.rollback_write()
                break
        logging.debug(f' Client {self.address} ended')
        self.end()
