from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    password: str


class NoteCreate(BaseModel):
    title: str
    content: str


class ShareNote(BaseModel):
    share_with_email: str