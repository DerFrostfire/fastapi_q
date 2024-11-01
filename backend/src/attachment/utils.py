from fastapi import File, UploadFile
from src.database import async_session_factory
from typing import List
import aiofiles
from src.logging.setting import loggings

logger = loggings(__name__)
async def save_upload_file(upload_files: List[UploadFile], paths: List[str]) -> None:
    for file, path in zip(upload_files, paths):
        logger.info(f'Записываем файл: {path}')
        async with aiofiles.open(path, 'wb') as out_file:
            while content := await file.read(1024*1024):  # читаем файл порциями по мегабайту
                await out_file.write(content)

