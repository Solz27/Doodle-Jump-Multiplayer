import pygame
import random

def create_window(width, height):
    win = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    win.fill((0, 255, 255))  # Cyan background
    pygame.display.set_caption("Doodle Jump")
    return win

def draw_player(win, player_rect):
    pygame.draw.rect(win, (0, 255, 0), player_rect)  # Green player square

def draw_platforms(win, platforms):
    for platform in platforms:
        pygame.draw.rect(win, platform.color, platform.rect)  # Draw platform with its color

def generate_platforms(grid_width, grid_height, cell_size, platform_width, platform_height, num_platforms, y_offset=0):
    platforms = []
    available_x_positions = list(range(0, grid_width, cell_size * 15))  # Ensure horizontal spacing
    random.shuffle(available_x_positions)  # Shuffle to randomize

    y = y_offset
    while y < grid_height + y_offset and len(platforms) < num_platforms:
        for x in available_x_positions:
            if len(platforms) >= num_platforms:
                break
            if random.random() < 0.5:  # 50% chance to place a platform
                if random.random() < 0.2:  # 20% chance to place a moving platform
                    platform = MovingPlatform(
                        pygame.Rect(
                            x + random.randint(0, cell_size * 9),
                            y + random.randint(0, cell_size * 2),
                            platform_width,
                            platform_height
                        )
                    )
                else:
                    platform = Platform(
                        pygame.Rect(
                            x + random.randint(0, cell_size * 9),
                            y + random.randint(0, cell_size * 2),
                            platform_width,
                            platform_height
                        )
                    )
                platforms.append(platform)
        y += cell_size * 3  # Ensure vertical spacing
    return platforms

class Platform:
    def __init__(self, rect):
        self.rect = rect
        self.color = (255, 0, 0)  # Red color for static platforms

class MovingPlatform:
    def __init__(self, rect):
        self.rect = rect
        self.color = (255, 255, 0)  # Yellow color for moving platforms
        self.direction = random.choice([-1, 1])  # Random initial direction
        self.speed = 2  # Speed of movement

    def update(self, width):
        # Move platform horizontally
        self.rect.x += self.direction * self.speed
        # Reverse direction if hitting window edges
        if self.rect.left <= 0 or self.rect.right >= width:
            self.direction *= -1

pygame.init()
width, height = 250, 450
cell_size = 10
platform_width, platform_height = 35, 5
initial_platform_count = 30 
gap = 50  # Minimum gap to trigger new platform generation
window = create_window(width, height)

# Initialize player properties
player_size = 15
player_x = width // 2 - player_size // 2

def place_player_on_platform(platforms, player_rect):
    for platform in platforms:
        if platform.rect.y < height and platform.rect.x <= player_rect.x <= platform.rect.x + platform_width:
            return platform.rect.y - player_size
    return height - player_size

# Generate initial platforms
platforms = generate_platforms(width, height, cell_size, platform_width, platform_height, initial_platform_count)

# Set initial player position on a platform
player_y = place_player_on_platform(platforms, pygame.Rect(player_x, 0, player_size, player_size))
player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
player_dy = 0.0

# Bounce parameters
gravity = 0.1
jump_strength = 15.0

clock = pygame.time.Clock()
# Event loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.VIDEORESIZE:
            width, height = event.size
            window = create_window(width, height)
            platforms = generate_platforms(width, height, cell_size, platform_width, platform_height, initial_platform_count)

            # Set initial player position on a platform
            player_y = place_player_on_platform(platforms, pygame.Rect(player_x, 0, player_size, player_size))
            player_rect.y = player_y

        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= 5
        if player_x < -player_size:
            player_x = width
    if keys[pygame.K_RIGHT]:
        player_x += 5
        if player_x > width:
            player_x = -player_size

    player_dy += gravity
    player_y += player_dy

    # Check collision with platforms
    for platform in platforms:
        if isinstance(platform, MovingPlatform):
            platform.update(width)  # Update moving platforms

        if player_rect.colliderect(platform.rect) and player_dy > 0:
            player_y = platform.rect.y - player_size
            player_dy = -jump_strength

    # Scroll the view downward when player reaches halfway
    if player_y < height // 4:
        scroll_amount = height // 4 - player_y
        player_y = height // 4
        for platform in platforms:
            platform.rect.y += scroll_amount

        # Remove platforms below the visible window
        platforms = [p for p in platforms if p.rect.y >= 0]

    # Generate new platforms above the visible window
    if player_y < platforms[-3].rect.y + gap:
        new_platform_y = platforms[-3].rect.y - random.randint(50, 100)
        if new_platform_y >= 0:
            new_platform = Platform(
                pygame.Rect(
                    random.randint(0, width - platform_width) // cell_size * cell_size,
                    new_platform_y // cell_size * cell_size,
                    platform_width,
                    platform_height
                )
            )
            platforms.append(new_platform)

    # End the game when hitting the bottom
    if player_y >= height - player_size:
        running = False

    player_rect.x = player_x
    player_rect.y = player_y

    window.fill((0, 255, 255))
    # draw_grid(window, width, height, cell_size)  # Grid drawing removed
    draw_player(window, player_rect)
    draw_platforms(window, platforms)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
