from pydantic import EmailStr, BaseModel, HttpUrl
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    email: EmailStr
    first_name: str
    last_name: str
    avatar: str

class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    avatar: HttpUrl

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    avatar: HttpUrl | None = None
