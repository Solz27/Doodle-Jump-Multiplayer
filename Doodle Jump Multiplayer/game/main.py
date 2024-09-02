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
        print(f"Loaded image: {image_path}")
        return image, mask
    except pygame.error as e:
        print(f"Cannot load image: {image_path} - {e}")
        return None, None


# Load player and platform images
player_image, player_mask = load_image_with_mask('Doodler5.png')
spritesheet = pygame.image.load("Doodler56.png")

fwidth = 55
fheight = 55

right_frame = spritesheet.subsurface(pygame.Rect(0, 0, fwidth, fheight))  # First frame (right orientation)
left_frame = spritesheet.subsurface(pygame.Rect(fwidth, 0, fwidth, fheight))  # Second frame (left orientation)

platform_images = {
    'normal': load_image_with_mask('PlatNorm.png'),
    'breakable': load_image_with_mask('BreakPlat.png'),
    'fly': load_image_with_mask('FlyPlat.png'),
    'moving': load_image_with_mask('MovePlat.png'),
    'danger': load_image_with_mask('DangerPlat.png'),
    'superJump': load_image_with_mask('SuperJumpPlat.png')
}

background_image = pygame.image.load('background.png').convert()

# Constants
width, height = 250, 450
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
def draw_screen(win):
    win.fill((0, 255, 0))
    buttonSize = 150
    buttonColor = (0, 255, 0)
    buttonRect = pygame.Rect((width - buttonSize) // 2, (height - buttonSize) // 2, buttonSize, buttonSize)
    pygame.draw.rect(win, buttonColor, buttonRect)

    draw_Start = font.render('Start', True, (0, 0, 0))
    draw_Start_rect = draw_Start.get_rect(center=buttonRect.center)
    win.blit(draw_Start, draw_Start_rect)

    pygame.display.flip()
    return buttonRect


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
    if overlap is not None:
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


def run_game(client_socket, player_id, other_player):
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))

    # Load images
    player_image = pygame.image.load('Doodler5.png').convert_alpha()
    other_player_image = pygame.image.load('OtherDoodler.png').convert_alpha()
    background_image = pygame.image.load('background.png').convert()

    player_rect = pygame.Rect(100, 300, player_image.get_width(), player_image.get_height())
    other_player_rect = pygame.Rect(other_player['x'], other_player['y'], other_player_image.get_width(),
                                    other_player_image.get_height())

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_rect.x -= 3
        if keys[pygame.K_RIGHT]:
            player_rect.x += 3
        if keys[pygame.K_SPACE]:
            player_rect.y -= 10  # Example jump mechanic

        # Send the player's position to the server
        client_socket.send(f"MOVE:{player_rect.x}:{player_rect.y}".encode())

        # Update the other player's position
        other_player_rect.x = other_player['x']
        other_player_rect.y = other_player['y']

        # Draw everything
        screen.blit(background_image, (0, 0))
        screen.blit(player_image, player_rect.topleft)
        screen.blit(other_player_image, other_player_rect.topleft)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


# Initialize game variables
player_size = 9

player_x = random.randint(0, width - player_size)
player_rect = pygame.Rect(player_x, height // 2, player_size, player_size)
player_dy = 0.0
orient_Player = 'Right'
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

start_screen = True
startButton_rect = None

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
    if start_screen:
        draw_screen(window)
        startButton_rect = draw_screen(window)

        while start_screen:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    start_screen = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mousePos = pygame.mouse.get_pos()
                    if startButton_rect.collidepoint(mousePos):
                        start_screen = False
                        reset_game()
                elif event.type == pygame.KEYDOWN:
                    if event.type == pygame.K_ESCAPE:
                        running = False
                        start_screen = False

    if game_over:
        window.blit(background_image, (0, 100))
        game_over_text = "Game Over"
        game_over_surface = font.render(game_over_text, True, (0, 0, 0))
        game_over_rect = game_over_surface.get_rect(center=(width // 2, height // 2))
        window.blit(game_over_surface, game_over_rect, )

        continue_text = "Press Space to Continue"
        continue_surface = font.render(continue_text, True, (0, 0, 0))
        continue_rect = continue_surface.get_rect(center=(width // 2, height // 2 + 20))
        window.blit(continue_surface, continue_rect)

        pygame.display.flip()
        clock.tick(60)
        continue

    keys = pygame.key.get_pressed()
    if not game_over:
        if keys[pygame.K_LEFT]:
            player_rect.x -= 3
            if player_rect.left < -player_rect.width:
                orient_Player = 'Left'
                print(f"direction:{orient_Player}")
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

        if check_collision(player_rect, player_mask, platform.rect, platform.mask):
            if player_dy > 0 and platform.platform_type != 'danger':
                player_rect.bottom = platform.rect.top
                if not using_super_jump:
                    if platform.platform_type == 'superJump':
                        player_dy = -super_jump_strength
                    else:
                        player_dy = -jump_strength

                if platform.platform_type == 'breakable':
                    platforms_to_remove.append(platform)
                    score += 1  # Increment score when hitting breakable platform
                elif platform.platform_type == 'fly':
                    score += 10
                    flying = True  # Activate fly effect
                    fly_end_time = pygame.time.get_ticks() + fly_duration
                elif platform.platform_type == 'normal':
                    score += 1
                elif platform.platform_type == 'moving':
                    score += 2
                elif platform.platform_type == 'superJump':
                    score += 5
            if platform.platform_type == 'danger':
                game_over = True

    # Remove breakable platforms
    platforms = [p for p in platforms if p not in platforms_to_remove]
    if player_rect.y < height // 4:
        scroll_amount = height // 4 - player_rect.y
        player_rect.y = height // 4
        for platform in platforms:
            platform.rect.y += scroll_amount
        platforms = [p for p in platforms if p.rect.y >= 0]

    if player_rect.y < platforms[-1].rect.y + gap:
        if random.random() < 0.5:
            new_platform_y = platforms[-1].rect.y - random.randint(70, 120)
            if new_platform_y >= 0:
                platform_type = random.choices(
                    ['normal', 'breakable', 'fly', 'moving', 'danger'],
                    [0.60, 0.10, 0.07, 0.20, 0.05]
                )[0]
                new_platform = Platform(
                    pygame.Rect(
                        random.randint(0, width - platform_width),
                        new_platform_y,
                        platform_width,
                        platform_height
                    ),
                    platform_type
                )
                platforms.append(new_platform)

    if player_rect.bottom >= height:
        game_over = True
        platforms.clear()

    # Drawing
    window.fill((0, 255, 255))
    window.blit(background_image, (0, 100))
    draw_player(window, player_rect)
    draw_platforms(window, platforms)

    flying_state_text = "Flying: True" if flying else "flying: False"
    flying_text_surface = font.render(flying_state_text, True, (0, 0, 0))
    window.blit(flying_text_surface, (10, 10))

    score_text = f"Score: {score}"
    score_surface = font.render(score_text, True, (0, 0, 0))
    score_rect = score_surface.get_rect(topright=(width - 10, 10))
    window.blit(score_surface, score_rect)

    highscore_text = f"Highscore: {highscore}"
    highscore_surface = font.render(highscore_text, True, (0, 0, 0))
    highscore_rect = highscore_surface.get_rect(topright=(width - 10, 30))
    window.blit(highscore_surface, highscore_rect)

    if game_over:
        game_over_text = "Game Over, Press Space to Continue"
        game_over_surface = font.render(game_over_text, True, (0, 0, 0))
        game_over_rect = game_over_surface.get_rect(center=(width // 2, height // 2))
        window.blit(game_over_surface, game_over_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()