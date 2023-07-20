from sqlalchemy.orm import Session

import models


def get_channel_by_username(db: Session, channel_username: str):
    """Returns channel with given username (using ilike query)

    Args:
        db (Session): SQLAlchemy Session
        channel_username (str): Channel username

    Returns:
        models.TelegramChannel: Returns single query channel result
    """
    return (
        db.query(models.TelegramChannel)
        .filter(models.TelegramChannel.username.ilike(f'%{channel_username}%'))
        .first()
    )


def get_channel_by_title(db: Session, channel_title: str):
    """Returns channel with given title (using ilike query)

    Args:
        db (Session): SQLAlchemy Session
        channel_title (str): Channel title

    Returns:
        models.TelegramChannel: Returns single query channel result
    """
    return (
        db.query(models.TelegramChannel)
        .filter(models.TelegramChannel.title.ilike(f'%{channel_title}%'))
        .first()
    )


def get_channel_by_id(db: Session, channel_id: int):
    """Returns exact channel with given id

    Args:
        db (Session): SQLAlchemy Session
        channel_title (int): Channel id

    Returns:
        models.TelegramChannel: Returns single query channel result
    """
    return (
        db.query(models.TelegramChannel)
        .filter(models.TelegramChannel.id == channel_id)
        .first()
    )


def get_channels(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TelegramChannel).offset(skip).limit(limit).all()
