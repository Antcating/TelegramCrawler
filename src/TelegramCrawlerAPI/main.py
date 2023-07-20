from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/channel_by_id/{channel_id}/", response_model=schemas.Channel)
def get_channel_by_id(channel_id: int, db: Session = Depends(get_db)):
    """Returns exact channel with given id

    Args:
        db (Session): SQLAlchemy Session
        channel_title (int): Channel id

    Returns:
        models.TelegramChannel: Returns single query channel result
    """
    db_channel = crud.get_channel_by_id(db, channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="No channel was found")
    return db_channel

@app.get("/channel_by_username/{channel_username}/", response_model=schemas.Channel)
def get_channel_by_username(channel_username: str, db: Session = Depends(get_db)):
    """Returns channel with given username (using ilike query)

    Args:
        db (Session): SQLAlchemy Session
        channel_username (str): Channel username

    Returns:
        models.TelegramChannel: Returns single query channel result
    """
    db_channel = crud.get_channel_by_username(db, channel_username)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="No channel was found")
    return db_channel

@app.get("/channels_by_username/{channel_username}/", response_model=list[schemas.Channel])
def get_channels_by_username(channel_username: str, db: Session = Depends(get_db), limit: int = 3):
    """Returns list of channels with similar to given username (using ilike query)

    Args:
        db (Session): SQLAlchemy Session
        channel_username (str): Channel username
        limis: (int): Limits number of channels in output

    Returns:
        list(models.TelegramChannel): Returns list of channels from query result
    """
    db_channels = crud.get_channels_by_username(db, channel_username, limit)
    if db_channels is None:
        raise HTTPException(status_code=404, detail="No channel was found")
    return db_channels

@app.get("/channel_by_title/{channel_title}/", response_model=schemas.Channel)
def get_channel_by_title(channel_title: str, db: Session = Depends(get_db)):
    """Returns channel with given title (using ilike query)

    Args:
        db (Session): SQLAlchemy Session
        channel_title (str): Channel title

    Returns:
        models.TelegramChannel: Returns single query channel result
    """
    db_channel = crud.get_channel_by_title(db, channel_title)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="No channel was found")
    return db_channel

@app.get("/channels_by_title/{channel_title}/", response_model=list[schemas.Channel])
def get_channels_by_title(channel_title: str, db: Session = Depends(get_db), limit: int = 3):
    """Returns list of channels with similar to given title (using ilike query)

    Args:
        db (Session): SQLAlchemy Session
        channel_username (str): Channel username
        limis: (int): Limits number of channels in output

    Returns:
        list(models.TelegramChannel): Returns list of channels from query result
    """
    db_channels = crud.get_channels_by_title(db, channel_title, limit)
    if db_channels is None:
        raise HTTPException(status_code=404, detail="No channel was found")
    return db_channels

@app.get("/channel_connections_out_after/{channel_id}/", response_model=list[schemas.Connection])
def get_channel_connections_out_after(channel_id: int, db: Session = Depends(get_db)):
    """Returns list of Connections going out 
        after the split from channel provided by id

    Args:
        db (Session): SQLAlchemy Session
        channel_title (int): Channel id

    Returns:
        _type_: _description_
    """
    db_connections = crud.get_channel_connections_out_after(db, channel_id)
    if db_connections is None:
        raise HTTPException(status_code=404, detail="No connections was found")
    return db_connections

@app.get("/channel_connections_in_after/{channel_id}/", response_model=list[schemas.Connection])
def get_channel_connections_in_after(channel_id: int, db: Session = Depends(get_db)):
    """Returns list of Connections going in 
        after the split from channel provided by id

    Args:
        db (Session): SQLAlchemy Session
        channel_title (int): Channel id

    Returns:
        _type_: _description_
    """
    db_connections = crud.get_channel_connections_in_after(db, channel_id)
    if db_connections is None:
        raise HTTPException(status_code=404, detail="No connections was found")
    return db_connections

@app.get("/channel_connections_out_before/{channel_id}/", response_model=list[schemas.Connection])
def get_channel_connections_out_before(channel_id: int, db: Session = Depends(get_db)):
    """Returns list of Connections going out 
        before the split from channel provided by id

    Args:
        db (Session): SQLAlchemy Session
        channel_title (int): Channel id

    Returns:
        _type_: _description_
    """
    db_connections = crud.get_channel_connections_out_before(db, channel_id)
    if db_connections is None:
        raise HTTPException(status_code=404, detail="No connections was found")
    return db_connections

@app.get("/channel_connections_in_before/{channel_id}/", response_model=list[schemas.Connection])
def get_channel_connections_in_before(channel_id: int, db: Session = Depends(get_db)):
    """Returns list of Connections going in 
        before the split from channel provided by id

    Args:
        db (Session): SQLAlchemy Session
        channel_title (int): Channel id

    Returns:
        _type_: _description_
    """
    db_connections = crud.get_channel_connections_in_before(db, channel_id)
    if db_connections is None:
        raise HTTPException(status_code=404, detail="No connections was found")
    return db_connections
