# Imports
from sqlalchemy import ForeignKey, Integer, Sequence, DateTime
from sqlalchemy import String, Column, Table, MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import mapped_column

from sqlalchemy import create_engine

meta = MetaData()

class Base(DeclarativeBase):
    pass

class TelegramChannel(Base):
    __tablename__ = "TelegramChannels"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String())
    username: Mapped[str] = mapped_column(String(32))
    date: Mapped[str] = mapped_column(DateTime())

    def __repr__(self) -> str:
        return f"Channel(id={self.id!r}, username={self.username!r}, title={self.title!r}, description={self.description!r}, subscribers={self.subscribers!r}, posts={self.posts!r})"

class TelegramConnection_before(Base):
    __tablename__ = 'TelegramConnections_before'

    id: Mapped[int] = mapped_column(Sequence("id", start=1), primary_key=True)
    id_origin: Mapped[int] = mapped_column(ForeignKey("TelegramChannels.id"))
    id_destination: Mapped[int] = mapped_column(ForeignKey("TelegramChannels.id"))

    strength: Mapped[int] = mapped_column(Integer())
    type: Mapped[int] = mapped_column(Integer())

class TelegramConnection_after(Base):
    __tablename__ = 'TelegramConnections_after'

    id: Mapped[int] = mapped_column(Sequence("id", start=1), primary_key=True)
    id_origin: Mapped[int] = mapped_column(ForeignKey("TelegramChannels.id"))
    id_destination: Mapped[int] = mapped_column(ForeignKey("TelegramChannels.id"))

    strength: Mapped[int] = mapped_column(Integer())
    type: Mapped[int] = mapped_column(Integer())

class TelegramQueue(Base):
    __tablename__ = 'TelegramQueue'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[str] = mapped_column(DateTime())