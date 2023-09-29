import struct
from typing import Any


class InitialHandshakePackage:

    def __init__(self, data: bytes):
        self.is_upload, self.is_saw, self.file_size, self.file_name = self.unpack_from_client(data)

    @staticmethod
    def unpack_from_client(data: bytes) -> tuple[Any, ...]:
        return struct.unpack('!??I256s', data)

    @staticmethod
    def pack_to_send(is_upload: bool, is_saw: bool,  file_size: int, file_name: str | bytes) -> bytes:
        if isinstance(file_name, str):
            file_name = file_name.encode()
        return struct.pack(f'!??I256s', is_upload, is_saw, file_size, file_name)


class AckSeqPackage:

    @staticmethod
    def unpack_from_server(data: bytes) -> tuple[Any, ...]:
        return struct.unpack('!II', data)

    @staticmethod
    def unpack_from_client(data: bytes) -> tuple[Any, ...]:
        return AckSeqPackage.unpack_from_server(data)

    @staticmethod
    def pack_to_send(ack: int, seq: int) -> str:
        return struct.pack('!II', ack, seq).decode()


class NormalPackage:

    @staticmethod
    def pack_to_send(ack: int, seq: int, data: bytes, end: bool, error: int) -> bytes:
        return struct.pack('!II?I256s', ack, seq, end, error, data)

    @staticmethod
    def unpack_from_client(data: bytes) -> tuple[Any, ...]:
        return struct.unpack('!II?I256s', data)
