from lib.server_args import server_args
from lib.socket_wrapper import SocketWrapper 

if __name__ == '__main__':
    udp_server = SocketWrapper()
    udp_server.bind("127.0.0.1", 6969) #XDDD

    print("Esperando una conexión UDP desde un solo cliente...")

    message, client_address = udp_server.recvfrom(1024)
    print(f"Conexión establecida desde {client_address}")

    while True:
        print(f"Recibido (UDP) desde {client_address}: {message}")

        response = input("Respuesta: ")
        udp_server.sendto(response, client_address)