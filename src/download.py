from lib.client.download_args import downloader_args
from lib.common.socket_wrapper import SocketWrapper

from lib.common.package import (
    InitialHandshakePackage,
    AckSeqPackage,
)
import logging
from lib.common.config import (
    NORMAL_PACKAGE_SIZE,
    NORMAL_PACKAGE_FORMAT,
    RECEPTION_TIMEOUT,
    WINDOW_SIZE,
    ACK_SEQ_SIZE,
    MAX_ATTEMPTS
)
from lib.common.file_handler import FileHandler
import os
import struct

if downloader_args.verbose:
    logging.basicConfig(level=logging.DEBUG)


def comp_host(host1: str, host2: str) -> bool:
    local_host_addr = {'localhost', '127.0.0.1'}
    return host1 == host2 or\
        (host1 in local_host_addr and host2 in local_host_addr)


def sr_client_download(socket: SocketWrapper,
                       file_handler: FileHandler) -> None:
    end = False
    received_chunks = {}
    base = 1
    attempts = 0
    socket.set_timeout(RECEPTION_TIMEOUT)
    while not end and attempts <= MAX_ATTEMPTS:
        try:
            # Recibo el paquete
            raw_data, address = socket.recvfrom(NORMAL_PACKAGE_SIZE)
            _, seq, end, error, data = struct.unpack(NORMAL_PACKAGE_FORMAT,
                                                     raw_data)
            logging.debug(f'Received package from: {address} with seq:' +
                          f' {seq} and end: {end} with len {len(data)}')

            # Si no tenia el paquete que me mandaron y esta
            # dentro de la ventana, lo guardo y mando confirmacion
            if seq not in received_chunks and base <= seq < base + WINDOW_SIZE:
                received_chunks[seq] = data
                socket.sendto(address,
                              AckSeqPackage.pack_to_send(seq, seq))
                logging.debug(f'Sending ack for seq: {seq}')
            elif seq in received_chunks:
                # Si ya tenia el paquete, mando confirmacion de nuevo
                socket.sendto(address,
                              AckSeqPackage.pack_to_send(seq, seq))
                logging.debug(f'Sending ack for seq: {seq}')
            # Chequeo si el paquete esta en sequencia
            # y lo agrego al archivo
            while base in received_chunks:
                received_chunk = received_chunks.pop(base)
                file_handler.append_chunk(received_chunk)
                base += 1
                attempts = 0
            # Si recibi el ultimo paquete, termino al toque roque
            if end:
                break
        except TimeoutError:
            if attempts == MAX_ATTEMPTS:
                logging.debug(' A timeout has occurred, ' +
                              'ending connection')
                break
            attempts += 1
            continue


def sw_client_download(
        socket: SocketWrapper,
        file_handler: FileHandler,
        raw_data: bytes,
        address: tuple
        ) -> None:
    end = False
    last_seq = 0
    socket.set_timeout(RECEPTION_TIMEOUT)
    while not end:
        try:
            if last_seq > 0:
                raw_data, address = socket.recvfrom(NORMAL_PACKAGE_SIZE)
            ack, seq, end, error, data = struct.unpack(
                NORMAL_PACKAGE_FORMAT,
                raw_data
            )
            if error != 0:
                break
            logging.debug(f' Recieved package \n{raw_data}\n from: ' +
                          f'{address} with len {len(raw_data)} and end: {end}')
            if seq == last_seq + 1 and ack == last_seq:
                last_seq = seq
                file_handler.append_chunk(data)
                logging.debug(f' Recieved package from: {address} with ' +
                              f'seq: {seq} and end: {end}')
                socket.sendto(address, AckSeqPackage.pack_to_send(seq, seq))
            else:
                logging.debug(
                    f' Recieved package from: {address} with seq: ' +
                    f'{seq} and end: {end} but missed previous package'
                )
                socket.sendto(
                    address,
                    AckSeqPackage.pack_to_send(last_seq, last_seq)
                )
        except TimeoutError:
            logging.debug(' A timeout has occurred, ' +
                            'ending connection and deleting corrupted file')
            file_handler.rollback_write()


def handshake_sw(
        socket: SocketWrapper,
        arg_addr: tuple,
        handshake_attempts: int
        ) -> tuple[bytes, ...]:
    while handshake_attempts < MAX_ATTEMPTS:
        try:
            socket.sendto(arg_addr,
                          InitialHandshakePackage.pack_to_send(
                            0,
                            1,
                            0,
                            downloader_args.FILENAME)
                          )
            raw_data, address = socket.recvfrom(NORMAL_PACKAGE_SIZE)
            if comp_host(address[0], arg_addr[0]):
                break
        except TimeoutError:
            handshake_attempts += 1
            logging.debug(f' Handshake attempt {handshake_attempts} ' +
                          f'to {arg_addr} failed')
    if handshake_attempts == MAX_ATTEMPTS:
        logging.debug(f' Handshake to {arg_addr} failed')
        exit(1)
    return raw_data, address


def handshake_sr(
        socket: SocketWrapper,
        arg_addr: tuple,
        handshake_attempts: int
        ) -> None:
    while handshake_attempts < MAX_ATTEMPTS:
        try:
            socket.sendto(arg_addr,
                          InitialHandshakePackage.pack_to_send(
                            0,
                            0,
                            0,
                            downloader_args.FILENAME)
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


if __name__ == '__main__':

    # File System Configuration
    path = os.path.join(downloader_args.FILEPATH, downloader_args.FILENAME)
    try:
        file_handler = FileHandler(open(file=path, mode='wb'))
    except FileNotFoundError:
        logging.debug(f' File {downloader_args.FILENAME} not found')
        exit(1)
    except OSError:
        logging.debug(f' File {downloader_args.FILENAME} could not be opened')
        exit(1)
    except Exception:
        logging.debug(f' File {downloader_args.FILENAME} could not be ' +
                      'opened, generic exception was raised')
        exit(1)

    # Network Configuration
    socket = SocketWrapper()
    socket.bind("", 0)
    socket.set_timeout(RECEPTION_TIMEOUT)
    handshake_attempts = 0
    arg_addr = (downloader_args.ADDR, downloader_args.PORT)
    address = None
    if downloader_args.selective_repeat:
        handshake_sr(socket, arg_addr, handshake_attempts)
    else:
        raw_data, address = handshake_sw(socket, arg_addr, handshake_attempts)

    try:
        # TODO: si el sw no se ingresa, entrar por defecto al sw (o al
        # sr depende de lo que se quiera)
        if downloader_args.stop_and_wait:
            sw_client_download(socket, file_handler, raw_data, address)
        else:
            sr_client_download(socket, file_handler)
    finally:
        file_handler.close()
        socket.close()
