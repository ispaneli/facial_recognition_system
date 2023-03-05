import uvicorn
from fastapi import FastAPI

from src.facial_recognition_system.config import CONFIG
from src.facial_recognition_system.employee import EMPLOYEE_ROUTER
from src.facial_recognition_system.face_recognition import FACE_ROUTER
from src.facial_recognition_system.jwt_auth import create_clients, JWT_ROUTER


FRS_APP = FastAPI(title="Facial Recognition System (FastAPI + OpenCV)")
for router in (JWT_ROUTER, EMPLOYEE_ROUTER, FACE_ROUTER):
    FRS_APP.include_router(router)


if __name__ == '__main__':
    create_clients()

    uvicorn.run(
        'main:FRS_APP',
        host=CONFIG['fastapi_service']['host'],
        port=CONFIG['fastapi_service']['port'],
        reload=CONFIG['fastapi_service']['reload'],
        workers=CONFIG['fastapi_service']['workers_count']
    )
