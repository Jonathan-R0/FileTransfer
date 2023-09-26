from lib.server.server_sw import ServerStopAndWait
from lib.server.server_sr import ServerSelectiveRepeat
from enum import Enum


class ServerTypes(Enum):

    STOPANDWAIT = 1
    SELECTIVEREPEAT = 2

    class ServerTypeNotFound(Exception):
        pass

    def create_server(self, args):
        match self:
            case ServerTypes.STOPANDWAIT:
                return ServerStopAndWait(*args)
            case ServerTypes.SELECTIVEREPEAT:
                return ServerSelectiveRepeat(*args)
            case _:
                raise ServerTypeNotFound(f'Invalid server type: {self}')