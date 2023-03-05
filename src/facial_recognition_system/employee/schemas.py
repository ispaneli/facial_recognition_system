from datetime import date

from pydantic import (
    BaseModel,
    Field,
    root_validator
)


class EmployeeModel(BaseModel):
    """
    Validation of new employee that come from Client.
    """
    first_name: str
    second_name: str

    date_of_birth: str | date = None
    phone: int = None
    email: str = None
    home_address: str = None

    position: str = None
    other_info: str = None

    @root_validator(pre=True)
    def root_validator(cls, values: dict[str, ...]) -> dict[str, ...]:
        """
        Root validation of object (validation begins with it).

        :param dict[str, ...] values: Values of all fields.
        :return: Values of all fields after validation.
        :rtype: dict[str, ...]
        """
        values['date_of_birth'] = str(values['date_of_birth'])
        return values


class UpdateEmployeeModel(EmployeeModel):
    """
    Validation of existing employee that come from Client.
    """
    id: str = Field(alias="_id")
