from typing import List

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, union_all

from src.auth.auth import auth
from src.database import get_async_session

from src.restAPI_chat.shems.user_rout_shema import UserGet, UserStatus

from src.chat_base_model.model import Users, Chats, ChatsUsers 

from aiohttp import ClientSession
from src.logging.setting import loggings


logger = loggings(__name__)

router = APIRouter(
    prefix='/user',
    tags=["Действия с пользователями"]
)


@router.get("/users", response_model=List[UserGet], summary='список пользователей ')
async def find_user(session: AsyncSession = Depends(get_async_session)):
    query = select(Users)
    result = await (session.execute(query))
    response = result.scalars().all()
    return response


@router.get('/users/{name}', response_model=List[UserGet], summary='поиск пользователей по имени')
async def find_user_to_quniq(name,
                             api_key: str = Depends(auth.api_key_header),
                             quniq_id: str = Depends(auth.get_user_id_and_name_api)):
    try:
        user_id = await auth.curent_user_id(quniq_id)
        headers = {'Authorization': f'Bearer {api_key}'}
        url = f'https://test.quniq.net/api/user?filter={name}'
        async with ClientSession() as client:
            async with client.get(url=url, timeout=5, headers=headers) as respons:
                if respons.status != 200:
                    logger.error("Ошибка при обращении к серверу")
                    raise HTTPException(status_code=respons.status, detail="Ошибка при обращении к серверу")
                user_list = await respons.json()
                logger.info(f'пришел джейсон по поиску {user_list}')
            return user_list['items']
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)

@router.get('/user_staus', response_model=List[UserStatus], summary='Получение статуса пользователя')
async def get_user_status(
            quniq_id=Depends(auth.get_user_id_and_name_api),
            session: AsyncSession = Depends(get_async_session)
            ):
    try: 
        curr_user = await auth.curent_user_id(quniq_id)
        private_chats_subquery = (
             select(ChatsUsers.user_id)
            .join(Chats, Chats.id == ChatsUsers.chat_id)
            .where(Chats.created_by == curr_user)
            .subquery()
        )
        group_chats_subquery = (
            select(ChatsUsers.user_id)
            .where(
                ChatsUsers.chat_id.in_(
                    select(ChatsUsers.chat_id)
                    .where(ChatsUsers.user_id == curr_user)
                )
            )
            .where(ChatsUsers.user_id != curr_user)
            .subquery()
        )
        combined_subquery = (
            union_all(
                select(private_chats_subquery.c.user_id),
                select(group_chats_subquery.c.user_id)
            )
            .subquery()
        )
        query = (
            select(Users.id, Users.status, Users.online_at)
            .where(Users.id.in_(combined_subquery))
        )
        result = (await session.execute(query)).fetchall()
    except Exception as e:
        raise HTTPException(status_code=404, detail=e)
    statuses =  []
    for user_id, status, online_at in result:
        item = UserStatus(user_id, status, online_at)
        statuses.append(item)
    return statuses