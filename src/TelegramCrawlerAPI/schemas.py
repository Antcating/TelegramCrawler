import datetime
from pydantic import BaseModel

class Channel(BaseModel):
    id: int
    username: str
    title: str
    date: datetime.datetime