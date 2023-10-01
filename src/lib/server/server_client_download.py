from lib.common.package import InitialHandshakePackage
from lib.server.server_client import ServerClient
from lib.common.package import AckSeqPackage, NormalPackage
from lib.common.config import TIMEOUT, MAX_ATTEMPTS, ACK_SEQ_SIZE, \
                              WINDOW_SIZE
import logging


class ServerClientDownload(ServerClient):
    def __init__(
            self,
            initial_package: InitialHandshakePackage,
            address: bytes | tuple[str, int],
            dirpath: str
            ):
        super().__init__(initial_package, address, dirpath)

    def run(self) -> None:
        self.create_socket_and_reply_handshake()
        # self.sw_download() if self.is_saw else
        self.sr_download()

    def sw_download(self):
        end = False
        ack = 0
        seq = 1
        lost_pkg_attempts = 0

        self.socket.set_timeout(TIMEOUT)
        while not end and lost_pkg_attempts < MAX_ATTEMPTS:
            try:
                chunk, end = self.file.read_next_chunk(seq)
                if end or len(chunk) == 0:
                    logging.debug(
                        f' Sending last chunk: {chunk} with ' +
                        'size: {len(chunk)} and end: {end}'
                    )
                self.socket.sendto(
                    self.address,
                    NormalPackage.pack_to_send(ack, seq, chunk, end, 0)
                )
                raw_data, _ = self.socket.recvfrom(ACK_SEQ_SIZE)
                new_ack, new_seq = AckSeqPackage.unpack_from_client(raw_data)
                logging.debug(f' Recieved ack: {new_ack} and seq: {new_seq}')
                if new_seq == seq == new_ack:
                    lost_pkg_attempts = 0
                    seq += 1
                    ack += 1
                else:
                    lost_pkg_attempts += 1
            except TimeoutError:
                logging.debug(' A timeout has occurred, no ack was recieved')
                lost_pkg_attempts += 1

        self.socket.set_timeout(None)
        self.end()

    def sr_download(self):
        end = False
        seq = 1
        next_seq_num = 1
        base = 1
        sent_chunks = {}

        while not end or sent_chunks:

            # Mando paquetes si tengo espacio en la ventana
            while next_seq_num < base + WINDOW_SIZE and not end:
                chunk, end = self.file.read_next_chunk(next_seq_num)

                if chunk or end:
                    packet = NormalPackage.pack_to_send(0, next_seq_num, chunk,
                                                        end, 0)
                    self.socket.sendto(self.address, packet)
                    logging.debug(f' Sent chunk {next_seq_num} with size ' +
                                  f'{len(chunk)} and end: {end}')

                    # Me guardo el paquete que mande para reenviarlo
                    # si es necesario
                    sent_chunks[next_seq_num] = chunk
                    next_seq_num += 1

            try:
                # Ahora recibo un ACK
                raw_data, _ = self.socket.recvfrom(ACK_SEQ_SIZE)
                ack, seq = AckSeqPackage.unpack_from_server(raw_data)
                logging.debug(f' Recieved ack: {ack} and seq: {seq}')

                # si el ACK esta en los que mande, lo saco de la lista
                if seq in sent_chunks:
                    del sent_chunks[seq]

                # Como recibi un ACK, muevo la ventana
                base = seq + 1

            except TimeoutError:
                # Timeout, reenvio todos los paquetes no confirmados
                logging.debug('Timeout occurred. Resending ' +
                              'unacknowledged chunks.')
                for seq, chunk in sent_chunks.items():
                    packet = NormalPackage.pack_to_send(0, seq, chunk, end, 0)
                    self.socket.sendto(self.address, packet)
        self.end()
