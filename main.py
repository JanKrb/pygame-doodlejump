import os
import json

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

config = Config()