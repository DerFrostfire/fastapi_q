from datetime import datetime
from typing import List, Dict, Set
from fastapi import WebSocket, HTTPException
from sqlalchemy import select, insert, update
from sqlalchemy.orm import selectinload

from src.database import async_session_factory
from src.chat_base_model.model import Chats, Messages, Users
from src.restAPI_chat.CRUD.user import UsersCRUD
from src.restAPI_chat.utils.user_in_chat import user_in_chat
from src.wschat.shema import TypeMessage
from src.restAPI_chat.shems.messsage_shemas import UserMessage
from src.attachment.connect_manager import manager as AttachmentManager
from src.logging.setting import loggings
from src.chat_base_model.model import UserStatusEnum


logger = loggings(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List = []  # список подключенных абонентов(вебсокетов)
        self.channel_connections: Dict[str, Set[WebSocket]] = {}


    async def connect(self, websocket: WebSocket, user_id):  # функция добавленя абонента
        logger.info(f'{user_id} user connection')
        
        await websocket.accept()
        self.active_connections.append(websocket)
        await self.update_user_status(user_id, UserStatusEnum.online) #  апдейт статуса
        
# Удаление всех соединений из всех каналов
    async def disconnect(self, websocket: WebSocket, user_id):  # разьеденение
        try:
            for channel in self.channel_connections.values():
                logger.info(f'соединений ,было {channel}')
                channel.discard(websocket)
                logger.info(f'соединений стало {channel}')
            logger.info('соединение разорвано')
            self.active_connections.remove(websocket)
            await self.update_user_status(user_id, UserStatusEnum.offline) #  апдейт статуса
        except Exception as e:
            logger.error(f'ошибка удаления вебсокета: {e}')
        
    async def creation_and_connect_to_channel(self, channels:list, websocet: WebSocket, user_id):

        for channel in channels:
            channel_type = channel.split('.')[0]
            channel_id = int(channel.split('.')[1])
            try:
                if channel_type == 'user':
                    if user_id != channel_id:
                        logger.error('нет доступа')
                        continue
                elif channel_type == 'chat':
                    async with async_session_factory() as session:
                        query = select(Chats).filter(Chats.id == channel_id).options(selectinload(Chats.users_chat)).filter(Users.id == user_id)
                        result = (await session.execute(query)).scalar_one()
                    if not result:
                        logger.error('нет доступа')
                        continue
                else:
                    raise HTTPException(status_code=400, detail='Bad Request')
                res_channel = f'{channel_type}.{channel_id}'
                if not res_channel in self.channel_connections:
                    self.channel_connections[res_channel] = {websocet}
                    logger.info(f'Канал {res_channel} создан сокет {websocet}\n')
                else:
                    logger.info(f'Сокет {websocet} добавлен в канал {res_channel}')
                    self.channel_connections[res_channel].add(websocet)
            except Exception as e:
                logger.error(f'{self.channel_connections}')
                raise HTTPException(status_code=404, detail='Чат не найден')

# Удаление соединений из выбранных каналов(сокет(соединение) отписывается от каналов)
    async def disconnect_from_the_channel(self, websocket: WebSocket, channels: list):
        try:
            for channel in channels:
                if channel in self.channel_connections:
                    self.channel_connections[channel].remove(websocket)
                    logger.info(f'Сокет {websocket} успешно удален из канала {channel}\n')
                    await websocket.send_json(f"status: removal_from {channel} done")
                else:
                    logger.warning(f"Канал {channel} не найден в списке подключений сокета {websocket}")
                    continue
        except Exception as e:
            logger.error(f"Ошибка при попытке удалить websocket {websocket} из каналов {channels}: {e}")

    async def send_personal_message(self, message: str, websocket: WebSocket):  # функция отправки сообщения абоненту
        await websocket.send_text(message)

#Отправка сообщений в каналы
    async def broadcast(self,
                    json_message: UserMessage,
                    add_to_db: bool,
                    user_id: int,
                    ):
    # Парсим входное сообщение
        logger.info(f'джейсон получен')
        try:
            chats_id = json_message.chats.chat_id
            message = json_message.chats.message.message
            message_typ = json_message.chats.message.type
            attachment = json_message.chats.message.attachment
            logger.info('парсин входного json прошел удачно\n')
        except Exception as e:
            raise HTTPException(status_code=401, detail=e)

        try:
            # Находим пользователей чата
            users_id_in_chat = await user_in_chat(chats_id, user_id)
        except Exception as e:
            raise HTTPException(status_code=401, detail=e)
        try:
            if add_to_db:
                create_message = await self.add_message_to_db(chats_id, user_id, message, message_typ)
                if attachment:
                    logger.info(f'добавление {attachment} в бузу даных')
                    await AttachmentManager.add_attachment_to_db(create_message[0], attachment)
            for id in users_id_in_chat:
                if not self.channel_connections.get(f'user.{id}'):
                    logger.error(f'на канал user.{id} никто не подписан')
                    continue
                else:
                    websocet_to_channel_user =  self.channel_connections.get(f'user.{id}')
                    for ws in websocet_to_channel_user:
                        if not ws.client_state != 1:
                            logger.error(f"соединение не активно")
                            manager.channel_connections.get(f'user.{id}').remove(ws)
                            continue
                        attachment_json = [item.dict() for item in attachment] if attachment else None
                        message_time = await self.datetime_handler(create_message[1])
                        name = await UsersCRUD.user_read(user_id)
                        await ws.send_json(
                            {
                                'chat_id': chats_id,
                                'created_by': user_id,
                                'user_name': name.user_name,
                                'message': message,
                                'attachment': attachment_json,
                                'created_at':  message_time

                            }
                        )
                        logger.info('сообщение отправленно в канал user')
                if not self.channel_connections.get(f'chat.{chats_id}'):
                    logger.error(f'на канал chat.{chats_id} никто не подписан')
                    continue
                else:
                    websocet_chat_channel = self.channel_connections.get(f'chat.{chats_id}')
                    for ws in websocet_chat_channel:
                        await ws.send_json({'chat_id': chats_id, 'created_by': user_id, 'message': message})
                        logger.info('сообщение отправленно в канал chat')
        except Exception as e:
            logger.error(e)


    @staticmethod
    async def add_message_to_db(chat_id: int, user_id: int, message: str,
                                message_typ: TypeMessage):  # добаляем сообщения в базу данных Message
        async with async_session_factory() as session:
            stmt = insert(Messages).values(
                chat_id=chat_id,
                created_by=user_id,
                message=message,
                message_type=message_typ
            ).returning(Messages.id, Messages.created_at)
            result = await session.execute(stmt)

            await session.commit()
            create_message = result.first()
            logger.info(f'!!!! {create_message} сообщение добавлено в базу данных')
            return create_message
    @staticmethod
    async def datetime_handler(x):
        if isinstance(x, datetime):
            return x.isoformat()
        else:
            raise HTTPException(status_code=422, detail='неверный формат вермени')
    @staticmethod
    async def update_user_status(user_id, user_status):
        async with async_session_factory() as session:
            stmt = (
                update(Users).
                where(Users.id == user_id).
                values(status = user_status)
            )
            await session.execute(stmt)

manager = ConnectionManager()
