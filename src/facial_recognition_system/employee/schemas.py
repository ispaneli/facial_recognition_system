from datetime import date

from pydantic import BaseModel, Field


class EmployeeModel(BaseModel):
    """
    Validation of new employee that come from Client.
    """
    first_name: str
    second_name: str

    date_of_birth: date = None
    phone: int = None
    email: str = None
    home_address: str = None

    position: str = None
    other_info: str = None


class UpdateEmployeeModel(EmployeeModel):
    """
    Validation of existing employee that come from Client.
    """
    id: str = Field(alias="_id")
