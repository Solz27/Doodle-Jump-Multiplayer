from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
import random


# Helper class to represent the platform and player objects
class Platform:
    def __init__(self, x, y, width, height, color):
        self.rect = [x, y, width, height]
        self.color = color

class MovingPlatform(Platform):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, (1, 1, 0))  # Yellow
        self.direction = random.choice([-1, 1])
        self.speed = 2

    def update(self):
        self.rect[0] += self.direction * self.speed
        if self.rect[0] <= 0 or self.rect[0] + self.rect[2] >= Window.width:
            self.direction *= -1

class BreakablePlatform(Platform):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, (1, 1, 1))  # White

class SpikePlatform(Platform):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, (0, 0, 1))  # Blue

class OrangePlatform(Platform):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, (1, 0.65, 0))  # Orange

class Player:
    def __init__(self, x, y, size):
        self.rect = [x, y, size, size]
        self.dy = 0.0

class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cell_size = 10
        self.platform_width = 35
        self.platform_height = 5
        self.initial_platform_count = 30
        self.player_size = 15
        self.gravity = 0.7
        self.jump_strength = 15.0
        self.base_jump_strength = self.jump_strength
        self.platforms = []
        self.player = None
        self.scroll_amount = 0
        self.generate_initial_platforms()
        self.create_player()
        Clock.schedule_interval(self.update, 1 / 60.0)

    def generate_initial_platforms(self):
        self.platforms = self.generate_platforms(Window.width, Window.height, self.initial_platform_count)

    def create_player(self):
        player_x = random.randint(0, Window.width - self.player_size)
        player_y = self.place_player_on_platform(self.platforms, player_x)
        self.player = Player(player_x, player_y, self.player_size)

    def generate_platforms(self, grid_width, grid_height, num_platforms, y_offset=0):
        platforms = []
        available_x_positions = list(range(0, grid_width, self.cell_size * 15))
        random.shuffle(available_x_positions)

        y = y_offset
        rows_with_moving_platforms = set()
        vertical_spacing = self.cell_size * 6

        while y < grid_height + y_offset and len(platforms) < num_platforms:
            row_x_positions = available_x_positions.copy()
            random.shuffle(row_x_positions)

            if random.random() < 0.2:
                moving_platform_x = row_x_positions.pop()
                moving_platform = MovingPlatform(
                    moving_platform_x + random.randint(0, self.cell_size * 9),
                    y + random.randint(0, self.cell_size * 2),
                    self.platform_width,
                    self.platform_height
                )
                platforms.append(moving_platform)
                rows_with_moving_platforms.add(y)

            for x in row_x_positions:
                if len(platforms) >= num_platforms:
                    break
                if random.random() < 0.5 and y not in rows_with_moving_platforms:
                    if random.random() < 0.05:
                        platform = BreakablePlatform(
                            x + random.randint(0, self.cell_size * 9),
                            y + random.randint(0, self.cell_size * 2),
                            self.platform_width,
                            self.platform_height
                        )
                    elif random.random() < 0.05:
                        platform = SpikePlatform(
                            x + random.randint(0, self.cell_size * 9),
                            y + random.randint(0, self.cell_size * 2),
                            self.platform_width,
                            self.platform_height
                        )
                    elif random.random() < 0.05:
                        platform = OrangePlatform(
                            x + random.randint(0, self.cell_size * 9),
                            y + random.randint(0, self.cell_size * 2),
                            self.platform_width,
                            self.platform_height
                        )
                    else:
                        platform = Platform(
                            x + random.randint(0, self.cell_size * 9),
                            y + random.randint(0, self.cell_size * 2),
                            self.platform_width,
                            self.platform_height,
                            (1, 0, 0)  # Red
                        )
                    platforms.append(platform)
            y += vertical_spacing

        return platforms

    def place_player_on_platform(self, platforms, player_x):
        for platform in platforms:
            if platform.rect[1] < Window.height // 4 and platform.rect[0] <= player_x <= platform.rect[0] + self.platform_width:
                return platform.rect[1] - self.player_size
        return Window.height // 4 - self.player_size

    def on_size(self, *args):
        self.generate_initial_platforms()
        self.create_player()

    def on_touch_down(self, touch):
        if touch.x < Window.width / 2:
            self.player.rect[0] -= 5
            if self.player.rect[0] < -self.player_size:
                self.player.rect[0] = Window.width
        else:
            self.player.rect[0] += 5
            if self.player.rect[0] > Window.width:
                self.player.rect[0] = -self.player_size

    def update(self, dt):
        self.player.dy += self.gravity
        self.player.rect[1] += self.player.dy

        hit_platform = False
        for platform in self.platforms:
            if isinstance(platform, MovingPlatform):
                platform.update()

            if self.collide(self.player.rect, platform.rect):
                hit_platform = True
                if self.player.dy > 0 and not isinstance(platform, SpikePlatform):
                    self.player.rect[1] = platform.rect[1] - self.player_size
                    self.player.dy = -self.jump_strength

                if isinstance(platform, BreakablePlatform):
                    self.platforms.remove(platform)

                if isinstance(platform, SpikePlatform):
                    self.stop_game()  # End the game on hitting a spike

                if isinstance(platform, OrangePlatform):
                    self.jump_strength = self.base_jump_strength * 2  # Double jump power for orange platform

                if not isinstance(platform, OrangePlatform):
                    self.jump_strength = self.base_jump_strength  # Reset jump power if hitting any non-orange platform

        if not hit_platform:
            self.jump_strength = self.base_jump_strength

        if self.player.rect[1] < Window.height // 4:
            self.scroll_amount = Window.height // 4 - self.player.rect[1]
            self.player.rect[1] = Window.height // 4
            for platform in self.platforms:
                platform.rect[1] += self.scroll_amount

            self.platforms = [p for p in self.platforms if p.rect[1] >= 0]

        if self.player.rect[1] >= Window.height - self.player_size:
            self.stop_game()

        self.canvas.clear()
        with self.canvas:
            Color(0, 1, 1)  # Cyan background
            Rectangle(pos=(0, 0), size=Window.size)
            self.draw_player()
            self.draw_platforms()

    def draw_player(self):
        Color(0, 1, 0)  # Green
        Rectangle(pos=(self.player.rect[0], self.player.rect[1]), size=(self.player.rect[2], self.player.rect[3]))

    def draw_platforms(self):
        for platform in self.platforms:
            Color(*platform.color)
            Rectangle(pos=(platform.rect[0], platform.rect[1]), size=(platform.rect[2], platform.rect[3]))

    def collide(self, rect1, rect2):
        return (rect1[0] < rect2[0] + rect2[2] and rect1[0] + rect1[2] > rect2[0] and
                rect1[1] < rect2[1] + rect2[3] and rect1[1] + rect1[3] > rect2[1])

    def stop_game(self):
        print("Game Over")
        App.get_running_app().stop()

class DoodleJumpApp(App):
    def build(self):
        Window.size = (250, 450)
        game = GameWidget()
        Window.bind(on_resize=game.on_size)
        return game

if __name__ == '__main__':
    DoodleJumpApp().run()
