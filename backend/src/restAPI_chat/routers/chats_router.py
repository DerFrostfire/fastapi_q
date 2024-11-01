from typing import List, Any
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.restAPI_chat.shems.chats_shemas import ChatListGet, ChatUserIN, CreateChat
from sqlalchemy import select

from src.auth.auth import auth
from src.database import get_async_session
from src.chat_base_model.model import Users, Chats

from src.chat_base_model.model import ChatsUsers

from src.logging.setting import loggings

logger = loggings(__name__)

router = APIRouter(prefix='/user_chat', tags=['Операции с чатами'])


@router.get('/chat_list', response_model=List[ChatListGet], summary='получение списка чатов пользователя')
async def getting_a_list_of_chats(
        quniq_id=Depends(auth.get_user_id_and_name_api),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        user_id = await auth.curent_user_id(quniq_id)
        qery = select(Users).options(selectinload(Users.chats_user)).filter_by(id=user_id)
        result = (await session.execute(qery)).scalars().all()
        chat_list = [chat for user in result for chat in user.chats_user]
    except Exception as e:
        raise HTTPException(status_code=404, detail=e)
    return chat_list


@router.post('/add_to_chat', response_class=JSONResponse, summary='добавление собеседника в чат')
async def adding_a_user_to_chat(
        user_chat: ChatUserIN,
        quniq_id= Depends(auth.get_user_id_and_name_api),
        session: AsyncSession = Depends(get_async_session)
) -> Any:
    user_id = await auth.curent_user_id(quniq_id)
    query = select(Chats).options(selectinload(Chats.users_chat)).filter_by(id=user_chat.chat_id)
    result = (await session.execute(query)).scalars().all()
    autors_in_chat = [chat.created_by for chat in result]
    logger.info(f'autor {autors_in_chat}')
    if not user_id in autors_in_chat:
        raise HTTPException(status_code=402, detail='the user is not the author of the chat')
    #поиск пользователя
    query = select(Users).filter_by(id=user_chat.user_id)
    try:
        result = (await session.execute(query)).scalar_one()
        add_user_to_chat = ChatsUsers(chat_id=user_chat.chat_id, user_id=result.id)
        session.add(add_user_to_chat)
        await session.commit()
    except Exception as e:
        return JSONResponse(e)
    except NoResultFound:
        return {'error': 'user no found'}

    return {'status': 'complite'}



@router.post('/create_chat',response_model= CreateChat, summary='создание чата')
async def crete_chat(title: str,
                     session: AsyncSession = Depends(get_async_session),
                     quniq_id=Depends(auth.get_user_id_and_name_api),
) -> Any:
    """
        Создает новый чат в базе данных.
        - **title**: Имя чата или c кем ведется переписка.
        """
    user_id = await auth.curent_user_id(quniq_id)
    chat = Chats(created_by=user_id, title=title)
    session.add(chat)
    await session.flush()
    chat_users = ChatsUsers(chat_id=chat.id,user_id=user_id)
    session.add(chat_users)
    await session.commit()
    await session.refresh(chat)
    logger.info('status: complit')
    return {"id": chat.id, "title": chat.title}


