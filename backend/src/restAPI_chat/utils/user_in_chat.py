from fastapi import HTTPException

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.chat_base_model.model import Chats
from src.database import async_session_factory
from src.logging.setting import loggings

logger = loggings(__name__)

async def user_in_chat(chats_id, user_id) -> any:
    ''''проверяем есть ли пользователь в этом чате'''
    async with async_session_factory() as session:
        query = (
            select(Chats)
            .options(selectinload(Chats.users_chat))
            .filter_by(id=chats_id)
        )
        result = (await session.execute(query)).scalars().all()
        users_id_in_chat = [user.id for chat in result for user in chat.users_chat]
        logger.info('поиск выполнен')
    if not user_id in users_id_in_chat:  # проверяем есть ли пользователь отправляющий сообщение в этом чате
        raise HTTPException(status_code=402, detail='user is not found')
    return users_id_in_chat