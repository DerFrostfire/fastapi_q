from datetime import datetime, timezone

from src.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship, query
from sqlalchemy import Text, ForeignKey, DateTime, String, func, UniqueConstraint
import enum
from sqlalchemy.dialects.postgresql import ENUM as PgEnum


class MessageTypeEnum(enum.Enum):
    text = "text"
    voice = "voice"
    video = "video"

class UserStatusEnum(enum.Enum):
    offline = "offline"
    online  = "online"


class Users(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    id_quniq: Mapped[int] = mapped_column(unique=True)
    user_name: Mapped[str] = mapped_column(nullable=True)
    update_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    status: Mapped[UserStatusEnum] = mapped_column(PgEnum(UserStatusEnum), server_default="offline")
    online_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    message_to_chat: Mapped[list['Messages']] = relationship(back_populates='created_by_user')
    chats_user: Mapped[list['Chats']] = relationship(back_populates='users_chat', secondary='chat_users')



class Messages(Base):
    __tablename__ = 'message'
    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[str] = mapped_column(Text, nullable=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey('chat.id'))
    message_type: Mapped[MessageTypeEnum]
    created_by: Mapped[int] = mapped_column(ForeignKey('user.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    created_by_user = relationship("Users", back_populates="message_to_chat")
    chats = relationship("Chats", back_populates="message_to_chat")
    attachments = relationship("Attachments", back_populates="message")

class Attachments(Base):
    __tablename__ = 'attachment'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    path: Mapped[str] = mapped_column(unique=True)
    type: Mapped[str]
    message_id: Mapped[int] = mapped_column(ForeignKey('message.id'))
    message = relationship("Messages", back_populates="attachments")
    UniqueConstraint('path', name='uc_path')
              
class Chats(Base):
    __tablename__ = 'chat'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(20), nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey('user.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now
    )
    users_chat = relationship("Users", back_populates="chats_user", secondary="chat_users")
    message_to_chat = relationship("Messages", back_populates="chats")


class ChatsUsers(Base):
    __tablename__ = 'chat_users'

    chat_id: Mapped[int] = mapped_column(ForeignKey('chat.id'), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
