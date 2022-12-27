import asyncio

import uvicorn
from fastapi import FastAPI
from pyaml_env import parse_config

from services.jwt_auth import JWT_ROUTER, create_config_clients
from services.face_auth import FR_ROUTER


CONFIG = parse_config("config.yaml")
FRS_APP = FastAPI(title="Facial Recognition System (FastAPI + OpenCV)")
FRS_APP.include_router(JWT_ROUTER)
FRS_APP.include_router(FR_ROUTER)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(create_config_clients(
        clear_db=CONFIG['fastapi_service']['clear_db']
    ))
    loop.close()

    uvicorn.run(
        'main:FRS_APP',
        host=CONFIG['fastapi_service']['host'],
        port=CONFIG['fastapi_service']['port'],
        reload=CONFIG['fastapi_service']['reload'],
        workers=CONFIG['fastapi_service']['workers_count']
    )
