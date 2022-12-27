import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pyaml_env import parse_config

from models import MONGO_DB
from models.valid import RefreshTokenModel

from ._jwt_logic import (
    encode_password,
    verify_password,
    decode_token,
    generate_new_tokens,
    get_current_client
)


CONFIG_PATH = Path(__file__).parents[2] / "config.yaml"
CONFIG = parse_config(str(CONFIG_PATH))
JWT_ROUTER = APIRouter(tags=['JWT Authentication'])


@JWT_ROUTER.post('/sign_in')
async def sign_in(client: OAuth2PasswordRequestForm = Depends()) -> dict[str, str]:
    """
    Authentication of an existing client equipment by login and password.

    :param OAuth2PasswordRequestForm client: Data of the client equipment.
    :return: Access and refresh tokens of the client equipment.
    :rtype: dict[str, str]
    """
    existing_client = await MONGO_DB.clients.find_one({'login': client.username})
    if not existing_client:
        raise HTTPException(status_code=401, detail="The client wasn't found.")

    if not await verify_password(client.username, client.password, existing_client['password']):
        raise HTTPException(status_code=401, detail="Invalid password.")

    access_data, refresh_data = await generate_new_tokens(client.username)
    await MONGO_DB.tokens.insert_one(refresh_data)

    return {
        'access_token': access_data['token'],
        'refresh_token': refresh_data['token']
    }


@JWT_ROUTER.post('/refresh_tokens')
async def refresh_tokens(refresh_model: RefreshTokenModel) -> dict[str, str]:
    """
    Refreshes access and refresh tokens of user model.

    :param RefreshTokenModel refresh_model: Model with actual refresh token of user model.
    :return: New access and new refresh tokens.
    :rtype: dict[str, str]
    """
    payload = await decode_token(refresh_model.refresh_token, token_type='refresh_token')
    token_from_db = await MONGO_DB.tokens.find_one({'token': refresh_model.refresh_token})

    if not token_from_db:
        raise HTTPException(status_code=401, detail="The refresh token wasn't found.")
    await MONGO_DB.tokens.delete_one({'_id': token_from_db['_id']})

    access_data, refresh_data = await generate_new_tokens(payload['login'])
    await MONGO_DB.tokens.insert_one(refresh_data)
    return {
        'access_token': access_data['token'],
        'refresh_token': refresh_data['token']
    }


@JWT_ROUTER.post('/test_private_method')
async def test_private_method(
        client: dict[str, str] = Depends(get_current_client)
) -> dict[str, bool]:
    return {'auth_status': True}


async def create_config_clients(clear_db: bool = True) -> None:
    """
    Creates all clients from config.yaml.

    :param bool clear_db: If True, all data will be deleted.
    :return: None
    """
    if clear_db:
        collections = await MONGO_DB.list_collection_names()
        for collection_name in collections:
            await MONGO_DB.drop_collection(collection_name)

    for client in CONFIG['clients']:
        client.update({
            '_id': uuid.uuid4(),
            'password': await encode_password(client['login'], client['password'])
        })
        await MONGO_DB.clients.insert_one(client)


async def expired_tokens_killer() -> None:
    """
    Removes all expired tokens in database.

    :return: None
    """
    await MONGO_DB.tokens.delete_many({
        'exp': {
            '$lte': datetime.now(tz=timezone.utc)
        }
    })
