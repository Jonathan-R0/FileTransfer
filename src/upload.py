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
    SENDING_TIMEOUT,
    MAX_FILE_SIZE
)
from lib.common.error_codes import handle_error_codes_client
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
    seq = 1
    lost_pkg_attempts = 0
    while not end and lost_pkg_attempts < MAX_ATTEMPTS:
        try:
            chunk, end = file_handler.read_next_chunk(seq)
            if end:
                logging.debug(
                    f' Sending last chunk with size: {len(chunk)}')
            socket.sendto(address, NormalPackage.pack_to_send(seq,
                          chunk, end, 0))
            while True:
                raw_data, _ = socket.recvfrom(ACK_SEQ_SIZE)
                new_seq, _ = AckSeqPackage.unpack_from_server(raw_data)
                logging.debug(f' Recieved ack with seq: {new_seq}')
                if new_seq == seq:
                    lost_pkg_attempts = 0
                    seq += 1
                    break
        except TimeoutError:
            lost_pkg_attempts += 1
            logging.debug(' A timeout has occurred, no ack was recieved')
            end = False
    logging.debug(f' Client {address} ended')


def sr_client_upload(
        socket: SocketWrapper,
        file_handler: FileHandler,
        address: tuple
        ) -> None:
    end = False
    seq = 1
    next_seq_num = 1
    base = 1
    sent_chunks = {}
    attempts = 0
    seq_end = 0
    socket.set_timeout(SENDING_TIMEOUT)
    while attempts <= MAX_ATTEMPTS:
        # Mando paquetes si tengo espacio en la ventana
        while next_seq_num < base + WINDOW_SIZE and not end:
            if (seq_end > 0 and next_seq_num > seq_end):
                break
            chunk, end = file_handler.read_next_chunk(next_seq_num)
            if end:
                seq_end = next_seq_num

            if chunk or end or len(chunk) != 0:
                packet = NormalPackage.pack_to_send(next_seq_num, chunk,
                                                    end, 0)
                socket.sendto(address, packet)
                logging.debug(f' Sent chunk {next_seq_num} with size ' +
                              f'{len(chunk)}')

                # Me guardo el paquete que mande para reenviarlo
                # si es necesario
                sent_chunks[next_seq_num] = chunk
                next_seq_num += 1

        try:
            # Ahora recibo un ACK
            raw_data, _ = socket.recvfrom(ACK_SEQ_SIZE)
            seq, _ = AckSeqPackage.unpack_from_server(raw_data)
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
                    socket.sendto(address, packet)
            else:
                break
    logging.debug(f' Client {address} ended')


if __name__ == '__main__':
    try:
        # File System Configuration
        path = os.path.join(uploader_args.FILEPATH, uploader_args.FILENAME)
        try:
            file_handler = FileHandler(path, True, 'rb')
        except FileNotFoundError:
            logging.debug(f' File {uploader_args.FILENAME} not found')
            exit(1)
        except OSError:
            logging.debug(f' File {uploader_args.FILENAME} could ' +
                          'not be opened')
            exit(1)
        except Exception:
            logging.debug(f' File {uploader_args.FILENAME} could not be ' +
                          'opened, generic exception was raised')
            exit(1)
        if file_handler.size() > MAX_FILE_SIZE:
            logging.debug(f' File {uploader_args.FILENAME} is too big')
            exit(1)

        # Network Configuration
        socket = SocketWrapper()
        socket.bind("", 0)
        socket.set_timeout(SENDING_TIMEOUT)
        handshake_attempts = 0
        arg_addr = (uploader_args.ADDR, uploader_args.PORT)
        address = None
        if uploader_args.selective_repeat:
            mode = 0
        else:
            mode = 1
        while handshake_attempts < MAX_ATTEMPTS:
            try:
                socket.sendto(arg_addr,
                              InitialHandshakePackage.pack_to_send(
                                1,
                                mode,
                                file_handler.size(),
                                uploader_args.FILENAME)
                              )
                raw_data, address = socket.recvfrom(ACK_SEQ_SIZE)
                seq, error = AckSeqPackage.unpack_from_client(raw_data)
                if error != 0:
                    handle_error_codes_client(error)
                    socket.sendto(address,
                                  AckSeqPackage.pack_to_send(0, 0))
                    exit(1)
                logging.debug(f' Recieved ack with seq: {seq} ' +
                              f'from {address}')
                if seq == 0 and comp_host(address[0], arg_addr[0]):
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
            if uploader_args.selective_repeat:
                sr_client_upload(socket, file_handler, address)
            else:
                sw_client_upload(socket, file_handler, address)
        finally:
            socket.close()
            file_handler.close()
    except KeyboardInterrupt:
        logging.debug(' Keyboard Interrupt, ending connection')
        exit(1)
