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
        self.socket.set_timeout(RECEPTION_TIMEOUT)
        try:
            raw_data, address = self.socket.recvfrom(NORMAL_PACKAGE_SIZE)
        except TimeoutError:
                self.end()
                return
        logging.debug(f' New client: {address}')
        self.socket.set_timeout(None)
        self.sw_upload(raw_data, address) if self.is_saw else self.sr_upload()
        # self.sr_upload()
        
    def sw_upload(self, raw_data: bytes, address) -> None:
        end = False
        last_seq = 0

        self.socket.set_timeout(RECEPTION_TIMEOUT)
        while True:
            # Recieve data
            try:
                if last_seq > 0:
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
                if not end:
                    logging.debug(' A timeout has occurred, ' +
                                'ending connection and deleting corrupted file')
                    self.file.rollback_write()
                break
        logging.debug(f' Client {self.address} ended')
        self.end()

    def sr_upload(self) -> None:
        end = False
        received_chunks = {}
        base = 1
        while not end:
            # Recibo el paquete
            raw_data, address = self.socket.recvfrom(NORMAL_PACKAGE_SIZE)
            _, seq, end, error, data = struct.unpack(NORMAL_PACKAGE_FORMAT,
                                                     raw_data)
            logging.debug(f'Received package from: {address} with seq:' +
                          f' {seq} and end: {end} with len {len(data)}')

            # Si no tenia el paquete que me mandaron y esta
            # dentro de la ventana, lo guardo y mando confirmacion
            if seq not in received_chunks and base <= seq < base + WINDOW_SIZE:
                received_chunks[seq] = data
                self.socket.sendto(address,
                                   AckSeqPackage.pack_to_send(seq, seq))
                logging.debug(f'Sending ack for seq: {seq}')
            elif seq in received_chunks:
                # Si ya tenia el paquete, mando confirmacion de nuevo
                self.socket.sendto(address,
                                   AckSeqPackage.pack_to_send(seq, seq))
                logging.debug(f'Sending ack for seq: {seq}')
            # Chequeo si el paquete esta en sequencia
            # y lo agrego al archivo
            while base in received_chunks:
                received_chunk = received_chunks.pop(base)
                self.file.append_chunk(received_chunk)
                base += 1
            # Si recibi el ultimo paquete, termino al toque roque
            if end:
                break
        logging.debug(f' Client {self.address} ended')
        self.end()
