from typing import Optional, List

from pydantic import BaseModel, Field, constr

from src.attachment.schema import AttachmentItem


# class MessageDTO(BaseModel):
#     type: str = Field(..., pattern="^(text|audio|video)$")
#     message: str
#     # attachment: Optional[List[AttachmentItem]]
#
# class Chats(BaseModel):
#     chat_id: int
#     message: MessageDTO
#
# class UserMessage(BaseModel):
#     chats: Chats

class TypeMessage(BaseModel):
    type: str = Field(..., pattern="^(text|audio|video)$")


# Схема для подписки на канал

class Сhannel(BaseModel):
    channel: List[constr(pattern="^(chat|user)\\.\\d+$")]
    action: str = Field(..., pattern="^(add|del)$")


class Subscription(BaseModel):
    subscriptions: Сhannel
