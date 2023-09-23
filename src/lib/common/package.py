import struct
INITIAl_MESSAGE_STRING = "!II?s"

class PackageParser: 

    @staticmethod
    def parse_normal_package(data: bytes):
        package = NormalPackage()
        data_from_package = struct.unpack('!II?255s', data)
        

        return package

#    def parse_handshake_package(data: bytes):



class HandshakePackage:
    
        def __init__(self, ack: int, seq: int, end: bool, data: bytes):
            self.ack = ack
            self.seq = seq
            self.end = end
            self.data = data



class NormalPackage:

    def __init__(self, ack: int, seq: int, end: bool, data: bytes):
        self.ack = ack
        self.seq = seq
        self.end = end
        self.data = data


package = HandshakePackage(2, 3, True, b'hello')
a = struct.pack('!II?6s', package.ack, package.seq, package.end, package.data)
print(a)
print(struct.unpack('!II?6s', a))

# Deberiamos recibir el tamaño del paquetito para saber cuantos bytes leer con el s