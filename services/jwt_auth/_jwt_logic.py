import hashlib
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pyaml_env import parse_config


CONFIG = parse_config("config.yaml")
OAUTH2_SCHEME = OAuth2PasswordBearer(
    tokenUrl='/sign_in',
    scheme_name='JWT'
)


async def encode_password(login: str, password: str) -> str:
    """
    Encodes password.

    :param str login: The client whose password is being hashed. It's used as personal salt.
    :param str password: Password (or already password hash) that came from Client.
    :return: New hash of the password (or existing password hash).
    :rtype: str
    """
    total_salt = CONFIG['password']['hash_global_salt'] + login
    return hashlib.pbkdf2_hmac(
        CONFIG['password']['hash_function'],
        password.encode(),
        total_salt.encode(),
        CONFIG['password']['hash_complexity']
    ).hex()


async def verify_password(login: str, password: str, pwd_hash_from_db: str) -> bool:
    """
    Password verification.

    :param str login: The client whose password is being hashed. It's used as personal salt.
    :param str password: Password (or already password hash) that came from Client.
    :param str pwd_hash_from_db: Hash of real plain password from database.
    :return: Whether password has been verified or not.
    :rtype: bool
    """
    return pwd_hash_from_db == await encode_password(login, password)


async def _encode_token(login: str, token_type: str = 'access_token') -> dict[str, str | datetime]:
    """
    Creates encoded access or refresh token.

    :param str login: Who needs to generate a token.
    :param str token_type: The name of token to be generated:
                           'access_token' or 'refresh_token'
                           (default: 'access_token').
    :return: Generated token and expiration time as dictionary.
    :rtype: dict[str, str | datetime]
    """
    token_issued_time = datetime.now(tz=timezone.utc)
    token_life_time = timedelta(
        days=CONFIG['jwt'][token_type]['expire_days'],
        hours=CONFIG['jwt'][token_type]['expire_hours'],
        minutes=CONFIG['jwt'][token_type]['expire_minutes']
    )
    token_expiration_time = token_issued_time + token_life_time

    payload = {
        # Identifies the recipients that the JWT is intended for.
        'login': login,
        # Identifies the subject of the JWT.
        'sub': token_type,
        # Identifies the expiration time on and after which
        # the JWT must not be accepted for processing.
        'exp': int(token_expiration_time.timestamp()),
        # Identifies the time at which the JWT was issued.
        'iat': int(token_issued_time.timestamp())
    }
    token = jwt.encode(
        payload,
        CONFIG['jwt']['ssl_secret_key'],
        algorithm=CONFIG['jwt']['algorithm']
    )

    return {
        'token': token,
        'exp': token_expiration_time
    }


async def decode_token(token: str, token_type: str = 'access_token') -> dict[str, str | int]:
    """
    Decodes access or refresh token.

    :param str token: Access or refresh token.
    :param str token_type: The name of token to be generated:
                           'access_token' or 'refresh_token'
                           (default: 'access_token').
    :return: Payload of token.
    :rtype: dict[str, str | int]
    """
    try:
        payload = jwt.decode(
            token,
            CONFIG['jwt']['ssl_secret_key'],
            algorithms=[CONFIG['jwt']['algorithm']]
        )

        if payload['sub'] == token_type:
            return payload
        raise HTTPException(status_code=401, detail="The token has invalid type.")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="The token is expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="The token is invalid.")


async def generate_new_tokens(login: str) -> tuple[dict[str, str | datetime], dict[str, str | datetime]]:
    """
    Creates encoded access and refresh tokens.

    :param str login: Who needs to generate tokens.
    :return: Access and refresh tokens.
    :rtype: tuple[dict[str, str | datetime], dict[str, str | datetime]]
    """
    access_data = await _encode_token(login)
    refresh_data = await _encode_token(login, token_type='refresh_token')

    return access_data, refresh_data


async def get_current_client(access_token: str = Depends(OAUTH2_SCHEME)) -> dict[str, str | int]:
    """
    Returns data about current client, checks access JWT-token.

    :param access_token: Access JWT-token of current client.
    :return: Data about current client.
    :rtype: dict[str, str | int]
    """
    payload = await decode_token(access_token)
    return {'login': payload['login']}
