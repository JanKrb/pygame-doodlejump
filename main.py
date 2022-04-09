import os
import json
import random
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
        self.delta_time = 1.0 / self.config.config['screen']['fps']

        self.background = Background(config)
        self.buttons = pygame.sprite.Group()

        self.state = StartState(self.config, self)

        self.background_music = pygame.mixer.Sound(os.path.join(Path.assets_sounds_path, self.config.config['sounds']['background']))
        self.volume = self.config.config['sounds']['volume']
        pygame.mixer.Channel(0).set_volume(self.volume)
        pygame.mixer.Channel(0).play(self.background_music, loops=-1)

    def run(self) -> None:
        while self.running:
            self.events()
            self.update()
            self.draw()
            self.delta_time = self.clock.tick(self.config.config['screen']['fps'])

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
        self.music_button = Button(config, 250, 50, None,
                                  self.quit_button.rect.bottom + self.config.config['start_screen']['music_button'][
                                      'quit_margin_top'], 'Toggle Music', (0, 0, 0),
                                  pygame.font.Font(os.path.join(Path.assets_fonts_path, 'al-seana.ttf'), 30),
                                  self.toggle_music)

        game.buttons.add(self.start_button)
        game.buttons.add(self.quit_button)
        game.buttons.add(self.music_button)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.logo, self.logo_rect)
        self.start_button.draw(screen)
        self.quit_button.draw(screen)
        self.music_button.draw(screen)

    def update(self) -> None:
        self.start_button.update()
        self.quit_button.update()
        self.music_button.update()

    def start_game(self) -> None:
        game.state = MainGameState(self.config, game)

    def stop_game(self) -> None:
        self.game.running = False

    def toggle_music(self) -> None:
        if pygame.mixer.Channel(0).get_busy():
            pygame.mixer.Channel(0).stop()
        else:
            pygame.mixer.Channel(0).play(self.game.background_music, loops=-1)

class Jumper(pygame.sprite.Sprite):
    def __init__(self, config: Config, platforms: pygame.sprite.Group) -> None:
        super().__init__()

        self.config = config

        self.image = pygame.image.load(
            os.path.join(Path.assets_images_path, self.config.config['main_game']['jumper']['image'])).convert_alpha()
        self.image = pygame.transform.scale(self.image, (
            self.config.config['main_game']['jumper']['width'], self.config.config['main_game']['jumper']['height']))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.platforms = platforms

        center_x = self.config.config['main_game']['jumper']['position']['center_x']
        center_y = self.config.config['main_game']['jumper']['position']['center_y']

        self.position = pygame.Vector2(0, 0)

        if center_x:
            self.position[0] = self.config.config['screen']['width'] / 2
        else:
            self.position[0] = self.config.config['main_game']['jumper']['position']['margin_left']

        if center_y:
            self.position[1] = self.config.config['screen']['height'] / 2
        else:
            self.position[1] = self.config.config['screen']['height'] - \
                          self.config.config['main_game']['jumper']['position']['margin_bottom']

        self.jump_offsets = list(range(10, 0, -1))
        self.jumping = True
        self.jump_offset = 0
        self.jump_micro_timer = Timer(self.config.config['main_game']['jumper']['jump']['duration'], False)

        self.speed_x = 0  # Left < 0, Right > 0

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def jump(self):
        if self.jump_micro_timer.is_next_stop_reached() and self.jumping:
            self.position[1] -= self.config.config['main_game']['jumper']['jump']['gravity_up'] * self.jump_offsets[
                self.jump_offset] * game.delta_time
            self.jump_offset += 1

            if self.jump_offset >= len(self.jump_offsets):
                self.jump_offset = 0
                self.jumping = False

        if not self.jumping:
            collided_platforms = pygame.sprite.spritecollide(self, self.platforms, False, pygame.sprite.collide_mask)

            if len(collided_platforms) <= 0:
                self.position[1] += self.config.config['main_game']['jumper']['jump']['gravity_down'] * self.jump_offsets[
                    self.jump_offset] * game.delta_time
            else:
                self.position[1] = collided_platforms[0].rect.top - self.rect.height  # Teleport jumper on top of platform, it doesn't glitch inside
                self.jumping = True
                self.jump_offset = 0
        
    def update(self, *args, **kwargs):
        self.jump()

        if kwargs.get('update_vp', False):
            self.update_vp()
        elif kwargs.get('move_left', False):
            self.move_left(stop=kwargs.get('stop', False))
        elif kwargs.get('move_right', False):
            self.move_right(stop=kwargs.get('stop', False))
        elif kwargs.get('shoot', False):
            self.shoot()
        
        self.move()
    
    def move(self):
        self.position[0] += self.speed_x * game.delta_time

        self.rect.x = self.position[0]
        self.rect.y = self.position[1]
    
    def move_left(self, *args, **kwargs):
        if kwargs.get('stop', False):
            self.speed_x = 0
            return
        
        self.speed_x = -self.config.config['main_game']['jumper']['move_x_speed']

    def move_right(self, *args, **kwargs):
        if kwargs.get('stop', False):
            self.speed_x = 0
            return
        
        self.speed_x = self.config.config['main_game']['jumper']['move_x_speed']
    
    def shoot(self):
        print('shoot')
    
    def update_vp(self):
        self.position[1] += self.config.config['main_game']['vp_scrollspeed']
        self.rect.y = self.position[1]

