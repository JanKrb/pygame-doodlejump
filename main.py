import os
import json
import pygame


class Path:
    runtime_path = os.path.dirname(os.path.realpath(__file__))

    assets_path = os.path.join(runtime_path, 'assets')
    assets_images_path = os.path.join(assets_path, 'images')
    assets_fonts_path = os.path.join(assets_path, 'fonts')
    assets_sounds_path = os.path.join(assets_path, 'sounds')

    config_path = os.path.join(runtime_path, 'config.json')
    config_example_path = os.path.join(runtime_path, 'config.example.json')


class Config:
    def __init__(self, config_path=Path.config_path, config_example=Path.config_example_path) -> None:
        self.config_path = config_path
        self.config_example_path = config_example

        self.config = self.load_config()

    def load_config(self) -> dict:
        try:
            with open(self.config_path, 'r') as config_file:
                return json.load(config_file)
        except FileNotFoundError:
            with open(self.config_example_path, 'r') as config_example_file:
                config_example = json.load(config_example_file)
            with open(self.config_path, 'w') as config_file:
                json.dump(config_example, config_file)
            return config_example
        except Exception as e:
            print(e)
            raise

    def save_config(self, config: dict) -> None:
        with open(self.config_path, 'w') as config_file:
            json.dump(config, config_file)


class Background:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.background = pygame.image.load(
            os.path.join(Path.assets_images_path, config.config['images']['background'])).convert()
        self.background = pygame.transform.scale(self.background,
                                                 (config.config['screen']['width'], config.config['screen']['height']))

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.background, (0, 0))

    def update(self) -> None:
        pass


class Button(pygame.sprite.Sprite):
    def __init__(self, config: Config, width: int, height: int, x: int | None, y: int, text: str,
                 color: tuple = (0, 0, 0), font: tuple | pygame.font.Font = ('arial', 24), click_callback=None) -> None:
        super().__init__()

        self.config = config

        self.image_selected = pygame.image.load(
            os.path.join(Path.assets_images_path, config.config['images']['menu_item_selected'])).convert_alpha()
        self.image_unselected = pygame.image.load(
            os.path.join(Path.assets_images_path, config.config['images']['menu_item_unselected'])).convert_alpha()

        self.image_selected = pygame.transform.scale(self.image_selected, (width, height))
        self.image_unselected = pygame.transform.scale(self.image_unselected, (width, height))

        self.image = self.image_unselected
        self.rect = self.image.get_rect()

        self.click_callback = click_callback

        if x is None:
            self.rect.centerx = config.config['screen']['width'] / 2
        else:
            self.rect.centerx = x

        if y is None:
            self.rect.centery = config.config['screen']['height'] / 2
        else:
            self.rect.centery = y

        if type(font) is tuple:
            self.font = pygame.font.SysFont(*font)
        else:
            self.font = font

        self.text = self.font.render(text, True, color)
        self.text_rect = self.text.get_rect()
        self.text_rect.center = self.rect.center

        self.hovered = False

    def update(self) -> None:
        old_hovered = self.hovered
        self.hovered = self.rect.collidepoint(pygame.mouse.get_pos())

        if self.hovered != old_hovered:
            self.image = self.image_selected if self.hovered else self.image_unselected

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def trigger_click(self):
        if self.hovered:
            self.click_callback()


class Timer(object):
    # Credits: https://github.com/adamsralf/pygame_timecontrol

    def __init__(self, duration, with_start=True):
        self.duration = duration
        if with_start:
            self.next = pygame.time.get_ticks()
        else:
            self.next = pygame.time.get_ticks() + self.duration

    def is_next_stop_reached(self):
        if pygame.time.get_ticks() > self.next:
            self.next = pygame.time.get_ticks() + self.duration
            return True
        return False


class Game:
    def __init__(self, config: Config) -> None:
        pygame.init()

        self.config = config
        self.screen = pygame.display.set_mode(
            (self.config.config['screen']['width'], self.config.config['screen']['height']))
        pygame.display.set_caption(self.config.config['screen']['title'])
        self.clock = pygame.time.Clock()
        self.running = True

        self.background = Background(config)
        self.buttons = pygame.sprite.Group()

        self.state = StartState(self.config, self)

    def run(self) -> None:
        while self.running:
            self.clock.tick(self.config.config['screen']['fps'])
            self.events()
            self.update()
            self.draw()

    def events(self) -> None:
        for event in pygame.event.get():
            self.state.handle_events(event)

            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    [button.trigger_click() for button in self.buttons]

    def update(self) -> None:
        self.background.update()
        self.state.update()

    def draw(self) -> None:
        self.background.draw(self.screen)
        self.state.draw(self.screen)
        pygame.display.flip()


