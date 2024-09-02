import pygame
import random
import os

# Initialize Pygame
pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((800, 600))

# Load images and masks
def load_image_with_mask(image_path):
    try:
        image = pygame.image.load(image_path).convert_alpha()
        mask = pygame.mask.from_surface(image)
        return image, mask
    except pygame.error as e:
        print(f"Cannot load image: {image_path} - {e}")
        return None, None

# Load player and platform images
player_image, player_mask = load_image_with_mask('Doodler5.png')
platform_images = {
    'normal': load_image_with_mask('PlatNorm.png'),
    'breakable': load_image_with_mask('BreakPlat.png'),
    'fly': load_image_with_mask('FlyPlat.png'),
    'moving': load_image_with_mask('MovePlat.png'),
    'danger': load_image_with_mask('DangerPlat.png'),
    'superJump': load_image_with_mask('SuperJumpPlat.png')
}

# Load background image
background_image = pygame.image.load('background.png').convert()

# Constants
width, height = 300, 450
cell_size = 10
platform_width, platform_height = 50, 50
initial_platform_count = 20
gap = 50  # Minimum gap to trigger new platform generation
gravity = 0.2
jump_strength = 9
super_jump_strength = jump_strength * 2
fly_duration = 5000  # Duration of fly effect in milliseconds

# Initialize font
font = pygame.font.SysFont(None, 24)

# Functions
def create_window(width, height):
    win = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    win.fill((0, 255, 255))  # Cyan background
    pygame.display.set_caption("Doodle Jump")
    return win

def draw_player(win, player_rect):
    win.blit(player_image, player_rect)  # Draw player image

def draw_platforms(win, platforms):
    for platform in platforms:
        win.blit(platform.image, platform.rect)  # Draw platform image

def generate_platforms(grid_width, grid_height, cell_size, num_platforms, y_offset=0):
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
        if random.random() < 0.2:  # 20% chance to place a moving platform
            moving_platform_x = row_x_positions.pop()
            moving_platform = Platform(
                pygame.Rect(
                    moving_platform_x,
                    y,
                    platform_width,
                    platform_height
                ),
                'moving'
            )
            platforms.append(moving_platform)
            rows_with_moving_platforms.add(y)  # Mark this row as containing a moving platform

        # Place other platforms
        for x in row_x_positions:
            if len(platforms) >= num_platforms:
                break
            if random.random() < 0.5 and y not in rows_with_moving_platforms:  # 50% chance to place a platform
                platform_type = random.choices(
                    ['normal', 'breakable', 'fly', 'superJump', 'danger'],
                    [0.60, 0.10, 0.07, 0.5, 0.05]  # Adjusted to ensure superJump is included
                )[0]
                platform = Platform(
                    pygame.Rect(
                        x,
                        y,
                        platform_width,
                        platform_height
                    ),
                    platform_type
                )
                platforms.append(platform)
        y += vertical_spacing  # Increased vertical spacing

    return platforms

class Platform:
    def __init__(self, rect, platform_type):
        self.rect = rect
        self.platform_type = platform_type
        self.image, self.mask = platform_images[platform_type]
        self.scored = False  # Track if the platform has been scored
        if platform_type == 'moving':
            self.direction = random.choice([-1, 1])  # Start moving left or right randomly
            self.speed = 2  # Speed of the moving platform

def check_collision(rect1, mask1, rect2, mask2):
    offset = (rect2.left - rect1.left, rect2.top - rect1.top)
    overlap = mask1.overlap(mask2, offset)
    return overlap is not None

