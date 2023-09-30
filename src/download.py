from lib.client.download_args import downloader_args
from lib.common.socket_wrapper import SocketWrapper
from lib.common.package import *
import logging
from lib.common.config import *
from lib.client.config import *
from lib.common.file_handler import FileHandler
import os

if downloader_args.verbose:
    logging.basicConfig(level=logging.DEBUG)

def comp_host(host1: str, host2: str) -> bool:
    local_host_addr = {'localhost', '127.0.0.1'}
    return host1 == host2 or (host1 in local_host_addr and host2 in local_host_addr)

def sw_client_download(socket: SocketWrapper, file_handler: FileHandler) -> None:
    end = False
    last_seq = 0
    lost_pkg_attempts = 0

    while not end and lost_pkg_attempts < MAX_ATTEMPTS:
        try:
            raw_data, address = socket.recvfrom(NORMAL_PACKAGE_SIZE)
            ack, seq, end, error, data = struct.unpack(NORMAL_PACKAGE_FORMAT, raw_data)
            logging.debug(f' Recieved package \n{raw_data}\n from: {address} with len {len(raw_data)} and end: {end}')
            if seq == last_seq + 1 and ack == last_seq:
                lost_pkg_attempts = 0
                last_seq = seq
                file_handler.append_chunk(data)
                logging.debug(f' Recieved package from: {address} with seq: {seq} and end: {end}')
                socket.sendto(address, AckSeqPackage.pack_to_send(seq, seq))
            else:
                lost_pkg_attempts += 1
                logging.debug(f' Lost package from: {address} with seq: {seq} and last good seq: {last_seq}')
        except TimeoutError:
            lost_pkg_attempts += 1
            logging.debug(' A timeout has occurred, no package was recieved')

if __name__ == '__main__':

    # File System Configuration
    path = os.path.join(downloader_args.FILEPATH, downloader_args.FILENAME)
    file_handler = FileHandler(open(file=path, mode='wb'))

    # Network Configuration
    socket = SocketWrapper()
    socket.bind("", 0)
    socket.set_timeout(TIMEOUT)
    handshake_attempts = 0
    arg_addr = (downloader_args.ADDR, downloader_args.PORT)
    address = None
    while handshake_attempts < MAX_ATTEMPTS:
        try: 
            socket.sendto(arg_addr, 
                InitialHandshakePackage.pack_to_send(0, 1, 0, downloader_args.FILENAME))
            raw_data, address = socket.recvfrom(ACK_SEQ_SIZE)
            ack, seq = AckSeqPackage.unpack_from_client(raw_data)
            logging.debug(f' Recieved ack: {ack} and seq: {seq} from {address}')
            if seq == ack == 0 and comp_host(address[0], arg_addr[0]):
                break
            else:
                handshake_attempts += 1
        except TimeoutError:
            handshake_attempts += 1
            logging.debug(f' Handshake attempt {handshake_attempts} to {arg_addr} failed')
    
    if handshake_attempts == MAX_ATTEMPTS:
        logging.debug(f' Handshake to {arg_addr} failed')
        exit(1)

    try:
        sw_client_download(socket, file_handler)
        #aca se deberia elegir si sw_download o sr_download
    finally:
        file_handler.close()
        socket.close()
