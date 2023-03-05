import uuid

from fastapi import APIRouter, Depends, status

from src.facial_recognition_system.database import MONGO_DB
from src.facial_recognition_system.jwt_auth import get_current_client

from .schemas import EmployeeModel, UpdateEmployeeModel


ROUTER = APIRouter(tags=['Employees'], prefix="/employee")


@ROUTER.post("/")
async def create(
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


@ROUTER.get("/")
async def get_all(
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


@ROUTER.get("/{employee_id}")
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


@ROUTER.put("/")
async def update(
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
    await MONGO_DB.employees.replace_one(replacement, updated_employee_params)

    return {'_id': updated_employee.id}


@ROUTER.delete("/{employee_id}", status_code=status.HTTP_200_OK)
async def delete(
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