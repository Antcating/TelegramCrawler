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
        list[schemas.Connection]: Connections object from pydantic
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
        list[schemas.Connection]: Connections object from pydantic
    """
    db_connections = crud.get_channel_connections_out(db, channel_id, type)
    if db_connections is None:
        raise HTTPException(status_code=404, detail="No connections was found")
    return db_connections

@app.post("/channel/", response_model=schemas.Channel)
def create_channel(channel: schemas.Channel, db: Session = Depends(get_db)):
    """Creates channel in DB

    Args:
        channel (schemas.Channel): Channel object from pydantic
        db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).

    Raises:
        HTTPException: Returns status_code 400 if channel already exists 

    Returns:
        schemas.Channel: Returns created channel
    """
    db_channel = crud.get_channel_by_id(db, channel.id)
    if db_channel:
        raise HTTPException(status_code=400, detail='Channel already exists')
    return crud.create_channel(db, channel)

@app.post("/connection/", response_model=schemas.Connection)
def create_connection(connection: schemas.ConnectionCreate, db: Session = Depends(get_db)):
    """Creates conection using IDs of the channels

    Args:
        connection (schemas.ConnectionCreate): Connection object from pydantic
        db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).

    Raises:
        HTTPException: returns status_code 403 if one of channel IDs doesn't exists in DB 

    Returns:
        schemas.Connection: Created Connection object from pydantic
    """
    db_connection = crud.create_connection(db, connection)
    if not db_connection:
        raise HTTPException(status_code=403, detail='At least one of the channels doesn`t exist')
    return db_connection

@app.patch("/connection/", response_model=schemas.Success)
def update_connection(id_origin: int, id_destination: int, type: int, db: Session = Depends(get_db)):
    db_connection = crud.update_connection(db, id_origin, id_destination, type)
    if not db_connection:
        raise HTTPException(status_code=404, detail='No connection between provided channels')
    return db_connection

@app.get('/connection/', response_model=schemas.Connection)
def get_connection(id_origin: int, id_destination: int, type: int, db: Session = Depends(get_db)):
    db_connection = crud.get_connection(db, id_origin, id_destination, type)
    if not db_connection:
        raise HTTPException(status_code=404, detail='No connection between provided channels')
    return db_connection

@app.delete("/connection/", response_model=schemas.Success)
def delete_connection(id_origin: int, id_destination: int, db: Session = Depends(get_db)):
    """Deletes connection from DB (both before and after)

    Args:
        id_origin (int): ID of channel from which connections are going
        id_destination (int): ID of channel to which connections are going
        db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).

    Returns:
        schemas.Deletion: returns ok status using pydantic schema
    """
    return crud.delete_connection(db, id_origin, id_destination)

@app.delete("/channel/", response_model=schemas.Success)
def delete_channel(channel_id: int, db: Session = Depends(get_db)):
    """Deletes channel

    Args:
        channel_id (int): ID of channel to delete
        db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).

    Raises:
        HTTPException: returns status_code 403 if channel with given ID has existing connections
        HTTPException: returns status_code 404 if channel with given ID does not exist

    Returns:
        schemas.Deletion: returns OK status of the process
    """
    db_status = crud.get_channel_by_id(db, channel_id)
    if not db_status:
        raise HTTPException(status_code=404, detail='Channel with this ID does not exist')
    if db_status == 'Connection':
        raise HTTPException(status_code=403, detail='Channel with this ID has existing connections')
    return crud.delete_channel(db, channel_id)

@app.get('/queue', response_model=schemas.Queue)
def get_last_in_queue(db: Session = Depends(get_db)):
    db_queue = crud.get_last_in_queue(db)
    if not db_queue:
        raise HTTPException(status_code=404, detail='No channels in queue')
    return db_queue

@app.post('/queue', response_model=schemas.Queue)
def add_to_queue(queue_element: schemas.QueueCreate, db: Session = Depends(get_db)):
    db_queue = crud.add_to_queue(db, queue_element)
    if db_queue is None:
        raise HTTPException(status_code=403, detail='This channel is already in the queue!')
    return db_queue

@app.delete('/queue', response_model=schemas.Success)
def delete_from_queue(channel_id: int, db: Session = Depends(get_db)):
    db_status = crud.delete_from_queue(db, channel_id)
    if db_status is None:
        raise HTTPException(status_code=404, detail='There is no channel with provided ID in queue')
    return db_status