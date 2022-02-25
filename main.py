import os
import json
import pygame

class Path:
    runtime_path = os.path.dirname(os.path.realpath(__file__))

    assets_path = os.path.join(runtime_path, 'assets')
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
        self.background = pygame.image.load(os.path.join(Path.assets_images_path, config.config['images']['background'])).convert()
        self.background = pygame.transform.scale(self.background, (config.config['screen']['width'], config.config['screen']['height']))
    
    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.background, (0, 0))
    
    def update(self, config: Config) -> None:
        pass

class Game:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.screen = pygame.display.set_mode((self.config.config['screen']['width'], self.config.config['screen']['height']))
        pygame.display.set_caption(self.config.config['screen']['title'])
        self.clock = pygame.time.Clock()
        self.running = True

        self.background = Background(config)
    
    def run(self) -> None:
        while self.running:
            self.clock.tick(self.config.config['screen']['fps'])
            self.events()
            self.update()
            self.draw()
    
    def events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
    
    def update(self) -> None:
        self.background.update(self.config)
    
    def draw(self) -> None:
        self.background.draw(self.screen)
        pygame.display.flip()


if __name__ == '__main__':
    config = Config()
    game = Game(config)
    game.run()