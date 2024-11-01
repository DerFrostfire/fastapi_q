from fastapi import APIRouter, HTTPException
from fastapi import WebSocket
from src.auth.auth import auth
from src.wschat.conect_manager import manager
from src.logging.setting import loggings
from pydantic import ValidationError
from src.wschat.shema import Subscription
from starlette.websockets import WebSocketDisconnect

logger = loggings(__name__)

router = APIRouter(
    prefix='/chat',
    tags=["Chat"]
)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, ticket: str=None):
    logger.info('socket connection')
    result = await auth.authentification(ticket)
    if result[0]:
        logger.info(f'token accept')
        await manager.connect(websocket, result[1])
        try:
            while True:
                data = await websocket.receive_json()
                logger.info('Получен запрос на подписку, валидируем данные...')
                message = Subscription(**data)
                channel = message.subscriptions.channel
                if message.subscriptions.action == 'add':
                    await manager.creation_and_connect_to_channel(channel,websocket, user_id=result[1])
                    logger.info(f' Cписок соединений обновлен:\n {manager.channel_connections}')
                elif message.subscriptions.action == 'del':
                    await manager.disconnect_from_the_channel(websocket, channel)

        except WebSocketDisconnect:

            logger.info(f'Клиент закрыл соединение {websocket}')
            try:
                await manager.disconnect(websocket)
                logger.info(f'функция дисконект отработла успешно')
            except Exception as e:
                logger.error(f'соединение закрыто с ошибкой соещинения: {e}')
        except ValidationError as e:
            logger.error(f"Ошибка валидации, разрыв соединения: {e}")
            await manager.disconnect(websocket)
        except Exception as e:
            logger.fatal(e)
            await manager.disconnect(websocket)
            raise HTTPException(status_code=400, detail=e)
