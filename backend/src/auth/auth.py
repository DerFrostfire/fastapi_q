from typing import Optional, Tuple

import aiohttp
from aiohttp import ClientError
import jwt
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import setting
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from fastapi.websockets import WebSocket

from sqlalchemy import select

from starlette import status

from src.chat_base_model.model import Users
from src.database import async_session_factory, get_async_session

from src.logging.setting import loggings

logger = loggings(__name__)

class Auth:
    _URL_QUNIQ = setting.URL_UNIQUE
    api_key_header = APIKeyHeader(name="Authorization")
    @staticmethod
    async def authentification(
            token,
    ):
        try:
            logger.info('token processing')
            decoded= jwt.decode(token, setting.SECRET_KEY, algorithms=["HS256"])
            if decoded:
                async with async_session_factory() as session:
                    query = select(Users).filter_by(id_quniq=decoded['user_id'])
                    result = (await session.execute(query)).scalar_one()
                    if result.id:
                        return (True, result.id)
                    else:
                        return False

        except jwt.ExpiredSignatureError:
            logger.error("token has expired")
        except jwt.InvalidTokenError:
            logger.error("Token is invalid")
        except NoResultFound:
            logger.error("User not found in the database")
            raise HTTPException(status_code=404, detail="User not found")
        except KeyError:
            logger.error("User not found in the database")
            raise HTTPException(status_code=401, detail="Authentication error: invalid token")



    # для HTTP запросов
    async def get_user_id_and_name_api(self, api_key: str = Depends(api_key_header)):
        headers = {'Authorization': f'Bearer {api_key}'}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self._URL_QUNIQ, headers=headers, timeout=5) as response:
                    if response.status != 200:
                        raise HTTPException(status_code=response.status, detail="Ошибка при обращении к серверу")
                    user = await response.json()
                    if "id" not in user:
                        raise HTTPException(status_code=401, detail="Ошибка аутентификации")
                    user['quniq_id'] = user['id']
                    del user['id']
                    logger.info(f'пришел юзер {user}')
                    return (user)
        except TimeoutError:
            logger.error(TimeoutError)
            raise HTTPException(status_code=500, detail='нет подключения к серверу')
        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def curent_user_id(user_quniq: Tuple[int, str]):
        async with async_session_factory() as session:
            async with session.begin():
                query = select(Users).filter_by(id_quniq=user_quniq['quniq_id'])
                result = await session.execute(query)
                user = result.scalars().first()
                logger.info('user updated')
                if user is None:
                    user_id_qu = Users(id_quniq=user_quniq['quniq_id'], user_name=user_quniq['name'])
                    session.add(user_id_qu)
                    user_id = user_id_qu.id
                    await session.commit()
                    logger.info('user added')
                    return user_id
                else:
                    user.user_name = user_quniq['name']
                    await session.flush()
                    return user.id


auth = Auth()
