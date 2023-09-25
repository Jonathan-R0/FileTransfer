import struct


class InitialHandshakePackage:

    def __init__(self, is_upload: bool, file_size: int, file_name: str):
        self.is_upload = is_upload
        self.file_size = file_size
        self.file_name = file_name

    def pack_initial_handshake_return(self) -> bytes:
        """Returns the handshake package to be sent to the client, also adds the seq number and ack as a zero"""
        return struct.pack(f'!?I{len(self.file_name)}sII', self.is_upload, self.file_size, self.file_name.encode())

class HandshakePackage:

    def __init__(self, is_upload: bool, file_size: int, file_name: str):
        self.is_upload = is_upload
        self.file_size = file_size
        self.file_name = file_name

    def pack_handshake_return(self) -> bytes:
        """Returns the handshake package to be sent to the client, also adds the seq number and ack as a zero"""
        return struct.pack(f'!?I{len(self.file_name)}sII', self.is_upload, self.file_size, self.file_name.encode(), 0, 0)

class EndHandshakePackage:

    def __init__(self, ack: int, seq: int):
        self.ack = ack
        self.seq = seq

    def pack_end_handshake_return(self) -> bytes:
        """Returns the handshake package to be sent to the client, also adds the seq number and ack as a zero"""
        return struct.pack(f'!II', self.ack, self.seq)

class NormalPackage:

    def __init__(self, ack: int, seq: int, size: int, end: bool, data: bytes):
        self.ack = ack
        self.seq = seq
        self.size = size
        self.end = end
        self.data = data

    def pack_normal_package_return(self) -> bytes:
        """Returns the normal package to be sent to the client. Adds +1 to the seq number"""
        return struct.pack(f'!III?{self.size}s', self.ack, self.seq + 1, self.size, self.end, self.data)
