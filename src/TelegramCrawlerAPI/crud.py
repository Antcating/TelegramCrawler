import datetime
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
            models.TelegramConnection.type == type,
        )
        .all()
    )


def get_channel_connections_in(db: Session, channel_id: int, type: int):
    return (
        db.query(models.TelegramConnection)
        .filter(
            models.TelegramConnection.id_destination == channel_id,
            models.TelegramConnection.type == type,
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


def update_connection(db: Session, id_origin: int, id_destination: int, type: int):
    db_connection = get_connection(db, id_origin, id_destination, type)
    if db_connection is None:
        return None
    db_connection = db.query(models.TelegramConnection).filter_by(
        id_origin=id_origin, id_destination=id_destination, type=type
    ).update(
        {
            models.TelegramConnection.strength: models.TelegramConnection.strength + 1,
        }
    )
    db.commit()
    return schemas.Success(ok=True)

def get_connection(db: Session, id_origin: int, id_destination: int, type: int):
    return (
        db.query(models.TelegramConnection)
        .filter(
            models.TelegramConnection.id_origin == id_origin,
            models.TelegramConnection.id_destination == id_destination,
            models.TelegramConnection.type == type,
        )
        .first()
    )


def delete_channel(db: Session, channel_id: schemas.Channel):
    channel = get_channel_by_id(db, channel_id)
    if channel is None:
        return None
    list_conenctions = [
        get_channel_connections_in(db, channel_id, 0),
        get_channel_connections_out(db, channel_id, 0),
        get_channel_connections_in(db, channel_id, 1),
        get_channel_connections_out(db, channel_id, 1),
    ]
    if any(list_conenctions):
        return "Connection"

    db.query(models.TelegramChannel).filter(
        models.TelegramChannel.id == channel_id
    ).delete()
    db.commit()
    return schemas.Success(ok=True)


def delete_connection(db: Session, id_origin: int, id_destination: int):
    db.query(models.TelegramConnection).filter(
        models.TelegramConnection.id_origin == id_origin,
        models.TelegramConnection.id_destination == id_destination,
    ).delete()
    db.commit()
    return schemas.Success(ok=True)


def get_last_in_queue(db: Session):
    return (
        db.query(models.TelegramQueue)
        .order_by(models.TelegramQueue.date)
        .limit(1)
        .first()
    )


def get_from_queue(db: Session, channel_id: int):
    return (
        db.query(models.TelegramQueue)
        .filter(models.TelegramQueue.id == channel_id)
        .first()
    )


def add_to_queue(db: Session, queue_element: schemas.QueueCreate):
    db_in_queue = get_from_queue(db, queue_element.id)
    if db_in_queue:
        return None
    db_queue = models.TelegramQueue(**queue_element.model_dump())
    db.add(db_queue)
    db.commit()
    db.refresh(db_queue)
    return db_queue


def delete_from_queue(db: Session, channel_id: int):
    db_in_queue = get_from_queue(db, channel_id)
    if db_in_queue is None:
        return None
    db.query(models.TelegramQueue).filter(
        models.TelegramQueue.id == channel_id
    ).delete()
    db.commit()
    return schemas.Success(ok=True)
