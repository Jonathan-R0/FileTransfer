from lib.client.download_args import downloader_args
from lib.common.socket_wrapper import SocketWrapper

from lib.common.package import (
    InitialHandshakePackage,
    AckSeqPackage,
    NormalPackage,
)
import logging
from lib.common.config import (
    NORMAL_PACKAGE_SIZE,
    RECEPTION_TIMEOUT,
    WINDOW_SIZE,
    MAX_ATTEMPTS
)
from lib.common.file_handler import FileHandler
import os
from hashlib import md5
from lib.common.error_codes import handle_error_codes_client
import struct

if downloader_args.verbose:
    logging.basicConfig(level=logging.DEBUG)


def comp_host(host1: str, host2: str) -> bool:
    local_host_addr = {'localhost', '127.0.0.1'}
    return host1 == host2 or\
        (host1 in local_host_addr and host2 in local_host_addr)


def sw_client_download(
        socket: SocketWrapper,
        file_handler: FileHandler,
        raw_data: bytes,
        address: tuple
        ) -> None:
    end = False
    last_seq = 0
    while True:
        try:
            if last_seq > 0:
                raw_data, address = socket.recvfrom(NORMAL_PACKAGE_SIZE)
            seq, end, error, checksum, data = \
                NormalPackage.unpack_from_client(raw_data)
            if any(data) and checksum != md5(struct.pack('!256s', data)).digest():
                logging.debug(' Checksum error for package ' +
                              f'with seq: {seq}. Ignoring...')
                continue
            if error != 0:
                handle_error_codes_client(error)
                break
            if seq == last_seq + 1:
                last_seq = seq
                file_handler.append_chunk(data, end)
                logging.debug(f' Recieved package from: {address} with ' +
                              f'seq: {seq} and end: {end}')
                socket.sendto(address, AckSeqPackage.pack_to_send(seq))
            else:
                logging.debug(
                    f' Recieved package from: {address} with seq: ' +
                    f'{seq} and end: {end} but missed previous package'
                )
                socket.sendto(
                    address,
                    AckSeqPackage.pack_to_send(last_seq)
                )
        except TimeoutError:
            if not end:
                logging.debug(' A timeout has occurred, ' +
                              'ending connection and deleting corrupted file')
                file_handler.rollback_write()
            break


def sr_client_download(socket: SocketWrapper,
                       file_handler: FileHandler,
                       raw_data: bytes,
                        address: tuple) -> None:
    end = False
    received_chunks = {}
    base = 1
    has_end_pkg = False
    seq_end = 0
    first_iteration = True
    while True:
        try:
            # Recibo el paquete
            if first_iteration:
                first_iteration = False
            else:
                raw_data, address = socket.recvfrom(NORMAL_PACKAGE_SIZE)
            seq, end, error, checksum, data = \
                NormalPackage.unpack_from_client(raw_data)
            if error != 0:
                handle_error_codes_client(error)
                break
            if any(data) and checksum != md5(struct.pack('!256s', data)).digest():
                logging.debug(' Checksum error for package ' +
                              f'with seq: {seq}. Ignoring...')
                continue
            if end:
                has_end_pkg = True
                seq_end = seq
            logging.debug(f' Received package from: {address} with seq:' +
                          f' {seq} and end: {end} with len {len(data)}')

            # Si no tenia el paquete que me mandaron y esta
            # dentro de la ventana, lo guardo y mando confirmacion
            if seq not in received_chunks and base <= seq < base + WINDOW_SIZE:
                received_chunks[seq] = data
                socket.sendto(address,
                              AckSeqPackage.pack_to_send(seq))
                logging.debug(f' Sending ack for seq: {seq}')
            elif seq in received_chunks:
                # Si ya tenia el paquete, mando confirmacion de nuevo
                socket.sendto(address,
                              AckSeqPackage.pack_to_send(seq))
                logging.debug(f' Sending ack for seq: {seq}')
            elif seq < base:
                socket.sendto(address, AckSeqPackage.pack_to_send(seq))
                logging.debug(f' Sending ack for seq: {seq}')
            # Chequeo si el paquete esta en sequencia
            # y lo agrego al archivo
            while base in received_chunks:
                received_chunk = received_chunks[base]
                del received_chunks[base]
                file_handler.append_chunk(received_chunk, seq_end == base)
                base += 1
        except TimeoutError:
            if len(received_chunks) != 0 or \
                       (not has_end_pkg and len(received_chunks) == 0):
                logging.debug(' A timeout has occurred, ' +
                              'ending connection and deleting corrupted file')
                file_handler.rollback_write()
            break
    if address:
        logging.debug(f' Client {address} ended')


def handshake(
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


if __name__ == '__main__':
    try:
        # File System Configuration
        path = os.path.join(downloader_args.FILEPATH, downloader_args.FILENAME)
        try:
            file_handler = FileHandler(path, False, 'wb')
        except FileNotFoundError:
            logging.debug(f' File {downloader_args.FILENAME} not found')
            exit(1)
        except OSError:
            logging.debug(f' File {downloader_args.FILENAME} could ' +
                          ' not be opened')
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
        raw_data, address = handshake(socket, arg_addr,
                                             handshake_attempts)

        try: 
            if downloader_args.stop_and_wait:
                sw_client_download(socket, file_handler, raw_data, address)
            else:
                sr_client_download(socket, file_handler, raw_data, address)
        finally:
            file_handler.close()
            socket.close()
    except KeyboardInterrupt:
        logging.debug(' Keyboard Interrupt, ending connection')
        exit(1)
