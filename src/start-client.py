from lib.socket_wrapper import SocketWrapper

if __name__ == "__main__":
    udp_client = SocketWrapper()

    server_address = ("127.0.0.1", 6969)
    udp_client.bind("127.0.0.1", 0)

    print("Conectándose al servidor UDP...")
    udp_client.sendto("¡Hola, servidor!", server_address)

    while True:
        message, server_address = udp_client.recvfrom(1024)
        print(f"Recibido (UDP) desde {server_address}: {message}")

        response = input("Respuesta: ")
        udp_client.sendto(response, server_address)