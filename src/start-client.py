from lib.socket_wrapper import SocketWrapper

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345

client_socket = SocketWrapper()

while True:
    try:
        message = input("Escribe un mensaje para el servidor: ")
        if message.lower() == 'exit':
            break
        client_socket.sendto(message, (SERVER_HOST, SERVER_PORT))

        response, server_address = client_socket.recvfrom(1024)
        print(f"Respuesta del servidor: {response}")

    except KeyboardInterrupt:
        print("Cliente detenido")
        break

client_socket.close()
