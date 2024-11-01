from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import async_session_factory
from src.chat_base_model.model import Users
from src.logging.setting import loggings
logger = loggings(__name__)
class UsersCRUD():

    async def user_read(id):
       async with async_session_factory() as session:
           query = select(Users).filter_by(id=id)
           result = (await session.execute(query)).scalar_one()
           logger.info(f'получен круд запрос {result}')
           session.commit()
           return result