class Platform(pygame.sprite.Sprite):
    def __init__(self, config: Config, width: int, height: int, x: int | None, y: int | None) -> None:
        super().__init__()

        self.config = config
        self.size = (width, height)

        self.image = pygame.image.load(
            os.path.join(Path.assets_images_path,
                         self.config.config['main_game']['platform']['static']['image'])).convert_alpha()
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        if x is None:
            self.rect.x = self.config.config['screen']['width'] / 2 - width / 2

        if y is None:
            self.rect.y = self.config.config['screen']['height'] / 2 - height / 2
        else:
            self.rect.y = self.config.config['screen']['height'] - y
    
    def reload_image(self, img: pygame.Surface):
        old_pos = self.rect.center
        self.image = img
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect()
        self.rect.center = old_pos
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self, *args, **kwargs):
        if kwargs.get('update_vp', False):
            self.update_vp()
    
    def update_vp(self):
        self.rect.y += self.config.config['main_game']['vp_scrollspeed']

class GreenPlatform(Platform):
    def __init__(self, config: Config, width: int, height: int, x: int | None, y: int | None):
        super().__init__(config, width, height, x, y)

class BluePlatform(Platform):
    def __init__(self, config: Config, width: int, height: int, x: int | None, y: int | None):
        super().__init__(config, width, height, x, y)
        self.reload_image(pygame.image.load(
            os.path.join(Path.assets_images_path,
                         self.config.config['main_game']['platform']['moving']['image'])).convert_alpha())
            

        self.moving_speed = random.uniform(
            self.config.config['main_game']['platform']['moving']['min_speed'],
            self.config.config['main_game']['platform']['moving']['max_speed']
        )
        self.moving_direction = -1 # < 0 left, > 0 right
    
    def update(self, *args, **kwargs):
        # Change direction
        if self.rect.x <= 0 or self.rect.x >= self.config.config['screen']['width'] - self.rect.width:
            self.moving_direction *= -1
        
        # Move
        self.rect.x += self.moving_direction * self.moving_speed * game.delta_time

