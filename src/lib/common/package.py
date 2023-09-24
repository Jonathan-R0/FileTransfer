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


class HandshakePackage:
    
        def __init__(self, is_upload: bool, file_size: int, file_name_size: int, file_name: str):
            self.is_upload = is_upload
            self.file_size = file_size
            self.file_name = file_name
            self.file_name_size = file_name_size


class NormalPackage:

    def __init__(self, ack: int, seq: int, size: int, end: bool, data: bytes):
        self.ack = ack
        self.seq = seq
        self.size = size
        self.end = end
        self.data = data



#packeo un paquete de xS letras
package = NormalPackage(2, 3, 25, True, b'probando probando 123123123123')
a = struct.pack(f'!III?{package.size}s', package.ack, package.seq, package.size, package.end, package.data)

#desempaqueto el header del paquete para obtener el tamaño de la data
header_from_package = struct.unpack('!III?', a[:13])
len_data = header_from_package[2]
print(f"el tamaño de la data es: {len_data}")

#desempaqueto el contenido del paquete
data_from_package = struct.unpack(f'!{len_data}s', a[13:])
print(f"el paquete contiene: {data_from_package[0].decode()}")


