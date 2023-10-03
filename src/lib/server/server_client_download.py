from lib.common.package import InitialHandshakePackage
from lib.server.server_client import ServerClient
from lib.common.package import AckSeqPackage, NormalPackage
from lib.common.config import (
    SENDING_TIMEOUT,
    MAX_ATTEMPTS,
    ACK_SEQ_SIZE,
    WINDOW_SIZE,
)
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
        if self.failed:
            return
        self.create_socket()
        if self.is_saw:
            self.sw_download()
        else:
            self.sr_download()

    def sw_download(self):
        if self.failed:
            return
        end = False
        seq = 1
        lost_pkg_attempts = 0
        self.socket.set_timeout(SENDING_TIMEOUT)
        while not end and lost_pkg_attempts < MAX_ATTEMPTS:
            try:
                chunk, end = self.file.read_next_chunk(seq)
                if end:
                    logging.debug(
                        ' Sending last chunk with ' +
                        f'size: {len(chunk)}, seq:{seq} and end: {end}'
                    )
                self.socket.sendto(
                    self.address,
                    NormalPackage.pack_to_send(seq, chunk, end, 0)
                )
                while True:
                    raw_data, _ = self.socket.recvfrom(ACK_SEQ_SIZE)
                    new_seq = \
                        AckSeqPackage.unpack_from_client(raw_data)
                    if new_seq == 1:
                        logging.debug(f' New client: {self.address}')
                    logging.debug(f' Recieved ack with seq: {new_seq}')
                    if new_seq == seq :
                        lost_pkg_attempts = 0
                        seq += 1
                        break
            except TimeoutError:
                lost_pkg_attempts += 1
                logging.debug(' A timeout has occurred, no ack was recieved')
                end = False
        logging.debug(f' Client {self.address} ended')
        self.end()


    def sr_download(self):
        if self.failed:
            return
        end = False
        seq = 1
        next_seq_num = 1
        base = 1
        sent_chunks = {}
        attempts = 0
        seq_end = 0
        self.socket.set_timeout(SENDING_TIMEOUT)
        first_iteration = True
        while attempts <= MAX_ATTEMPTS:
            # Mando paquetes si tengo espacio en la ventana
            while next_seq_num < base + WINDOW_SIZE and not end:
                if(seq_end > 0 and next_seq_num > seq_end):
                    break
                chunk, end = self.file.read_next_chunk(next_seq_num)
                if end:
                    seq_end = next_seq_num

                if chunk or end or len(chunk) != 0:
                    packet = NormalPackage.pack_to_send(next_seq_num, chunk,
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
                raw_data = self.socket.recvfrom(ACK_SEQ_SIZE)
                seq = AckSeqPackage.unpack_from_server(raw_data)
                if first_iteration:
                    first_iteration = False
                    logging.debug(f' New client: {self.address}')
                logging.debug(f' Recieved ack with seq: {seq}')

                # Como recibi un ACK, muevo la ventana
                chunk_elements = [int(x) for x in sent_chunks.keys()]
                if seq == min(chunk_elements):
                    if len(chunk_elements) > 1:
                        base = min(chunk_elements)
                    else:
                        base = base + WINDOW_SIZE
                    attempts = 0

                # si el ACK esta en los que mande, lo saco de la lista
                if seq in sent_chunks:
                    attempts = 0
                    del sent_chunks[seq]

            except TimeoutError:
                if first_iteration:
                    self.end()
                    return
                # Timeout, reenvio todos los paquetes no confirmados
                attempts += 1
                if len(sent_chunks) > 0 and attempts <= MAX_ATTEMPTS:
                    logging.debug(' Timeout occurred. Resending ' +
                                  'unacknowledged chunks.')
                    for seq, chunk in sent_chunks.items():
                        if seq == seq_end:
                            end = True
                        else:
                            end = False
                        packet = NormalPackage.pack_to_send(
                                seq,
                                chunk,
                                end,
                                0
                            )
                        self.socket.sendto(self.address, packet)
                else:
                    break
        logging.debug(f' Client {self.address} ended')
        self.end()
