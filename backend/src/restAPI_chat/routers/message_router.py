from typing import Any

from dns.e164 import query
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_async_session, async_session_factory
from src.restAPI_chat.shems.messsage_shemas import UserMessage, Message, GettingMessages

from src.chat_base_model.model import Chats, Users, Messages

from src.auth.auth import auth

from src.wschat.conect_manager import manager

from src.logging.setting import loggings

logger = loggings(__name__)

from typing import List

from src.attachment.schema import AttachmentItem

router = APIRouter(
    tags=['операции с сообщениями'],
    prefix='/message'
)


@router.post('/message', response_class=JSONResponse, summary='отправка сообщений')
async def creation_and_sending(chat: UserMessage,
                               quniq_id=Depends(auth.get_user_id_and_name_api),
                               ) -> Any:
    try:
        logger.info(f'сообщение джейсон {chat}')
        user_id = await auth.curent_user_id(quniq_id)
        await manager.broadcast(chat, add_to_db=True, user_id=user_id)
        logger.info('выполнена отправка сообщения')
        return {'status': 'complite'}
    except Exception as e:
        logger.error(f'ошибка отправки сообения {e}')

# создание API-эндпоинта для получения сообщений пользователя
@router.get('message/{chat_id}', response_model=List[GettingMessages], summary='Получение сообщений чата')
async def get_chat_messages(
        chat_id: int,
        quniq_id: str = Depends(auth.get_user_id_and_name_api),
        session: AsyncSession = Depends(get_async_session)) -> Any:
    try:
        user_id = await auth.curent_user_id(quniq_id)
        logger.info(f"Получение сообщений для чата с ID {chat_id} пользователем ID {user_id}")


        query = (
                select(Messages)
                .filter(Messages.chat_id == chat_id)
                .order_by(Messages.created_at.asc())
                .options(selectinload(Messages.attachments))
            )
        result = await session.execute(query)
        message_list = result.scalars().all()

            # Создаем список сообщений для данного чата

        return message_list

    except Exception as e:
        logger.error(f'Ошибка при получении сообщений для чата {chat_id}: {e}')
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
