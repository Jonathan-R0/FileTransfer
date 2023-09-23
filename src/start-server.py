import threading
from lib.socket_wrapper import SocketWrapper
from lib.server.server import Server
from lib.server.server_args import server_args
import logging

if server_args.verbose:
    logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    logging.debug(' Starting server...')
    server = Server(server_args.ADDR, server_args.PORT, server_args.DIRPATH)
    