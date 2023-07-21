import datetime
from sqlite3 import Connection
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

@app.get("/channel_connections_in/{channel_id}/{type}", response_model=list[schemas.Connection])
def get_channel_connections_in(channel_id: int, type: int, db: Session = Depends(get_db)):
    """Returns list of Connections going in 
        after the split from channel provided by id

    Args:
        db (Session): SQLAlchemy Session
        channel_title (int): Channel id

    Returns:
        _type_: _description_
    """
    db_connections = crud.get_channel_connections_in(db, channel_id, type)
    if db_connections is None:
        raise HTTPException(status_code=404, detail="No connections was found")
    return db_connections

@app.get("/channel_connections_out/{channel_id}/{type}", response_model=list[schemas.Connection])
def get_channel_connections_out(channel_id: int, type: int, db: Session = Depends(get_db)):
    """Returns list of Connections going out 
        before the split from channel provided by id

    Args:
        db (Session): SQLAlchemy Session
        channel_title (int): Channel id

    Returns:
        _type_: _description_
    """
    db_connections = crud.get_channel_connections_out(db, channel_id, type)
    if db_connections is None:
        raise HTTPException(status_code=404, detail="No connections was found")
    return db_connections

@app.post("/channel/", response_model=schemas.Channel)
def create_channel(channel: schemas.Channel, db: Session = Depends(get_db)):
    db_channel = crud.get_channel_by_id(db, channel.id)
    if db_channel:
        raise HTTPException(status_code=400, detail='Channel already exists')
    return crud.create_channel(db, channel)

@app.post("/connection/", response_model=schemas.Connection)
def create_connection(connection: schemas.ConnectionCreate, db: Session = Depends(get_db)):
    db_connection = crud.create_connection(db, connection)
    if not db_connection:
        raise HTTPException(status_code=403, detail='At least one of the channels doesn`t exist')
    return db_connection

@app.delete("/connection_after/", response_model=schemas.Deletion)
def delete_connection(id_origin: int, id_destination: int, db: Session = Depends(get_db)):

    return crud.delete_connection(db, id_origin, id_destination)

@app.delete("/channel/", response_model=schemas.Deletion)
def delete_channel(channel_id: int, db: Session = Depends(get_db)):
    db_channel = crud.get_channel_by_id(db, channel_id)
    if not db_channel:
        raise HTTPException(status_code=404, detail='No channel was found')
    return crud.delete_channel(db, channel_id)