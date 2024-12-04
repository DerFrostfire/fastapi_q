from fastapi import FastAPI
from src.wschat.router import router as ws
from src.restAPI_chat.routers.user_rout import router as user
from src.restAPI_chat.routers.chats_router import router as chat
from src.auth.auth_router import router as auth_ws
from src.attachment.router import router as attachment
from src.restAPI_chat.routers.message_router import router as message
from src.config import setting


app = FastAPI(root_path=setting.ROOT_PATH)

endpoints = [ws, user, auth_ws, attachment, message]

for endpoint in endpoints:
    app.include_router(endpoint)

