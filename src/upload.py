from lib.client.upload_args import uploader_args
from lib.common.socket_wrapper import SocketWrapper
from lib.common.package import *
from lib.common.file_handler import FileHandler
from lib.common.config import *
import logging
import os

if __name__ == '__main__':
    # File System Configuration
    path = os.path.join(uploader_args.FILEPATH, uploader_args.FILENAME)
    file_handler = FileHandler(open(file=path, mode='rb'))

    # Network Configuration
    socket = SocketWrapper()
    socket.bind("", 0)
    address = (uploader_args.ADDR, uploader_args.PORT)
    socket.sendto(address, 
        InitialHandshakePackage.pack_to_send(1, 1, file_handler.size(), uploader_args.FILENAME))
    raw_data, addr = socket.recvfrom(ACK_SEQ_SIZE)
    print(f' Replying to handshake from: {addr}')

    end = False
    ack = 0
    seq = 1
    address = addr #aca cambie el address por el que tiene el server que le responde (socket?)
    while not end:
        chunk, end = file_handler.read_next_chunk(seq)
        if end or len(chunk) == 0:
            logging.debug(f' Sending last chunk: {chunk} with size: {len(chunk)}')
        if len(chunk) == 0:
            break
        socket.sendto(address, NormalPackage.pack_to_send(ack, seq, chunk, end, 0))
        raw_data, _ = socket.recvfrom(ACK_SEQ_SIZE)
        new_ack, new_seq = AckSeqPackage.unpack_from_server(raw_data)
        logging.debug(f' Recieved ack: {new_ack} and seq: {new_seq}')
        if new_seq == seq == new_ack:
            seq += 1
            ack += 1
        else:
            pass # TODO handle late or lost package
    socket.close()
    file_handler.close()
    logging.debug(f' Client {address} ended')
        