from lib.client.download_args import downloader_args
from lib.common.socket_wrapper import SocketWrapper
from lib.common.package import *
import logging
from lib.common.config import *

if __name__ == '__main__':
    print(downloader_args)
    socket = SocketWrapper()
    #socket.bind(downloader_args.host, downloader_args.port)
    host = '127.0.0.1'
    address = (host, 8080)
    socket.bind(host, 8081)
    data = struct.pack('!?I255s', True, 20, b'tuvie')
    initial_package = InitialHandshakePackage(data)
    sendable_initial_package = initial_package.pack_initial_handshake_return()
    #socket.sendto((downloader_args.host, downloader_args.port), sendable_initial_package)
    socket.sendto(address, sendable_initial_package)
    print(f' [CLIENTXD] Sent initial package: {sendable_initial_package}')
    data, address = socket.recvfrom(HANDSHAKE_PACKAGE_SIZE)
    print(f' [CLIENTXD] Received data from {address}: {data}')
    is_upload, file_size, file_name, ack, seq = struct.unpack('!?I255sII', data)
    print(f' [CLIENTXD] Received is_upload: {is_upload}, file_size: {file_size}, file_name: {file_name.decode()}, ack: {ack}, seq: {seq}')
    ack_data = struct.pack('!II', 2, 3)
    ack_seq_package = AckSeqPackage(ack_data)
    socket.sendto(address, ack_seq_package.pack_ack_seq_package_return())
    print(f' [CLIENTXD] Sent ack_seq_package: {ack_seq_package.pack_ack_seq_package_return()}')