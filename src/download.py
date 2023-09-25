from src.lib.client.download_args import downloader_args
from src.lib.common.socket_wrapper import SocketWrapper
from src.lib.common.package import *
import logging

if __name__ == '__main__':
    socket = SocketWrapper()
    socket.bind(downloader_args.host, downloader_args.port)
    initial_package = InitialHandshakePackage(True, 20, 'tuvie')
    sendable_initial_package = initial_package.pack_initial_handshake_return()
    socket.sendto((downloader_args.host, downloader_args.port), sendable_initial_package)
    logging.debug(f' [CLIENTXD] Sent initial package: {sendable_initial_package}')
    data, address = socket.recvfrom(HANDSHAKE_PACKAGE_SIZE)
    logging.debug(f' [CLIENTXD] Received data from {address}: {data}')
    is_upload, file_size, file_name, ack, seq = struct.unpack('!?I255sII', data)
    logging.debug(f' [CLIENTXD] Received is_upload: {is_upload}, file_size: {file_size}, file_name: {file_name}, ack: {ack}, seq: {seq}')
    ack_seq_package = AckSeqPackage(2, 3)
    socket.sendto((downloader_args.host, downloader_args.port), ack_seq_package.pack_ack_seq_package_return())
    logging.debug(f' [CLIENTXD] Sent ack_seq_package: {ack_seq_package.pack_ack_seq_package_return()}')