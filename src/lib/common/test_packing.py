import struct

from package import NormalPackage

# packeo un paquete de xS letras
package = NormalPackage(2, 3, 10, True, b'probando')
a = struct.pack(f'!III?{package.size}s', package.ack, package.seq,
                package.size, package.end, package.data)

# desempaqueto el header del paquete para obtener el tamaño de la data
header_from_package = struct.unpack('!III?', a[:13])
len_data = header_from_package[2]
print(f"el tamaño de la data es: {len_data}")

# desempaqueto el contenido del paquete
data_from_package = struct.unpack(f'!{len_data}s', a[13:])
print(f"el paquete contiene: {data_from_package[0].decode()}")

# imprimo el tamaño en bytes de a
print(f"el tamaño de a es: {len(a)}")
