from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.auth.auth_shema import AuthMe

import jwt
from src.auth.auth import auth
from src.chat_base_model.model import Users
from src.config import setting
from src.logging.setting import loggings

from src.database import get_async_session

logger = loggings(__name__)

router = APIRouter(
    prefix='/auth',
    tags=['Модуль авторизации для websocet']
)

@router.post('/auth_ws', response_class=JSONResponse, summary='получение токена для вебсокета')
async def create_one_time_token(quniq_id = Depends(auth.get_user_id_and_name_api)):
    user_id = await auth.curent_user_id(quniq_id)
    logger.info('user received')
    payload = {
        'user_id': quniq_id['quniq_id'],
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }

    token = jwt.encode(payload, key=setting.SECRET_KEY, algorithm='HS256',)
    return {'ticket': token}


@router.get('/auth_me', response_model=AuthMe, summary='получение информации о себе')
async def auth_me(
        quniq = Depends(auth.get_user_id_and_name_api),
        session: AsyncSession = Depends(get_async_session)
                    ) -> Any:
    ''''
    получение информации о себе происходит по токену авторизции для приложений
    '''

    user_id = await auth.curent_user_id(quniq)
    qury = select(Users).filter_by(id=user_id)
    result = (await session.execute(qury)).scalar_one()
    return AuthMe(**quniq, **result.__dict__)
