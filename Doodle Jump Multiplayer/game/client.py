import pygame
import socket
import threading

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FONT_SIZE = 24
FONT_COLOR = (0, 0, 0)

# Player size and initial position
PLAYER_WIDTH = 55
PLAYER_HEIGHT = 55
PLAYER_START_X = WINDOW_WIDTH // 2 - PLAYER_WIDTH // 2
PLAYER_START_Y = WINDOW_HEIGHT - PLAYER_HEIGHT - 10

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.font.init()
font = pygame.font.SysFont(None, FONT_SIZE)

# Define player rectangle
player_rect = pygame.Rect(PLAYER_START_X, PLAYER_START_Y, PLAYER_WIDTH, PLAYER_HEIGHT)

def draw_text(text, x, y):
    surface = font.render(text, True, FONT_COLOR)
    rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)

def receive_messages(sock):
    global messages, game_started, player_rect
    while True:
        try:
            message = sock.recv(1024).decode()
            if message.startswith("CONNECTED:"):
                messages.append(f"Connected to: {message.split(':')[1]}")
            elif message == "START":
                game_started = True
                break
            else:
                # Handle player position updates
                if message.startswith("POS:"):
                    pos_data = message.split(":")[1]
                    x, y = map(int, pos_data.split(","))
                    player_rect.x = x
                    player_rect.y = y
                else:
                    messages.append(message)
        except ConnectionResetError:
            break

def start_client():
    global messages, game_started
    messages = []
    game_started = False
    server_ip = '192.168.1.196'  # Localhost for local testing
    server_port = 59215       # Match this with the server port

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    # Start receiving messages
    receiver_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receiver_thread.start()

    # Lobby loop
    running = True
    while running and not game_started:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                client_socket.close()

        screen.fill((0, 255, 0))  # Green background
        draw_text("Game Lobby", WINDOW_WIDTH // 2, 50)

        y = 100
        for message in messages:
            draw_text(message, WINDOW_WIDTH // 2, y)
            y += 30

        pygame.display.flip()

    if game_started:
        # Start the main game in a new Pygame window
        client_socket.close()
        return True  # Signal to start the game

    pygame.quit()
    return False  # Signal to not start the game

if __name__ == "__main__":
    if start_client():
        import main  # Import and run your main game
