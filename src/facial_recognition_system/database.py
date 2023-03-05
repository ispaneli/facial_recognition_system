import certifi
from motor import motor_asyncio

from src.facial_recognition_system.config import CONFIG


_MONGO_CLIENT = motor_asyncio.AsyncIOMotorClient(
    CONFIG['db']['mongo_url'],
    tlsCAFile=certifi.where(),
    uuidRepresentation='standard',
    serverSelectionTimeoutMS=CONFIG['db']['timeout']
)
MONGO_DB = _MONGO_CLIENT.fr_system
