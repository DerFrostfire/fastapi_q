from fastapi import APIRouter, Depends, File, UploadFile, HTTPException

from src.attachment.schema import AttachmentItem
from pydantic import conlist
from typing import List, Any

from src.attachment.utils import save_all_upload_files

from sqlalchemy.exc import NoResultFound
from src.auth.auth import auth
from uuid import uuid4
from fastapi.responses import FileResponse

from src.chat_base_model.model import Attachments
from src.database import get_async_session
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from src.attachment.connect_manager import manager as am
import os 
from src.config import ATTACHMENT_DIR
from src.logging.setting import loggings

logger = loggings(__name__)

router = APIRouter(
    tags=["Attachment"]
)


@router.post(
     "/attachment",
     summary="Загрузка вложений на сервер",
     response_model=List[AttachmentItem]
)
async def create_attachment(
                        files: conlist(item_type=UploadFile, max_length=10) = File(...),
                        session: AsyncSession = Depends(get_async_session),
                        quniq_id = Depends(auth.get_user_id_and_name_api)
                        ) -> Any:
    attachment = []
    path_list = []

    for file in files:
        file_id = uuid4().hex + os.path.splitext(file.filename)[1]
        path_list.append(os.path.join(ATTACHMENT_DIR, file_id))
        item = AttachmentItem( 
                name = file.filename,
                type = file.content_type,
                file_id = file_id
        )
        attachment.append(item)

    while True:
        query = exists(select(Attachments.path).where(Attachments.path.in_(path_list))).select()
        path_exist = (await session.execute(query)).scalar()
        if not path_exist:
            break
        logger.info('Найдено совпадение в бд path, генерация новых file_id, path...')
        attachment, path_list = am.generate_new_properties(attachment)

        
    await save_all_upload_files(files, path_list)

    return attachment

@router.get("/attachment", summary="Скачать вложение")
async def send_attachment(
                        file_id: str,
                        session: AsyncSession = Depends(get_async_session),
                        quniq_id = Depends(auth.get_user_id_and_name_api)
                        ):
    query = select(Attachments).filter_by(path=os.path.join(ATTACHMENT_DIR, file_id))
    try:
        logger.info(f'Поиск файла {file_id}')
        attachment = (await session.execute(query)).scalars().one()
        return FileResponse(
                    path=attachment.path,
                    media_type=attachment.type,
                    filename=attachment.name
                    )
    except NoResultFound:
        logger.error(f'Файл {file_id} не найден')
        raise HTTPException(status_code=404, detail='file not found')