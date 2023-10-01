from lib.client.upload_args import uploader_args
from lib.common.socket_wrapper import SocketWrapper
from lib.common.package import (
    InitialHandshakePackage,
    AckSeqPackage,
    NormalPackage
)
from lib.common.file_handler import FileHandler
from lib.common.config import (
    MAX_ATTEMPTS,
    ACK_SEQ_SIZE,
    WINDOW_SIZE,
    SENDING_TIMEOUT
)
import logging
import os

if uploader_args.verbose:
    logging.basicConfig(level=logging.DEBUG)


def comp_host(host1: str, host2: str) -> bool:
    local_host_addr = {'localhost', '127.0.0.1'}
    return host1 == host2 or\
        (host1 in local_host_addr and host2 in local_host_addr)


def sw_client_upload(
        socket: SocketWrapper,
        file_handler: FileHandler,
        address: tuple
        ) -> None:
    end = False
    ack = 0
    seq = 1
    lost_pkg_attempts = 0
    while not end and lost_pkg_attempts < MAX_ATTEMPTS:
        try:
            chunk, end = file_handler.read_next_chunk(seq)
            if end or len(chunk) == 0:
                logging.debug(
                    f' Sending last chunk: {chunk} with size: {len(chunk)}')
            socket.sendto(address, NormalPackage.pack_to_send(ack, seq,
                          chunk, end, 0))
            while True:
                raw_data, _ = socket.recvfrom(ACK_SEQ_SIZE)
                new_ack, new_seq = AckSeqPackage.unpack_from_server(raw_data)
                logging.debug(f' Recieved ack: {new_ack} and seq: {new_seq}')
                if new_seq == seq == new_ack:
                    lost_pkg_attempts = 0
                    seq += 1
                    ack += 1
                    break
        except TimeoutError:
            lost_pkg_attempts += 1
            logging.debug(' A timeout has occurred, no ack was recieved')
    logging.debug(f' Client {address} ended')


def resend_missing_chunks(
        socket: SocketWrapper,
        address: tuple,
        sent_chunks: dict[int, bytes]
        ) -> None:
    for seq, chunk in sent_chunks.items():
        socket.sendto(address, NormalPackage.pack_to_send(0, seq, chunk, 0, 1))
        logging.debug(f' Resending chunk with seq:{seq} and size:{len(chunk)}')


def sr_client_upload(
        socket: SocketWrapper,
        file_handler: FileHandler,
        address: tuple
        ) -> None:
    end = False
    ack = 0
    seq = 1
    avalable_seats = WINDOW_SIZE
    sent_chunks = {}
    # los while habria que revisarlos
    while not end:
        try:
            while avalable_seats > 0:
                # envio los que entren en mi window
                chunk, end = file_handler.read_next_chunk(seq)
                if end or len(chunk) == 0:
                    logging.debug(
                        f' Sending last chunk: {chunk} with size:{len(chunk)}')
                socket.sendto(address, NormalPackage.pack_to_send(ack, seq,
                              chunk, end, 0))
                avalable_seats -= 1
                seq += 1
                ack += 1
                sent_chunks[seq] = chunk

                # una vez que envie todos los que entran en mi window ack
                raw_data, _ = socket.recvfrom(ACK_SEQ_SIZE)
                new_ack, new_seq = AckSeqPackage.unpack_from_server(raw_data)
                logging.debug(f' Recieved ack: {new_ack} and seq: {new_seq}')

                # si el ack es igual que el menor de todos los que envie
                # solo ahi libero un asiento

                if new_seq == min(sent_chunks.keys()):
                    avalable_seats += 1
                    sent_chunks.pop(min(sent_chunks.keys()))

        # este timeout ocurre cuando dejo de recibir acks
        except TimeoutError:
            logging.debug(' A timeout has occurred, no ack was recieved')
            logging.debug(f' Resending chunks: {sent_chunks}')
            resend_missing_chunks(socket, address, sent_chunks)
            # una vez que reenvie todos los chunks que no recibi respuesta
            # espero un ack
            raw_data, _ = socket.recvfrom(ACK_SEQ_SIZE)
            new_ack, new_seq = AckSeqPackage.unpack_from_server(raw_data)
            logging.debug(f' Recieved ack: {new_ack} and seq: {new_seq}')

            if new_seq == min(sent_chunks.keys()):
                avalable_seats += 1
                sent_chunks.pop(min(sent_chunks.keys()))


if __name__ == '__main__':

    # File System Configuration
    path = os.path.join(uploader_args.FILEPATH, uploader_args.FILENAME)
    try:
        file_handler = FileHandler(open(file=path, mode='rb'))
    except FileNotFoundError:
        logging.debug(f' File {uploader_args.FILENAME} not found')
        exit(1)
    except OSError:
        logging.debug(f' File {uploader_args.FILENAME} could not be opened')
        exit(1)
    except Exception:
        logging.debug(f' File {uploader_args.FILENAME} could not be ' +
                      'opened, generic exception was raised')
        exit(1)

    # Network Configuration
    socket = SocketWrapper()
    socket.bind("", 0)
    socket.set_timeout(SENDING_TIMEOUT)
    handshake_attempts = 0
    arg_addr = (uploader_args.ADDR, uploader_args.PORT)
    address = None
    # El error de la muerte se encuentra por aca, en el Handshake
    while handshake_attempts < MAX_ATTEMPTS:
        try:
            socket.sendto(arg_addr,
                          InitialHandshakePackage.pack_to_send(
                            1,
                            1,
                            file_handler.size(),
                            uploader_args.FILENAME)
                          )
            raw_data, address = socket.recvfrom(ACK_SEQ_SIZE)
            ack, seq = AckSeqPackage.unpack_from_client(raw_data)
            logging.debug(f' Recieved ack: {ack} & seq: {seq} from {address}')
            if seq == ack == 0 and comp_host(address[0], arg_addr[0]):
                break
            else:
                handshake_attempts += 1
        except TimeoutError:
            handshake_attempts += 1
            logging.debug(f' Handshake attempt {handshake_attempts} ' +
                          f'to {arg_addr} failed')

    if handshake_attempts == MAX_ATTEMPTS:
        logging.debug(f' Handshake to {arg_addr} failed')
        exit(1)

    try:
        sw_client_upload(socket, file_handler, address)
        # aca se deberia elegir si sw_upload o sr_upload
    finally:
        socket.close()
        file_handler.close()
