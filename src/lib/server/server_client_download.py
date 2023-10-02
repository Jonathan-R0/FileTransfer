from lib.common.package import InitialHandshakePackage
from lib.server.server_client import ServerClient
from lib.common.package import AckSeqPackage, NormalPackage
from lib.common.config import (
    SENDING_TIMEOUT,
    RECEPTION_TIMEOUT,
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
        if self.is_saw:
            self.create_socket()
            self.sw_download()
        else:
            self.create_socket_and_reply_handshake()
            self.sr_download()

    def sw_download(self):
        end = False
        ack = 0
        seq = 1
        lost_pkg_attempts = 0
        self.socket.set_timeout(SENDING_TIMEOUT)
        while not end and lost_pkg_attempts < MAX_ATTEMPTS:
            try:
                chunk, end = self.file.read_next_chunk(seq)
                if end:
                    logging.debug(
                        f' Sending last chunk: {chunk} with ' +
                        'size: {len(chunk)} and end: {end}'
                    )
                self.socket.sendto(
                    self.address,
                    NormalPackage.pack_to_send(ack, seq, chunk, end, 0)
                )
                while True:
                    raw_data, _ = self.socket.recvfrom(ACK_SEQ_SIZE)
                    new_ack, new_seq = \
                        AckSeqPackage.unpack_from_client(raw_data)
                    logging.debug(f' Recieved ack: {new_ack} & seq: {new_seq}')
                    logging.debug(f' New client: {self.address}')
                    if new_seq == seq == new_ack:
                        lost_pkg_attempts = 0
                        seq += 1
                        ack += 1
                        break
            except TimeoutError:
                if (ack == 0):
                    self.end()
                    return
                lost_pkg_attempts += 1
                logging.debug(' A timeout has occurred, no ack was recieved')
                end = False
        logging.debug(f' Client {self.address} ended')
        self.end()

    def sr_download(self):
        end = False
        seq = 1
        next_seq_num = 1
        base = 1
        sent_chunks = {}
        attempts = 0
        seq_end = 0
        self.socket.set_timeout(RECEPTION_TIMEOUT)
        while attempts <= MAX_ATTEMPTS:
            # Mando paquetes si tengo espacio en la ventana
            while next_seq_num < base + WINDOW_SIZE and not end:
                chunk, end = self.file.read_next_chunk(next_seq_num)
                if end:
                    seq_end = next_seq_num

                if chunk or end or not len(chunk) == 0:
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
                print(f"sent chunks: {sent_chunks.keys()}")
                ack, seq = AckSeqPackage.unpack_from_server(raw_data)
                logging.debug(f' Recieved ack: {ack} and seq: {seq}')

                # Como recibi un ACK, muevo la ventana
                chunk_elements = [int(x) for x in sent_chunks.keys()]
                if seq == min(chunk_elements):
                    if len(chunk_elements) > 1:
                        base = min(chunk_elements)
                        print(f"new base: {base}")
                    else:
                        base = base + WINDOW_SIZE
                        print(f"new base: {base}")
                    attempts = 0

                # si el ACK esta en los que mande, lo saco de la lista
                if seq in sent_chunks:
                    attempts = 0
                    del sent_chunks[seq]


            except TimeoutError:
                # Timeout, reenvio todos los paquetes no confirmados
                attempts += 1
                print(f"attempts: {attempts}, chunks: {sent_chunks.keys()}")
                if len(sent_chunks) > 0 and attempts <= MAX_ATTEMPTS:
                    logging.debug('Timeout occurred. Resending ' +
                                  'unacknowledged chunks.')
                    for seq, chunk in sent_chunks.items():
                        if seq == seq_end:
                            end = True
                        else:
                            end = False
                        packet = NormalPackage.pack_to_send(
                                0,
                                seq,
                                chunk,
                                end,
                                0
                            )
                        self.socket.sendto(self.address, packet)
                else:
                    print("aca")
                    break

        logging.debug(f' Client {self.address} ended')
        self.end()
