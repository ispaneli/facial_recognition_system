from pydantic import BaseModel


class RefreshTokenModel(BaseModel):
    """
    Validation of refresh token that come from Client.
    """
    refresh_token: str
