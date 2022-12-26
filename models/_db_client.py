import certifi
from motor import motor_asyncio
from pyaml_env import parse_config


CONFIG = parse_config("config.yaml")

_MONGO_CLIENT = motor_asyncio.AsyncIOMotorClient(
    CONFIG['db']['mongo_url'],
    tlsCAFile=certifi.where(),
    uuidRepresentation='standard',
    serverSelectionTimeoutMS=CONFIG['db']['timeout']
)
MONGO_DB = _MONGO_CLIENT.fr_system
