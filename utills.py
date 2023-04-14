from fastapi import status
from fastapi.exceptions import HTTPException


def authorization_required(authorize):
    try:
        authorize.jwt_required()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
        ) from e
