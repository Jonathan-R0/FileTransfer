import struct
from typing import Any
from lib.common.config import (
    INITIAL_MESSAGE_FORMAT,
    ACK_SEQ_FORMAT,
    NORMAL_PACKAGE_FORMAT,
)
from hashlib import md5


class InitialHandshakePackage:

    def __init__(self, data: bytes):
        self.is_upload, self.is_saw, self.file_size, self.file_name = \
            self.unpack_from_client(data)

    @staticmethod
    def unpack_from_client(data: bytes) -> tuple[Any, ...]:
        return struct.unpack(INITIAL_MESSAGE_FORMAT, data)

    @staticmethod
    def pack_to_send(is_upload: bool, is_saw: bool,
                     file_size: int, file_name: str | bytes) -> bytes:
        if isinstance(file_name, str):
            file_name = file_name.encode()
        return struct.pack(
            INITIAL_MESSAGE_FORMAT,
            is_upload, is_saw, file_size, file_name
        )


class AckSeqPackage:

    @staticmethod
    def unpack_from_server(data: bytes) -> tuple[Any, ...]:
        return struct.unpack(ACK_SEQ_FORMAT, data)

    @staticmethod
    def unpack_from_client(data: bytes) -> int:
        return AckSeqPackage.unpack_from_server(data)

    @staticmethod
    def pack_to_send(seq: int, error: int) -> bytes:
        return struct.pack(ACK_SEQ_FORMAT, seq, error)


class NormalPackage:

    @staticmethod
    def pack_to_send(seq: int, data: bytes,
                     end: bool, error: int) -> bytes:
        checksum = md5(struct.pack('!256s', data)).digest()
        return struct.pack(NORMAL_PACKAGE_FORMAT, seq, end, error,
                           checksum, data)

    @staticmethod
    def unpack_from_client(data: bytes) -> tuple[Any, ...]:
        return struct.unpack(NORMAL_PACKAGE_FORMAT, data)
