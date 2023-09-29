from lib.client.download_args import downloader_args
from lib.common.socket_wrapper import SocketWrapper
from lib.common.package import *
import logging
from lib.common.config import *
from lib.common.file_handler import FileHandler
import os

if uploader_args.verbose:
    logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    print(downloader_args)

    # File System Configuration
    path = os.path.join(downloader_args.FILEPATH, downloader_args.FILENAME)
    file_handler = FileHandler(open(file=path, mode='ab'))

    # Network Configuration
    socket = SocketWrapper()
    socket.bind("", 0)
    socket.sendto((downloader_args.ADDR, downloader_args.PORT), 
        InitialHandshakePackage.pack_to_send(0, 1, 0, downloader_args.FILENAME))
    raw_data, addr = socket.recvfrom(ACK_SEQ_SIZE)
    print(f' Replying to handshake from: {addr}')

    end = False

    while not end:
        raw_data, address = socket.recvfrom(NORMAL_PACKAGE_SIZE)
        print(f' Recieved package \n{raw_data.decode()}\n from: {address} with len {len(raw_data)}')
        ack, seq, end, error, data = struct.unpack(NORMAL_PACKAGE_FORMAT, raw_data)
        file_handler.append_chunk(data)
        print(f' Recieved package from: {address} with seq: {seq} and end: {end}')
        socket.sendto(address, AckSeqPackage.pack_to_send(seq, seq))
    file_handler.close()
