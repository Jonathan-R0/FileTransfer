import struct

class PackageParser: 

    @staticmethod
    def parse_normal_package(data: bytes):
        header_from_package = struct.unpack('!III?', data[:13])
        data_from_package = struct.unpack(f'!{package.size}s', data[13:])
        package = NormalPackage(header_from_package[0], header_from_package[1], header_from_package[2], header_from_package[3], data_from_package)
        return package

    @staticmethod
    def parse_handshake_package(data: bytes):
        package_data = struct.unpack('!?II', data[:9])
        file_name = struct.unpack(f'!{package_data[2]}s', data[9:])
        package = HandshakePackage(package_data[0], package_data[1], package_data[2], file_name[0].decode())
        return package

    def pack_handshake_return(self, package) -> bytes:
        package = HandshakePackage(package.is_upload, package.file_size, package.file_name_size, package.file_name)
        return package.pack_handshake_return()

    def pack_normal_package_return(self, package) -> bytes:
        package = NormalPackage(package.ack, package.seq, package.size, package.end, package.data)
        return package.pack_normal_package_return()

class HandshakePackage:
    
        def __init__(self, is_upload: bool, file_size: int, file_name_size: int, file_name: str):
            self.is_upload = is_upload
            self.file_size = file_size
            self.file_name = file_name
            self.file_name_size = file_name_size

        def pack_handshake_return(self) -> bytes:
            '''Returns the handshake package to be sent to the client, also adds the seq number as a zero'''
            return struct.pack(f'!?II{self.file_name_size}sI', self.is_upload, self.file_size, self.file_name_size, self.file_name.encode(), 0)



class NormalPackage:

    def __init__(self, ack: int, seq: int, size: int, end: bool, data: bytes):
        self.ack = ack
        self.seq = seq
        self.size = size
        self.end = end
        self.data = data

    def pack_normal_package_return(self) -> bytes:
        '''Returns the normal package to be sent to the client. Adds +1 to the seq number'''
        return struct.pack(f'!III?{self.size}s', self.ack, self.seq + 1, self.size, self.end, self.data)
