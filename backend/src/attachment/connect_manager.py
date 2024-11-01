from uuid import uuid4

from sqlalchemy import insert, select
from src.chat_base_model.model import Attachments
from src.attachment.schema import AttachmentItem
from sqlalchemy.exc import IntegrityError
from typing import List, Dict, Tuple
from src.logging.setting import loggings
import os
from src.config import BASE_DIR, ATTACHMENT_DIR
from src.database import async_session_factory

logger = loggings(__name__)
class AttachmentManager:

    @staticmethod
    async def generate_new_properties(attachment: List[AttachmentItem]) -> Tuple[List[AttachmentItem], List[str]]:
      path_list = []
      for item in attachment:
        item.file_id = uuid4().hex + os.path.splitext(item.name)[1]
        path_list.append(os.path.join(ATTACHMENT_DIR, item.file_id))
      return path_list
    
    @staticmethod
    async def add_attachment_to_db(message_id: int, attachment: List[AttachmentItem]) -> None:
      logger.info(f'Запись в бд вложений сообщения с id={message_id}')
      async with async_session_factory() as session:   
        for item in attachment:
          record = Attachments(
            message_id=message_id, 
            name=item.name, 
            type=item.type, 
            path=os.path.join(ATTACHMENT_DIR, item.file_id)
          )
          session.add(record)
        await session.commit()


manager = AttachmentManager()