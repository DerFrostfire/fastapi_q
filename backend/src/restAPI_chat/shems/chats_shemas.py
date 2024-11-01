from pydantic import BaseModel


class ChatListGet(BaseModel):
    id: int
    title: str
    created_by: int

class ChatUserIN(BaseModel):
    user_id: int
    chat_id: int


class CreateChat(BaseModel):
    id: int
    title: str