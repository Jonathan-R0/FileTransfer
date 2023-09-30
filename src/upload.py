from lib.client.upload import Upload
from lib.client.upload_args import uploader_args
from lib.common.socket_wrapper import SocketWrapper
from lib.common.package import *
from lib.common.file_handler import FileHandler
from lib.common.config import *
from lib.client.config import *
import logging
import os

if uploader_args.verbose:
    logging.basicConfig(level=logging.DEBUG)

def comp_host(host1: str, host2: str) -> bool:
    local_host_addr = {'localhost', '127.0.0.1'}
    return host1 == host2 or (host1 in local_host_addr and host2 in local_host_addr)

def sw_client_upload(socket: SocketWrapper, file_handler: FileHandler, address: tuple) -> None:
    end = False
    ack = 0
    seq = 1
    lost_pkg_attempts = 0
    while not end and lost_pkg_attempts < MAX_ATTEMPTS:
        chunk, end = file_handler.read_next_chunk(seq)
        if end or len(chunk) == 0:
            logging.debug(f' Sending last chunk: {chunk} with size: {len(chunk)}')
        socket.sendto(address, NormalPackage.pack_to_send(ack, seq, chunk, end, 0))
        raw_data, _ = socket.recvfrom(ACK_SEQ_SIZE)
        new_ack, new_seq = AckSeqPackage.unpack_from_server(raw_data)
        logging.debug(f' Recieved ack: {new_ack} and seq: {new_seq}')
        if new_seq == seq == new_ack:
            lost_pkg_attempts = 0
            seq += 1
            ack += 1
        else:
            lost_pkg_attempts += 1
    socket.close()
    file_handler.close()
    logging.debug(f' Client {address} ended')

if __name__ == '__main__':

    # File System Configuration
    path = os.path.join(uploader_args.FILEPATH, uploader_args.FILENAME)
    file_handler = FileHandler(open(file=path, mode='rb'))

    # Network Configuration
    socket = SocketWrapper()
    socket.bind("", 0)
    socket.set_timeout(TIMEOUT)
    handshake_attempts = 0
    arg_addr = (uploader_args.ADDR, uploader_args.PORT)
    address = None
    while handshake_attempts < MAX_ATTEMPTS:
        try: 
            socket.sendto(arg_addr, 
                InitialHandshakePackage.pack_to_send(1, 1, file_handler.size(), uploader_args.FILENAME))
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

    sw_client_upload(socket, file_handler, address)
    
    #aca se deberia elegir si sw_upload o sr_upload