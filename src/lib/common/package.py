import struct


class InitialHandshakePackage:

    def __init__(self, data: bytes):
        self.is_upload, self.file_size, self.file_name = struct.unpack('!?I255s', data)

    def __init__(self, is_upload: bool, file_size: int, file_name: str):
        self.is_upload = is_upload
        self.file_size = file_size
        self.file_name = file_name

    def pack_data_send(self) -> bytes:
        return struct.pack(f'!?I255s', self.is_upload, self.file_size, self.file_name)

    def pack_initial_handshake_return(self) -> bytes:
        """Returns the handshake package to be sent to the client, also adds the seq number and ack as a zero"""
        return struct.pack(f'!?I255sII', self.is_upload, self.file_size, self.file_name, 0, 0)

class HandshakePackage:

    def __init__(self, is_upload: bool, file_size: int, file_name: str):
        self.is_upload = is_upload
        self.file_size = file_size
        self.file_name = file_name

    def __init__(self, data: InitialHandshakePackage):
        self.is_upload = data.is_upload
        self.file_size = data.file_size
        self.file_name = data.file_name
        

    def pack_handshake_return(self) -> bytes:
        """Returns the handshake package to be sent to the client, also adds the seq number and ack as a zero"""
        return struct.pack('!?I255sII', self.is_upload, self.file_size, self.file_name, 0, 0)

    @staticmethod
    def unpack_handshake_return(self, data: bytes):
        self.is_upload, self.file_size, self.file_name, self.ack, self.seq = struct.unpack('!?I255sII', data)

class AckSeqPackage:

    #def __init__(self, ack: int, seq: int):
    #    self.ack = ack
    #    self.seq = seq

    def __init__(self, data: bytes):
        self.ack, self.seq = struct.unpack('!II', data)

    def pack_ack_seq_package_return(self) -> bytes:
        """Returns the ack_seq package to be sent to the client. Adds +1 to the seq number"""
        return struct.pack('!II', self.ack, self.seq + 1)

class NormalPackage:

    def __init__(self, ack: int, seq: int, end: bool, data: bytes):
        self.ack = ack
        self.seq = seq
        self.end = end
        self.data = data

    def __init__(self, data: bytes):
        self.ack, self.seq, self.end, self.data = struct.unpack('!II?251s', data)

    def pack_normal_package_return(self) -> bytes:
        """Returns the normal package to be sent to the client. Adds +1 to the seq number"""
        return struct.pack(f'!III?{self.size}s', self.ack, self.seq + 1, self.size, self.end, self.data)
