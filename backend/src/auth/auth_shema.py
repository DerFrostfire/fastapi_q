from pydantic import BaseModel


class AuthMe(BaseModel):
    id: int
    name: str
    phone: str
    email: str
    created_at: str
    updated_at: str
    nick: str
    quniq_id: int

