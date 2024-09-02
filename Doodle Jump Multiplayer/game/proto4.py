import pygame
import random

# Initialize font
pygame.font.init()
font = pygame.font.SysFont(None, 24)

# Highscore file
highscore_file = "highscore.txt"

# Function to read highscore
def read_highscore():
    try:
        with open(highscore_file, "r") as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return 0

# Function to save highscore
def save_highscore(score):
    with open(highscore_file, "w") as file:
        file.write(str(score))

def create_window(width, height):
    win = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    win.fill((0, 255, 255))  # Cyan background
    pygame.display.set_caption("Doodle Jump")
    return win

def draw_player(win, player_image, player_rect, debug_mode):
    win.blit(player_image, player_rect)  # Draw the player image
    if debug_mode:
        # Draw the collision rectangle
        pygame.draw.rect(win, (255, 0, 0, 128), player_rect, 2)  # Semi-transparent red rectangle

def draw_platforms(win, platforms, debug_mode):
    for platform in platforms:
        win.blit(platform.image, platform.rect)  # Draw platform with its image
        if debug_mode:
            # Draw the collision rectangle
            pygame.draw.rect(win, (0, 255, 0, 128), platform.rect, 2)  # Semi-transparent green rectangle

def generate_platforms(grid_width, grid_height, cell_size, platform_width, platform_height, num_platforms, y_offset=0):
    platforms = []
    available_x_positions = list(range(0, grid_width, cell_size * 15))  # Ensure horizontal spacing
    random.shuffle(available_x_positions)  # Shuffle to randomize

    y = y_offset
    rows_with_moving_platforms = set()  # To keep track of rows with moving platforms
    vertical_spacing = cell_size * 8  # Increased vertical spacing between platforms

    while y < grid_height + y_offset and len(platforms) < num_platforms:
        row_x_positions = available_x_positions.copy()  # Copy x positions for this row
        random.shuffle(row_x_positions)  # Shuffle to randomize

        # Chance to place a moving platform
        if random.random() < 0.15:  # Reduced chance to place a moving platform
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

        # Place normal, breakable, spike, ability, or fly platforms, avoiding rows with moving platforms
        for x in row_x_positions:
            if len(platforms) >= num_platforms:
                break
            if random.random() < 0.3 and y not in rows_with_moving_platforms:  # Reduced chance to place a platform
                if random.random() < 0.03:  # Reduced chance to place a breakable platform
                    platform = BreakablePlatform(
                        pygame.Rect(
                            x + random.randint(0, cell_size * 9),
                            y + random.randint(0, cell_size * 2),
                            platform_width,
                            platform_height
                        )
                    )
                elif random.random() < 0.03:  # Reduced chance to place a danger platform
                    platform = DangerPlatform(
                        pygame.Rect(
                            x + random.randint(0, cell_size * 9),
                            y + random.randint(0, cell_size * 2),
                            platform_width,
                            platform_height
                        )
                    )
                elif random.random() < 0.03:  # Reduced chance to place an ability platform
                    platform = AbilityPlatform(
                        pygame.Rect(
                            x + random.randint(0, cell_size * 9),
                            y + random.randint(0, cell_size * 2),
                            platform_width,
                            platform_height
                        )
                    )
                elif random.random() < 0.02:  # Reduced chance to place a fly platform
                    platform = FlyPlatform(
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
        self.image = platform_images['normal']
        self.scored = False

class MovingPlatform:
    def __init__(self, rect):
        self.rect = rect
        self.image = platform_images['moving']
        self.direction = random.choice([-1, 1])  # Random initial direction
        self.speed = 2  # Speed of movement
        self.scored = False

    def update(self, width):
        # Move platform horizontally
        self.rect.x += self.direction * self.speed
        # Reverse direction if hitting window edges
        if self.rect.left <= 0 or self.rect.right >= width:
            self.direction *= -1

class BreakablePlatform:
    def __init__(self, rect):
        self.rect = rect
        self.image = platform_images['breakable']
        self.scored = False

class DangerPlatform:
    def __init__(self, rect):
        self.rect = rect
        self.image = platform_images['danger']
        self.scored = False

class AbilityPlatform:
    def __init__(self, rect):
        self.rect = rect
        self.image = platform_images['ability']
        self.scored = False

class FlyPlatform:
    def __init__(self, rect):
        self.rect = rect
        self.image = platform_images['fly']
        self.scored = False

pygame.init()
width, height = 250, 450
cell_size = 10
platform_width, platform_height = 50, 50  # Updated to 50x50 for images
initial_platform_count = 15  # Reduced initial platform count
gap = 50  # Minimum gap to trigger new platform generation
window = create_window(width, height)

# Load images
player_image = pygame.image.load('Doodler.png').convert_alpha()
platform_images = {
    'normal': pygame.image.load('PlatNorm.png').convert_alpha(),
    'breakable': pygame.image.load('BreakPlat.png').convert_alpha(),
    'fly': pygame.image.load('FlyPlat.png').convert_alpha(),
    'moving': pygame.image.load('MovePlat.png').convert_alpha(),
    'danger': pygame.image.load('Danger Plat.png').convert_alpha(),
    'ability': pygame.image.load('SuperJumpPlat.png').convert_alpha(),
}

# Initialize player position and hitbox
player_rect = player_image.get_rect()
player_rect.centerx = width // 2
player_rect.bottom = height // 2
player_dy = 0.0

# Generate initial platforms
platforms = generate_platforms(width, height, cell_size, platform_width, platform_height, initial_platform_count)

# Find the nearest platform to start with
def place_player_on_platform(platforms, player_rect):
    for platform in platforms:
        if platform.rect.y < height // 4 and platform.rect.x <= player_rect.centerx <= platform.rect.x + platform_width:
            return platform.rect.y - player_rect.height
    return height // 4 - player_rect.height

# Set initial player position on a platform
player_rect.y = place_player_on_platform(platforms, player_rect)
player_dy = 0.0

# Bounce parameters
gravity = 0.7
jump_strength = 15.0
super_jump_strength = jump_strength * 2
super_jump_count = 0
using_super_jump = False
flying = False
fly_end_time = 0
fly_duration = 3000  # Duration of fly effect in milliseconds

clock = pygame.time.Clock()
# Event loop
running = True

# Add a game_over variable
game_over = False
score = 0
highscore = read_highscore()  # Read the highscore from the file

def reset_game():
    global player_rect, player_dy, super_jump_count, using_super_jump, flying, fly_end_time, platforms, score, game_over, highscore
    player_rect.centerx = width // 2
    player_rect.bottom = height // 2
    player_dy = 0.0
    super_jump_count = 0
    using_super_jump = False
    flying = False
    fly_end_time = 0
    platforms = generate_platforms(width, height, cell_size, platform_width, platform_height, initial_platform_count)
    player_rect.y = place_player_on_platform(platforms, player_rect)
    player_dy = 0.0
    score = 0
    game_over = False

debug_mode = False  # Initial state of debug mode

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_over:
                reset_game()  # Restart the game when space is pressed
            if event.key == pygame.K_ESCAPE:
                running = False  # Exit the game on ESC key press
            if event.key == pygame.K_d:
                debug_mode = not debug_mode  # Toggle debug mode on 'D' key press

    keys = pygame.key.get_pressed()

    if game_over:
        # Display game over message
        window.fill((0, 255, 255))
        game_over_text = "Game Over, Press Space to Continue"
        game_over_surface = font.render(game_over_text, True, (0, 0, 0))  # Black color
        game_over_rect = game_over_surface.get_rect(center=(width // 2, height // 2))  # Center of the screen
        window.blit(game_over_surface, game_over_rect)
        pygame.display.flip()
        clock.tick(60)
        continue

    if not flying:
        if keys[pygame.K_LEFT]:
            player_rect.x -= 5
            if player_rect.left < -player_rect.width:
                player_rect.right = width
        if keys[pygame.K_RIGHT]:
            player_rect.x += 5
            if player_rect.right > width:
                player_rect.left = -player_rect.width
        if keys[pygame.K_SPACE] and super_jump_count > 0 and not using_super_jump:
            using_super_jump = True
            super_jump_count -= 1

    current_time = pygame.time.get_ticks()
    if flying:
        if current_time < fly_end_time:
            player_rect.y -= 5
        else:
            flying = False

    # Update player position
    if not flying:
        player_dy += gravity
        player_rect.y += player_dy

    # Check collision with platforms
    for platform in platforms:
        if isinstance(platform, MovingPlatform):
            platform.update(width)  # Update moving platforms

        if player_rect.colliderect(platform.rect):
            if player_dy > 0 and not isinstance(platform, DangerPlatform):
                player_rect.bottom = platform.rect.top
                if using_super_jump:
                    player_dy = -super_jump_strength
                    using_super_jump = False
                else:
                    player_dy = -jump_strength

                # Update the score based on the platform type
                if not platform.scored:
                    if isinstance(platform, Platform):
                        score += 1
                    elif isinstance(platform, AbilityPlatform):
                        score += 10
                    elif isinstance(platform, BreakablePlatform):
                        score += 1
                    elif isinstance(platform, FlyPlatform):
                        score += 10
                    elif isinstance(platform, MovingPlatform):
                        score += 2
                    platform.scored = True  # Mark platform as scored

            if isinstance(platform, BreakablePlatform):
                platforms.remove(platform)  # Remove the breakable platform

            if isinstance(platform, AbilityPlatform) and not platform.scored:
                super_jump_count += 1  # Increment super jump count
                platform.scored = True  # Ensure it doesn't grant another super jump

            if isinstance(platform, FlyPlatform):
                flying = True
                fly_end_time = pygame.time.get_ticks() + fly_duration  # Set fly duration

            if isinstance(platform, DangerPlatform):
                game_over = True  # End the game on hitting a danger platform

    # Scroll the view downward when player reaches halfway
    if player_rect.y < height // 4:
        scroll_amount = height // 4 - player_rect.y
        player_rect.y = height // 4
        for platform in platforms:
            platform.rect.y += scroll_amount

        # Remove platforms below the visible window
        platforms = [p for p in platforms if p.rect.y >= 0]

    # Generate new platforms above the visible window with reduced frequency
    if player_rect.y < platforms[-1].rect.y + gap:
        if random.random() < 0.5:  # Reduced probability to add new platforms
            new_platform_y = platforms[-1].rect.y - random.randint(70, 120)  # Increased vertical spacing
            if new_platform_y >= 0:
                if random.random() < 0.01:
                    new_platform = FlyPlatform(
                        pygame.Rect(
                            random.randint(0, width - platform_width),
                            new_platform_y,
                            platform_width,
                            platform_height
                        )
                    )
                elif random.random() < 0.03:
                    new_platform = MovingPlatform(
                        pygame.Rect(
                            random.randint(0, width - platform_width),
                            new_platform_y,
                            platform_width,
                            platform_height
                        )
                    )
                elif random.random() < 0.05:
                    new_platform = BreakablePlatform(
                        pygame.Rect(
                            random.randint(0, width - platform_width),
                            new_platform_y,
                            platform_width,
                            platform_height
                        )
                    )
                elif random.random() < 0.02:
                    new_platform = DangerPlatform(
                        pygame.Rect(
                            random.randint(0, width - platform_width),
                            new_platform_y,
                            platform_width,
                            platform_height
                        )
                    )
                elif random.random() < 0.02:
                    new_platform = AbilityPlatform(
                        pygame.Rect(
                            random.randint(0, width - platform_width),
                            new_platform_y,
                            platform_width,
                            platform_height
                        )
                    )
                else:
                    new_platform = Platform(
                        pygame.Rect(
                            random.randint(0, width - platform_width),
                            new_platform_y,
                            platform_width,
                            platform_height
                        )
                    )
                platforms.append(new_platform)

    # End the game when hitting the bottom
    if player_rect.bottom >= height:
        game_over = True

    window.fill((0, 255, 255))
    draw_player(window, player_image, player_rect, debug_mode)
    draw_platforms(window, platforms, debug_mode)

    # Draw the super jumps counter
    super_jump_text = f"Superjumps: {super_jump_count}"
    text_surface = font.render(super_jump_text, True, (0, 0, 0))  # Black color
    window.blit(text_surface, (10, 10))  # Draw text at the top-left corner

    # Determine flying state text
    flying_state_text = "flying: true" if flying else "flying: false"
    flying_text_surface = font.render(flying_state_text, True, (0, 0, 0))  # Black color
    window.blit(flying_text_surface, (10, 30))  # Draw text below the super jumps counter

    # Draw the score counter
    score_text = f"Score: {score}"
    score_surface = font.render(score_text, True, (0, 0, 0))  # Black color
    score_rect = score_surface.get_rect(topright=(width - 10, 10))  # Top-right corner
    window.blit(score_surface, score_rect)

    # Draw the highscore counter
    highscore_text = f"Highscore: {highscore}"
    highscore_surface = font.render(highscore_text, True, (0, 0, 0))  # Black color
    highscore_rect = highscore_surface.get_rect(topright=(width - 10, 30))  # Top-right corner below the score
    window.blit(highscore_surface, highscore_rect)

    if game_over:
        game_over_text = "Game Over, Press Space to Continue"
        game_over_surface = font.render(game_over_text, True, (0, 0, 0))  # Black color
        game_over_rect = game_over_surface.get_rect(center=(width // 2, height // 2))  # Center of the screen
        window.blit(game_over_surface, game_over_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
