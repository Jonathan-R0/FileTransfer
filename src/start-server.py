import threading
from lib.socket_wrapper import SocketWrapper

HOST = '127.0.0.1'
PORT = 12345

server_socket = SocketWrapper()
server_socket.bind(HOST, PORT)

print(f"Servidor UDP en {HOST}:{PORT}")

client_sockets = {}

print_lock = threading.Lock() 

def handle_client(client_socket, client_address):
    while True:
        try:
            data, _ = client_socket.recvfrom(1024)
            if not data:
                break

            print(f"Recibido de {client_address}: {data}")

            response = "Mensaje ok!"
            client_socket.sendto(response.encode(), client_address)
        except KeyboardInterrupt:
            print(f"Cliente {client_address} desconectado")
            break

    client_socket.close()
    with print_lock:
        del client_sockets[client_address]

while True:
    try:
        data, client_address = server_socket.recvfrom(1024)
        if not data:
            break

        print(f"Recibido de {client_address}: {data}")

        if client_address not in client_sockets:
            client_socket = SocketWrapper()
            client_sockets[client_address] = client_socket
            threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

        response = "Mensaje ok!"
        client_sockets[client_address].sendto(response.encode(), client_address)
    except KeyboardInterrupt:
        print("Servidor detenido")
        break

server_socket.close()
