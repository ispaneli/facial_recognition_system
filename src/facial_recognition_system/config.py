from pathlib import Path

from pyaml_env import parse_config


CONFIG_PATH = Path(__file__).parents[2] / "config.yaml"
CONFIG = parse_config(str(CONFIG_PATH))
