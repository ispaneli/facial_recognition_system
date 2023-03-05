from pathlib import Path

import certifi
from motor import motor_asyncio
from pyaml_env import parse_config


CONFIG_PATH = Path(__file__).parents[1] / "config.yaml"
CONFIG = parse_config(str(CONFIG_PATH))

_MONGO_CLIENT = motor_asyncio.AsyncIOMotorClient(
    CONFIG['db']['mongo_url'],
    tlsCAFile=certifi.where(),
    uuidRepresentation='standard',
    serverSelectionTimeoutMS=CONFIG['db']['timeout']
)
MONGO_DB = _MONGO_CLIENT.fr_system
