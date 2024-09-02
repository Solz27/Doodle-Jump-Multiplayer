import socket
import threading

host_pc = '192.168.1.196'
port = 59215
clients = []
max_clients = 2  # The game starts when exactly 2 clients are connected

# Initial player positions
players = {
    0: {'x': 100, 'y': 300},  # Player 1
    1: {'x': 150, 'y': 300}   # Player 2
}

def handle_client(client_socket, address, player_id):
    global clients, players
    try:
        # Notify other clients of the new connection
        for c in clients:
            c.send(f"CONNECTED:{address[1]}".encode())

        # Send initial position to the connected client
        client_socket.send(f"INIT:{player_id}:{players[player_id]['x']}:{players[player_id]['y']}".encode())

        # Keep the connection open to relay messages between clients
        while True:
            message = client_socket.recv(1024).decode()
            if not message:
                break

            # Parse the message
            if message.startswith("MOVE"):
                _, x, y = message.split(":")
                players[player_id] = {'x': int(x), 'y': int(y)}

                # Broadcast the updated position to other clients
                broadcast(f"UPDATE:{player_id}:{x}:{y}", client_socket)

    except ConnectionResetError:
        pass
    finally:
        # Remove client from the list when they disconnect
        clients.remove(client_socket)
        client_socket.close()
        print(f"Connection closed from {address}")

def broadcast(message, exclude_socket=None):
    for client in clients:
        if client != exclude_socket:
            client.send(message.encode())

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host_pc, port))
    server_socket.listen(max_clients)
    print("Server started, waiting for connections...")

    player_id = 0
    while True:
        if len(clients) < max_clients:
            client_socket, address = server_socket.accept()
            clients.append(client_socket)
            print(f"Connection from {address}")

            client_handler = threading.Thread(target=handle_client, args=(client_socket, address, player_id))
            client_handler.start()

            # Start the game when 2 clients have connected
            if len(clients) == max_clients:
                print("Two clients connected. Starting the game.")
                for c in clients:
                    c.send("START".encode())
                player_id = 1
        else:
            pass

if __name__ == "__main__":
    start_server()
