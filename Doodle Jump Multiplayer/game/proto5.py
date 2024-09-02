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
    rows_with_moving_platforms = set()  # To keep track of rows with moving platforms
    vertical_spacing = cell_size * 6  # Increased vertical spacing between platforms

    while y < grid_height + y_offset and len(platforms) < num_platforms:
        row_x_positions = available_x_positions.copy()  # Copy x positions for this row
        random.shuffle(row_x_positions)  # Shuffle to randomize

        # Chance to place a moving platform
        if random.random() < 0.2:  # 20% chance to place a moving platform
            moving_platform_x = row_x_positions.pop()
            moving_platform = MovingPlatform(
                pygame.Rect(
                    moving_platform_x + random.randint(0, cell_size * 9),
                    y + random.randint(0, cell_size * 2),
                    platform_width,
                    platform_height
                )
            )
            platforms.append(moving_platform)
            rows_with_moving_platforms.add(y)  # Mark this row as containing a moving platform

        # Place normal, breakable, spike, or ability platforms, avoiding rows with moving platforms
        for x in row_x_positions:
            if len(platforms) >= num_platforms:
                break
            if random.random() < 0.5 and y not in rows_with_moving_platforms:  # 50% chance to place a platform
                if random.random() < 0.05:  # 5% chance to place a breakable platform
                    platform = BreakablePlatform(
                        pygame.Rect(
                            x + random.randint(0, cell_size * 9),
                            y + random.randint(0, cell_size * 2),
                            platform_width,
                            platform_height
                        )
                    )
                elif random.random() < 0.05:  # 5% chance to place a spike
                    platform = SpikePlatform(
                        pygame.Rect(
                            x + random.randint(0, cell_size * 9),
                            y + random.randint(0, cell_size * 2),
                            platform_width,
                            platform_height
                        )
                    )
                elif random.random() < 0.05:  # 5% chance to place an ability platform
                    platform = AbilityPlatform(
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
        y += vertical_spacing  # Increased vertical spacing

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

class BreakablePlatform:
    def __init__(self, rect):
        self.rect = rect
        self.color = (255, 255, 255)  # White color for breakable platforms

class SpikePlatform:
    def __init__(self, rect):
        self.rect = rect
        self.color = (0, 0, 255)  # Blue color for spike platforms

class AbilityPlatform:
    def __init__(self, rect):
        self.rect = rect
        self.color = (255, 165, 0)  # Orange color for ability platforms

pygame.init()
width, height = 250, 450
cell_size = 10
platform_width, platform_height = 35, 5
initial_platform_count = 30 
gap = 50  # Minimum gap to trigger new platform generation
window = create_window(width, height)

# Initialize player properties
player_size = 15
player_x = random.randint(0, width - player_size)  # Random horizontal position

# Generate initial platforms
platforms = generate_platforms(width, height, cell_size, platform_width, platform_height, initial_platform_count)

# Find the nearest platform to start with
def place_player_on_platform(platforms, player_rect):
    for platform in platforms:
        if platform.rect.y < height // 4 and platform.rect.x <= player_rect.x <= platform.rect.x + platform_width:
            return platform.rect.y - player_size
    return height // 4 - player_size

# Set initial player position on a platform
player_y = place_player_on_platform(platforms, pygame.Rect(player_x, 0, player_size, player_size))
player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
player_dy = 0.0

# Bounce parameters
gravity = 0.7
jump_strength = 15.0
super_jump_strength = jump_strength * 2
super_jump_count = 0
using_super_jump = False

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
    if keys[pygame.K_SPACE] and super_jump_count > 0 and not using_super_jump:
        using_super_jump = True
        super_jump_count -= 1

    player_dy += gravity
    player_y += player_dy

    # Check collision with platforms
    for platform in platforms:
        if isinstance(platform, MovingPlatform):
            platform.update(width)  # Update moving platforms

        if player_rect.colliderect(platform.rect):
            if player_dy > 0 and not isinstance(platform, SpikePlatform):
                player_y = platform.rect.y - player_size
                if using_super_jump:
                    player_dy = -super_jump_strength
                    using_super_jump = False
                else:
                    player_dy = -jump_strength

            if isinstance(platform, BreakablePlatform):
                platforms.remove(platform)  # Remove the breakable platform

            if isinstance(platform, SpikePlatform):
                running = False  # End the game on hitting a spike

            if isinstance(platform, AbilityPlatform):
                super_jump_count += 1
                platforms.remove(platform)  # Remove the ability platform after collision

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
            # Generate new platform with a 20% chance of being a moving platform
            if random.random() < 0.2:
                new_platform = MovingPlatform(
                    pygame.Rect(
                        random.randint(0, width - platform_width) // cell_size * cell_size,
                        new_platform_y // cell_size * cell_size,
                        platform_width,
                        platform_height
                    )
                )
            elif random.random() < 0.05:
                new_platform = BreakablePlatform(
                    pygame.Rect(
                        random.randint(0, width - platform_width) // cell_size * cell_size,
                        new_platform_y // cell_size * cell_size,
                        platform_width,
                        platform_height
                    )
                )
            elif random.random() < 0.05:
                new_platform = SpikePlatform(
                    pygame.Rect(
                        random.randint(0, width - platform_width) // cell_size * cell_size,
                        new_platform_y // cell_size * cell_size,
                        platform_width,
                        platform_height
                    )
                )
            elif random.random() < 0.05:
                new_platform = AbilityPlatform(
                    pygame.Rect(
                        random.randint(0, width - platform_width) // cell_size * cell_size,
                        new_platform_y // cell_size * cell_size,
                        platform_width,
                        platform_height
                    )
                )
            else:
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
    draw_player(window, player_rect)
    draw_platforms(window, platforms)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
