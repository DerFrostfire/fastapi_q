from pydantic import BaseModel


class AttachmentItem(BaseModel):
    name: str
    type: str
    file_id: str
