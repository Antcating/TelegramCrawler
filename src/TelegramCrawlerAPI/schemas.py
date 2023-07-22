import datetime
from pydantic import BaseModel, validator

class Channel(BaseModel):
    id: int
    username: str
    title: str
    date: datetime.datetime

    # @validator(date, pre=True)
    # def date_validate(cls, date):
    #     return datetime.datetime.fro
    
class Connection(BaseModel):
    id_origin: int
    id_destination: int
    strength: int
    type: int = 1

class ConnectionCreate(Connection):
    date: datetime.datetime

class Queue(BaseModel):
    id: int

class QueueCreate(Queue):
    date: datetime.datetime

class Success(BaseModel):
    ok: bool
    details: str | None = None