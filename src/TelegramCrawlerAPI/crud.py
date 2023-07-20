from sqlalchemy.orm import Session

from . import models

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

def get_channels_by_username(db: Session, channel_username: str, limit: int = 3):
    """Returns list of channels with similar to given username (using ilike query)

    Args:
        db (Session): SQLAlchemy Session
        channel_username (str): Channel username
        limis: (int): Limits number of channels in output

    Returns:
        list(models.TelegramChannel): Returns list of channels from query result
    """
    return (
        db.query(models.TelegramChannel)
        .filter(models.TelegramChannel.username.ilike(f'%{channel_username}%'))
        .limit(limit)
        .all()
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


def get_channels_by_title(db: Session, channel_title: str, limit: int = 3):
    """Returns list of channels with similar to given title (using ilike query)

    Args:
        db (Session): SQLAlchemy Session
        channel_username (str): Channel username
        limis: (int): Limits number of channels in output

    Returns:
        list(models.TelegramChannel): Returns list of channels from query result
    """
    return (
        db.query(models.TelegramChannel)
        .filter(models.TelegramChannel.title.ilike(f'%{channel_title}%'))
        .limit(limit)
        .all()
    )

def get_channel_connections_out_after(db: Session, channel_id: int):
    return (
        db.query(models.TelegramConnection_after)
        .filter(models.TelegramConnection_after.id_origin == channel_id)
        .all()
    )

def get_channel_connections_in_after(db: Session, channel_id: int):
    return (
        db.query(models.TelegramConnection_after)
        .filter(models.TelegramConnection_after.id_destination == channel_id)
        .all()
    )

def get_channel_connections_out_before(db: Session, channel_id: int):
    return (
        db.query(models.TelegramConnection_before)
        .filter(models.TelegramConnection_before.id_origin == channel_id)
        .all()
    )

def get_channel_connections_in_before(db: Session, channel_id: int):
    return (
        db.query(models.TelegramConnection_before)
        .filter(models.TelegramConnection_before.id_destination == channel_id)
        .all()
    )