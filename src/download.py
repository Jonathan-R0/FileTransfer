from lib.client.download_args import downloader_args
from lib.common.socket_wrapper import SocketWrapper
from lib.common.package import *
import logging
from lib.common.config import *

if __name__ == '__main__':
    print(downloader_args)
    file = []
    socket = SocketWrapper()
    host = '127.0.0.1'
    address = (host, 8080)
    socket.bind(host, 8081)
    socket.sendto(address, InitialHandshakePackage.pack_to_send(0, 1, 0, b'dataxd'))
    print(f' Replying to handshake from: {address}')
    raw_data, _ = socket.recvfrom(ACK_SEQ_SIZE)
    end = False
    while not end:
        raw_data, address = socket.recvfrom(NORMAL_PACKAGE_SIZE)
        print(f' Recieved package \n{raw_data.decode()}\n from: {address} with len {len(raw_data)}')
        ack, seq, end, error, data = struct.unpack(NORMAL_PACKAGE_FORMAT, raw_data)
        file.append(data)
        print(f' Recieved package from: {address} with seq: {seq} and end: {end}')
        socket.sendto(address, AckSeqPackage.pack_to_send(seq, seq))
