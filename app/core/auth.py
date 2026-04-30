from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    # TODO: validar token JWT e retornar usuário de domínio
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
