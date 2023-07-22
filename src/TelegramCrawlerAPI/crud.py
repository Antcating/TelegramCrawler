import datetime
from re import A
from sqlalchemy.orm import Session

from . import schemas
from . import models
from ..constants import DATE_BREAK


def get_channel_by_id(db: Session, channel_id: int):
    return (
        db.query(models.TelegramChannel)
        .filter(models.TelegramChannel.id == channel_id)
        .first()
    )


def get_channel_by_username(db: Session, channel_username: str):
    return (
        db.query(models.TelegramChannel)
        .filter(models.TelegramChannel.username.ilike(f"%{channel_username}%"))
        .first()
    )


def get_channels_by_username(db: Session, channel_username: str, limit: int = 3):
    return (
        db.query(models.TelegramChannel)
        .filter(models.TelegramChannel.username.ilike(f"%{channel_username}%"))
        .limit(limit)
        .all()
    )


def get_channel_by_title(db: Session, channel_title: str):
    return (
        db.query(models.TelegramChannel)
        .filter(models.TelegramChannel.title.ilike(f"%{channel_title}%"))
        .first()
    )


def get_channels_by_title(db: Session, channel_title: str, limit: int = 3):
    return (
        db.query(models.TelegramChannel)
        .filter(models.TelegramChannel.title.ilike(f"%{channel_title}%"))
        .limit(limit)
        .all()
    )


def get_channel_connections_out(db: Session, channel_id: int, type: int):
    return (
        db.query(models.TelegramConnection)
        .filter(
            models.TelegramConnection.id_origin == channel_id, 
            models.TelegramConnection.type == type
        )
        .all()
    )


def get_channel_connections_in(db: Session, channel_id: int, type: int):
    return (
        db.query(models.TelegramConnection)
        .filter(
            models.TelegramConnection.id_destination == channel_id, 
            models.TelegramConnection.type == type
        )
        .all()
    )


def create_channel(db: Session, channel: schemas.Channel):
    db_channel = models.TelegramChannel(**channel.model_dump())
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    return db_channel


def create_connection(db: Session, connection: schemas.ConnectionCreate):
    db_channel_origin = get_channel_by_id(db, connection.id_origin)
    db_channel_destination = get_channel_by_id(db, connection.id_origin)

    if connection.date < DATE_BREAK:
        type = 0
    elif connection.date >= DATE_BREAK:
        type = 1
    if not db_channel_origin or not db_channel_destination:
        return None

    db_connection = models.TelegramConnection(
        id_origin=connection.id_origin,
        id_destination=connection.id_destination,
        strength=connection.strength,
        type=type,
    )
    db.add(db_connection)
    db.commit()
    db.refresh(db_connection)
    return db_connection


def delete_channel(db: Session, channel_id: schemas.Channel):
    channel = get_channel_by_id(channel_id)
    if channel is None: 
        return None
    list_conenctions = [
        get_channel_connections_in(db, channel_id, 0),
        get_channel_connections_out(db, channel_id, 0),
        get_channel_connections_in(db, channel_id, 1),
        get_channel_connections_out(db, channel_id, 1),
    ]
    if any(list_conenctions):
        return 'Connection'

    db.query(models.TelegramChannel).filter(
        models.TelegramChannel.id == channel_id
    ).delete()
    db.commit()
    return schemas.Deletion(ok=True)


def delete_connection(db: Session, id_origin: int, id_destination: int):
    db.query(models.TelegramConnection).filter(
        models.TelegramConnection.id_origin == id_origin,
        models.TelegramConnection.id_destination == id_destination
    ).delete()
    db.commit()
    return schemas.Deletion(ok=True)