class MainGameState(GameState):
    def __init__(self, config: Config, game: Game):
        super().__init__(config, game)

        self.config = config

        self.platforms = pygame.sprite.Group()
        self.points = 0
        self.vp_offset = 0

        start_platform = GreenPlatform(self.config,
                                       self.config.config['main_game']['jumper']['start_platform']['width'],
                                       self.config.config['main_game']['jumper']['start_platform']['height'],
                                       None,
                                       self.config.config['main_game']['jumper']['position']['margin_bottom'] -
                                       self.config.config['main_game']['jumper']['height'])

        for i in range(16):
            test_platform = GreenPlatform(self.config,
                                       self.config.config['main_game']['jumper']['start_platform']['width'],
                                       self.config.config['main_game']['jumper']['start_platform']['height'],
                                       None,
                                       self.config.config['main_game']['jumper']['position']['margin_bottom'] -
                                       self.config.config['main_game']['jumper']['height'] + 200 * i) 
            self.platforms.add(test_platform)
        """
        test_platform = BluePlatform(self.config,
                                       self.config.config['main_game']['jumper']['start_platform']['width'],
                                       self.config.config['main_game']['jumper']['start_platform']['height'],
                                       None,
                                       self.config.config['main_game']['jumper']['position']['margin_bottom'] -
                                       self.config.config['main_game']['jumper']['height'] + 200 * 2) 
        self.platforms.add(test_platform)
                  """                                                
        self.platforms.add(start_platform)

        self.jumper = Jumper(self.config, self.platforms)

        # Points
        self.render_points()
    
    def render_points(self):
        font = pygame.font.Font(os.path.join(Path.assets_fonts_path, 'al-seana.ttf'), 30)
        self.points_text = font.render(f"Points: {round(self.points)}", True, (0, 0, 0))
        self.points_text_rect = self.points_text.get_rect()
        self.points_text_rect.top = self.config.config['screen']['height'] - self.points_text_rect.height - 15
        self.points_text_rect.right = self.config.config['screen']['width'] - 15

    def draw(self, screen):
        self.jumper.draw(screen)
        self.platforms.draw(screen)
        screen.blit(self.points_text, self.points_text_rect)

    def move_viewport(self):
        if self.jumper.rect.top < 0:
            self.jumper.update(update_vp=True)
            self.platforms.update(update_vp=True)
            self.vp_offset += self.config.config['main_game']['vp_scrollspeed']

    def regenerate_platforms(self):
        # Spawn new platforms
        if len(self.platforms) < self.config.config['main_game']['platform']['max_platforms']:
            # New platform
            pass

        # Delete old platforms
        for platform in self.platforms.sprites():
            if platform.rect.top > self.config.config['screen']['height']:
                self.platforms.remove(platform)
        
    def init_gameover(self):
        if self.jumper.rect.top > self.config.config['screen']['height']:
            game.state = GameOverGameState(self.config, game, self.points)

    def update(self):
        self.move_viewport()
        self.regenerate_platforms()
        self.init_gameover()

        self.jumper.update()
        self.platforms.update()

        # Get points
        self.points = max(self.points, (self.vp_offset + self.jumper.rect.bottom) / 100)
        self.render_points()

    def keystroke_left(self, *args, **kwargs):
        if kwargs.get('stop', False):
            self.jumper.update(move_left=True, stop=True)
        else:
            self.jumper.update(move_left=True)

    def keystroke_right(self, *args, **kwargs):
        if kwargs.get('stop', False):
            self.jumper.update(move_right=True, stop=True)
        else:
            self.jumper.update(move_right=True)

    def keystroke_space(self):
        self.jumper.update(shoot=True)

    def handle_events(self, event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.keystroke_left()
            elif event.key == pygame.K_RIGHT:
                self.keystroke_right()
            elif event.key == pygame.K_SPACE:
                self.keystroke_space()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                self.keystroke_left(stop=True)
            elif event.key == pygame.K_RIGHT:
                self.keystroke_right(stop=True)
            elif event.key == pygame.K_SPACE:
                self.keystroke_space(stop=True)

class Highscore:
    def __init__(self, config: Config):
        self.config = config
        self.highscore_file = os.path.join(Path.runtime_path, self.config.config['highscore']['file'])
        self.highscore = self.load_highscore()
    
    def load_highscore(self) -> int:
        with open(self.highscore_file, 'r') as f:
            highscores = json.load(f)
            highscores.sort(reverse=True)
            
            return highscores[0]
    
    def write_highscore(self, points) -> int:
        with open(self.highscore_file, 'r+') as f:
            highscores = json.load(f)
            highscores.append(points)
            highscores.sort(reverse=True)
            highscores = highscores[:self.config.config['highscore']['max_highscores']]

            highscores = json.dumps(highscores)
            f.seek(0)
            f.write(highscores)
            f.close()
        return self.load_highscore()

class GameOverGameState(GameState):
    def __init__(self, config: Config, game: Game, points: float) -> None:
        self.config = config
        self.game = game
        self.points = points

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
        
        self.restart_button = Button(config, 250, 50, None,
                                   self.logo_rect.bottom + self.config.config['start_screen']['play_button'][
                                       'logo_margin_top'], 'Retry', (0, 0, 0),
                                   pygame.font.Font(os.path.join(Path.assets_fonts_path, 'al-seana.ttf'), 30),
                                   self.restart_game)
        self.quit_button = Button(config, 250, 50, None,
                                  self.restart_button.rect.bottom + self.config.config['start_screen']['quit_button'][
                                      'play_margin_top'], 'Quit', (0, 0, 0),
                                  pygame.font.Font(os.path.join(Path.assets_fonts_path, 'al-seana.ttf'), 30),
                                  self.stop_game)

        game.buttons.add(self.restart_button)
        game.buttons.add(self.quit_button)

        font = pygame.font.Font(os.path.join(Path.assets_fonts_path, 'al-seana.ttf'), 30)
        self.points_text = font.render(f'Points: {round(self.points)}', True, (0, 0, 0))
        self.points_text_rect = self.points_text.get_rect()
        self.points_text_rect.centerx = self.config.config['screen']['width'] / 2
        self.points_text_rect.centery = self.quit_button.rect.bottom + 100

        highscore_obj = Highscore(config)
        highscore = highscore_obj.write_highscore(self.points)

        self.highscore_text = font.render(f'Highscore: {round(highscore)}', True, (0, 0, 0))
        self.highscore_text_rect = self.highscore_text.get_rect()
        self.highscore_text_rect.centerx = self.config.config['screen']['width'] / 2
        self.highscore_text_rect.centery = self.points_text_rect.bottom + 50

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.logo, self.logo_rect)
        self.restart_button.draw(screen)
        self.quit_button.draw(screen)

        screen.blit(self.points_text, self.points_text_rect)
        screen.blit(self.highscore_text, self.highscore_text_rect)

    def update(self) -> None:
        self.restart_button.update()
        self.quit_button.update()

    def restart_game(self):
        game.state = MainGameState(self.config, game)
    
    def stop_game(self):
        self.game.running = False

if __name__ == '__main__':
    config = Config()
    game = Game(config)
    game.run()
