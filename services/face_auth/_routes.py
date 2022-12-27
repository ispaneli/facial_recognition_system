import uuid

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    UploadFile,
    File,
    status
)
from pyaml_env import parse_config

from models import MONGO_DB
from services.jwt_auth import get_current_client
from models.valid import EmployeeModel, UpdateEmployeeModel

from .processing import photo_stream_to_encoding, who_is_it


CONFIG = parse_config("config.yaml")
FR_ROUTER = APIRouter(tags=['Face recognition'])


@FR_ROUTER.post('/add_employee')
async def add_employee(
        employee: EmployeeModel,
        client: dict[str, str] = Depends(get_current_client)
) -> dict[str, str]:
    """
    Adds a new employee.

    :param EmployeeModel employee: Data of the new employee.
    :param dict[str, str] client: Data about the client who made the request.
    :return: ID of the new employee.
    :rtype: dict[str, str]
    """
    employee_params = employee.dict()
    employee_params['_id'] = uuid.uuid4()
    await MONGO_DB.employees.insert_one(employee_params)

    return {'_id': employee_params['_id']}


@FR_ROUTER.get('/get_employees')
async def get_employees(
        client: dict[str, str] = Depends(get_current_client)
) -> list[dict[str, ...]]:
    """
    Returns data about all employees

    :param dict[str, str] client: Data about the client who made the request.
    :return: Data about all employees.
    :rtype: list[dict[str, ...]]
    """
    return [
        employee
        async for employee in MONGO_DB.employees.find()
    ]


@FR_ROUTER.get('/get_employee/{employee_id}')  # +
async def get_employee(
        employee_id: str,
        client: dict[str, str] = Depends(get_current_client)
) -> dict[str, ...]:
    """
    Returns data about the employee.

    :param str employee_id: ID of the employee.
    :param dict[str, str] client: Data about the client who made the request.
    :return: Data about the employee.
    :rtype: dict[str, ...]
    """
    return await MONGO_DB.employees.find_one({'_id': uuid.UUID(employee_id)})


@FR_ROUTER.put('/update_employee')
async def update_employee(
        updated_employee: UpdateEmployeeModel,
        client: dict[str, str] = Depends(get_current_client)
) -> dict[str, str]:
    """
    Updates data about of the employee.

    :param UpdateEmployeeModel updated_employee: Updated data about the employee.
    :param dict[str, str] client: Data about the client who made the request.
    :return: ID of the updated employee.
    :rtype: dict[str, str]
    """
    replacement = {'_id': uuid.UUID(updated_employee.id)}
    updated_employee_params = updated_employee.dict(exclude={'id'})
    print(replacement, updated_employee_params)
    await MONGO_DB.employees.replace_one(replacement, updated_employee_params)
    return {'_id': updated_employee.id}


@FR_ROUTER.post('/add_employee_biometrics/{employee_id}')
async def add_employee_biometrics(
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
        await photo_stream_to_encoding(photo.file, model_tag=CONFIG['model']['model_tag'])
        for photo in photos
    ]

    existing_biometrics = await MONGO_DB.biometrics.find_one({'_id': uuid.UUID(employee_id)})
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


@FR_ROUTER.patch('/replace_employee_biometrics/{employee_id}')
async def replace_employee_biometrics(
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
            await photo_stream_to_encoding(photo.file, model_tag=CONFIG['model']['model_tag'])
            for photo in photos
        ]
    }
    await MONGO_DB.biometrics.delete_one({'_id': uuid.UUID(employee_id)})
    await MONGO_DB.biometrics.insert_one(new_biometrics)

    return {'_id': employee_id}


@FR_ROUTER.post('/find_employee_by_biometrics')
async def find_employee_by_biometrics(
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
    employee_id = await who_is_it(photo.file, model_tag=CONFIG['model']['model_tag'])
    if employee_id:
        return {'_id': employee_id}

    raise HTTPException(status_code=401, detail="The employee wasn't found.")


@FR_ROUTER.delete('/delete_employee/{employee_id}', status_code=status.HTTP_200_OK)
async def delete_employee(
        employee_id: str,
        client: dict[str, str] = Depends(get_current_client)
) -> None:
    """
    Deletes data about of the employee.

    :param str employee_id: ID of the employee.
    :param dict[str, str] client: Data about the client who made the request.
    :return: None
    """
    await MONGO_DB.employees.delete_one({'_id': uuid.UUID(employee_id)})
    await MONGO_DB.biometrics.delete_one({'_id': uuid.UUID(employee_id)})
