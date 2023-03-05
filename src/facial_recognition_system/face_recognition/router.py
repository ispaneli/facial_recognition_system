import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    UploadFile,
    File
)
from pyaml_env import parse_config

from src.facial_recognition_system.database import MONGO_DB
from src.facial_recognition_system.jwt_auth import get_current_client

from .dependencies import encode_img_stream, get_employee_by_img


CONFIG_PATH = Path(__file__).parents[2] / "config.yaml"
CONFIG = parse_config(str(CONFIG_PATH))
ROUTER = APIRouter(tags=['Face recognition'], prefix="/biometrics")


@ROUTER.post("/{employee_id}")
async def create(
        employee_id: str,
        photos: list[UploadFile] = File(...),
        client: dict[str, str] = Depends(get_current_client)
) -> dict[str, str]:
    """
    Adds new encodings of biometrics to the employee data.

    :param str employee_id: ID of the employee.
    :param list[UploadFile] photos: Uploaded photos of the employee.
    :param dict[str, str] client: Data about the client who made the request.
    :return: ID of the employee.
    :rtype: None
    """
    employee = await MONGO_DB.employees.find_one({'_id': uuid.UUID(employee_id)})
    if not employee:
        raise HTTPException(status_code=401, detail="Invalid ID of the employee.")

    new_encodings = [
        await encode_img_stream(photo.file, model_tag=CONFIG['model']['model_tag'])
        for photo in photos
    ]

    existing_biometrics = await MONGO_DB.biometrics.find_one(
        {'_id': uuid.UUID(employee_id)}
    )
    if existing_biometrics:
        existing_biometrics['encodings'] += new_encodings
        await MONGO_DB.biometrics.replace_one(
            {'_id': uuid.UUID(employee_id)},
            existing_biometrics
        )
    else:
        await MONGO_DB.biometrics.insert_one({
            '_id': uuid.UUID(employee_id),
            'encodings': new_encodings
        })

    return {'_id': employee_id}


@ROUTER.patch("/{employee_id}")
async def update(
        employee_id: str,
        photos: list[UploadFile] = File(...),
        client: dict[str, str] = Depends(get_current_client)
):
    """
    Replaces new encodings of biometrics to the employee data.

    :param str employee_id: ID of the employee.
    :param list[UploadFile] photos: Uploaded photos of the employee.
    :param dict[str, str] client: Data about the client who made the request.
    :return: ID of the employee.
    :rtype: None
    """
    employee = await MONGO_DB.employees.find_one({'_id': uuid.UUID(employee_id)})
    if not employee:
        raise HTTPException(status_code=401, detail="Invalid ID of the employee.")

    new_biometrics = {
        '_id': uuid.UUID(employee_id),
        'encodings': [
            await encode_img_stream(
                photo.file,
                model_tag=CONFIG['model']['model_tag']
            )
            for photo in photos
        ]
    }
    await MONGO_DB.biometrics.delete_one({'_id': uuid.UUID(employee_id)})
    await MONGO_DB.biometrics.insert_one(new_biometrics)

    return {'_id': employee_id}


@ROUTER.post("/")
async def find(
    photo: UploadFile = File(...),
    client: dict[str, str] = Depends(get_current_client)
) -> dict[str, str]:
    """
    Searches for the employee in database of biometrics.

    :param UploadFile photo: Uploaded photo of the employee (or not).
    :param dict[str, str] client: Data about the client who made the request.
    :return: ID of the employee.
    :rtype: dict[str, str]
    """
    employee_id = await get_employee_by_img(
        photo.file,
        model_tag=CONFIG['model']['model_tag']
    )
    if employee_id:
        return {'_id': employee_id}

    raise HTTPException(status_code=401, detail="The employee wasn't found.")



