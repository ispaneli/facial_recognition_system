from pathlib import Path

from pyaml_env import parse_config


CONFIG_PATH = Path(__file__).parents[2] / "config.yaml"
CONFIG = parse_config(str(CONFIG_PATH))

LOG_CONFIG_PATH = str(Path(__file__).parents[2] / "logging.ini")