def reset_game():
    global player_rect, player_dy, super_jump_count, using_super_jump, flying, fly_end_time, score, game_over
    global platforms

    player_rect = pygame.Rect(random.randint(0, width - player_size), height // 2, player_size, player_size)
    player_dy = 0.0
    super_jump_count = 0
    using_super_jump = False
    flying = False
    fly_end_time = 0
    score = 0
    game_over = False
    platforms = generate_platforms(width, height, cell_size, initial_platform_count)

# Load highscore
def load_highscore():
    if os.path.isfile('highscore.txt'):
        with open('highscore.txt', 'r') as file:
            return int(file.read().strip())
    return 0

# Save highscore
def save_highscore(new_highscore):
    with open('highscore.txt', 'w') as file:
        file.write(str(new_highscore))

def place_player_on_platform(platforms, player_rect):
    for platform in platforms:
        if platform.rect.y < height // 4 and platform.rect.x <= player_rect.x <= platform.rect.x + platform_width:
            return platform.rect.y - player_size
    return height // 4 - player_size

# Initialize game variables
player_size = 9

player_x = random.randint(0, width - player_size)
player_rect = pygame.Rect(player_x, height // 2, player_size, player_size)
player_dy = 0.0
flying = False
fly_end_time = 0
score = 0
game_over = False
super_jump_count = 0
super_jump_strength = jump_strength * 2
using_super_jump = False
highscore = load_highscore()
window = create_window(width, height)
platforms = generate_platforms(width, height, cell_size, initial_platform_count)

# Game loop
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_over:
                    reset_game()
                elif super_jump_count > 0:
                    using_super_jump = True
                    super_jump_count -= 1
            if event.key == pygame.K_ESCAPE:
                running = False

    if game_over:
        window.fill((0, 255, 255))
        game_over_text = "Game Over, Press Space to Continue"
        game_over_surface = font.render(game_over_text, True, (0, 0, 0))
        game_over_rect = game_over_surface.get_rect(center=(width // 2, height // 2))
        window.blit(game_over_surface, game_over_rect)
        pygame.display.flip()
        clock.tick(60)
        continue

    keys = pygame.key.get_pressed()
    if not game_over:
        if keys[pygame.K_LEFT]:
            player_rect.x -= 3
            if player_rect.left < -player_rect.width:
                player_rect.right = width
        if keys[pygame.K_RIGHT]:
            player_rect.x += 3
            if player_rect.right > width:
                player_rect.left = -player_rect.width

    current_time = pygame.time.get_ticks()
    if flying:
        if current_time < fly_end_time:
            player_rect.y -= 5  # Move player upwards while flying
        else:
            flying = False
            player_dy = gravity  # Resume normal gravity

    if not flying:
        player_dy += gravity
        player_rect.y += player_dy

    if using_super_jump:
        # Ensure the super jump only affects the next jump
        player_dy = -super_jump_strength
        using_super_jump = False

    # Handle collisions and platform interactions
    platforms_to_remove = []
    for platform in platforms:
        if platform.platform_type == 'moving':
            platform.rect.x += platform.direction * platform.speed
            if platform.rect.left <= 0:
                platform.rect.left = 0
                platform.direction = 1  # Move right
            elif platform.rect.right >= width:
                platform.rect.right = width
                platform.direction = -1  # Move left

        if player_rect.bottom >= platform.rect.top and player_rect.bottom <= platform.rect.bottom and player_dy > 0:
            if player_rect.left <= platform.rect.right and player_rect.right >= platform.rect.left:
                if platform.platform_type == 'breakable':
                    platforms_to_remove.append(platform)
                elif platform.platform_type == 'fly':
                    flying = True
                    fly_end_time = current_time + fly_duration
                elif platform.platform_type == 'superJump':
                    super_jump_count += 1
                player_dy = -jump_strength
                score += 1

    for platform in platforms_to_remove:
        platforms.remove(platform)

    # Scroll platforms down
    if player_rect.top <= height // 4:
        for platform in platforms:
            platform.rect.y += abs(player_dy)

        player_rect.y += abs(player_dy)

        # Add new platforms if needed
        if len(platforms) < initial_platform_count:
            new_platform_y = min(platform.rect.y for platform in platforms) - gap
            platform_type = random.choices(
                ['normal', 'breakable', 'fly', 'superJump', 'danger', 'moving'],
                [0.60, 0.10, 0.07, 0.5, 0.05, 0.20]
            )[0]
            new_platform = Platform(
                pygame.Rect(random.randint(0, width - platform_width), new_platform_y, platform_width, platform_height),
                platform_type
            )
            platforms.append(new_platform)
        platforms = [platform for platform in platforms if platform.rect.top < height]
    if player_rect.top > height:
        game_over = True
        if score > highscore:
            highscore = score
            save_highscore(highscore)

    # Draw everything
    window.blit(background_image, (0, 0))  # Draw background image
    draw_platforms(window, platforms)
    draw_player(window, player_rect)

    # Draw score and highscore
    score_surface = font.render(f"Score: {score}", True, (0, 0, 0))
    window.blit(score_surface, (10, 10))
    highscore_surface = font.render(f"Highscore: {highscore}", True, (0, 0, 0))
    window.blit(highscore_surface, (10, 40))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
