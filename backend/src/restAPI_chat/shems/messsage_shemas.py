from typing import Optional, List

from pydantic import BaseModel, Field, conlist

from src.attachment.schema import AttachmentItem

from datetime import datetime


# схемы валидации JSON объектов


class Message(BaseModel):
    type: str = Field(..., pattern="^(text|voice|video)$")
    message: str
    attachment: Optional[List[AttachmentItem]] = Field(default=None)


class Chats(BaseModel):
    chat_id: int
    message: Message


class UserMessage(BaseModel):
    chats: Chats

class GettingMessages(BaseModel):
    chat_id: int
    created_by: int
    message: str
    created_at: datetime
    attachment: Optional[List[AttachmentItem]] = Field(default=None)