class GameState:
    def __init__(self, config: Config, game: Game) -> None:
        self.config = config
        self.game = game

    def draw(self, screen: pygame.Surface) -> None:
        pass

    def update(self) -> None:
        pass

    def handle_events(self, event) -> None:
        pass


class StartState(GameState):
    def __init__(self, config: Config, game: Game) -> None:
        super().__init__(config, game)

        self.logo = pygame.image.load(
            os.path.join(Path.assets_images_path, self.config.config['images']['logo'])).convert_alpha()
        self.logo = pygame.transform.scale(self.logo, (self.config.config['start_screen']['logo_size']['width'],
                                                       self.config.config['start_screen']['logo_size']['height']))
        self.logo_rect = self.logo.get_rect()
        center_logo_x = self.config.config['start_screen']['logo_position']['center_x']
        center_logo_y = self.config.config['start_screen']['logo_position']['center_y']

        if center_logo_x:
            self.logo_rect.centerx = self.config.config['screen']['width'] / 2
        else:
            self.logo_rect.x = self.config.config['start_screen']['logo_position']['x']

        if center_logo_y:
            self.logo_rect.centery = self.config.config['screen']['height'] / 2
        else:
            self.logo_rect.y = self.config.config['start_screen']['logo_position']['y']

        self.start_button = Button(config, 250, 50, None,
                                   self.logo_rect.bottom + self.config.config['start_screen']['play_button'][
                                       'logo_margin_top'], 'Start Game', (0, 0, 0),
                                   pygame.font.Font(os.path.join(Path.assets_fonts_path, 'al-seana.ttf'), 30),
                                   self.start_game)
        self.quit_button = Button(config, 250, 50, None,
                                  self.start_button.rect.bottom + self.config.config['start_screen']['quit_button'][
                                      'play_margin_top'], 'Quit', (0, 0, 0),
                                  pygame.font.Font(os.path.join(Path.assets_fonts_path, 'al-seana.ttf'), 30),
                                  self.stop_game)

        game.buttons.add(self.start_button)
        game.buttons.add(self.quit_button)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.logo, self.logo_rect)
        self.start_button.draw(screen)
        self.quit_button.draw(screen)

    def update(self) -> None:
        self.start_button.update()
        self.quit_button.update()

    def start_game(self) -> None:
        game.state = MainGameState(self.config, game)

    def stop_game(self) -> None:
        print("Stop...")


class Jumper(pygame.sprite.Sprite):
    def __init__(self, config: Config):
        super().__init__()

        self.config = config

        self.image = pygame.image.load(
            os.path.join(Path.assets_images_path, self.config.config['main_game']['jumper']['image'])).convert_alpha()
        self.image = pygame.transform.scale(self.image, (
        self.config.config['main_game']['jumper']['width'], self.config.config['main_game']['jumper']['height']))
        self.rect = self.image.get_rect()

        center_x = self.config.config['main_game']['jumper']['position']['center_x']
        center_y = self.config.config['main_game']['jumper']['position']['center_y']

        if center_x:
            self.rect.centerx = self.config.config['screen']['width'] / 2
        else:
            self.rect.x = self.config.config['main_game']['jumper']['position']['margin_left']

        if center_y:
            self.rect.centery = self.config.config['screen']['height'] / 2
        else:
            self.rect.y = self.config.config['screen']['height'] - \
                          self.config.config['main_game']['jumper']['position']['margin_bottom']


class GreenPlatform(pygame.sprite.Sprite):
    def __init__(self, config: Config, width: int, height: int, x: int | None, y: int | None):
        super().__init__()

        self.config = config

        self.image = pygame.image.load(
            os.path.join(Path.assets_images_path,
                         self.config.config['main_game']['platform']['static']['image'])).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        if x is None:
            self.rect.x = self.config.config['screen']['width'] / 2 - width / 2

        if y is None:
            self.rect.y = self.config.config['screen']['height'] / 2 - height / 2
        else:
            self.rect.y = self.config.config['screen']['height'] - y

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        pass


class MainGameState(GameState):
    def __init__(self, config: Config, game: Game):
        super().__init__(config, game)

        self.config = config

        self.jumper = Jumper(self.config)

    def draw(self, screen):
        self.jumper.draw(screen)

    def update(self):
        self.jumper.update()

    def keystroke_left(self):
        print("Left Btn")

    def keystroke_right(self):
        print("Right Btn")

    def keystroke_space(self):
        print("Space Btn")

    def handle_events(self, event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.keystroke_left()
            elif event.key == pygame.K_RIGHT:
                self.keystroke_right()
            elif event.key == pygame.K_SPACE:
                self.keystroke_space()


if __name__ == '__main__':
    config = Config()
    game = Game(config)
    game.run()
