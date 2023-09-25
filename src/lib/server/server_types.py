from lib.server.server_sw import ServerStopAndWait
from enum import Enum


class ServerTypes(Enum):

    STOPANDWAIT = 1

    def create_server(self, args):
        if self == ServerTypes.STOPANDWAIT:
            return ServerStopAndWait(*args)
        else:
            raise Exception('Invalid server type')
