from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine

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
    db_channel = crud.get_channel_by_id(db, channel_id)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    return db_channel

@app.get("/channel_by_username/{channel_username}/", response_model=schemas.Channel)
def get_channel_by_username(channel_username: str, db: Session = Depends(get_db)):
    db_channel = crud.get_channel_by_username(db, channel_username)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    return db_channel

@app.get("/channel_by_title/{channel_title}/", response_model=schemas.Channel)
def get_channel_by_title(channel_title: str, db: Session = Depends(get_db)):
    db_channel = crud.get_channel_by_title(db, channel_title)
    if db_channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    return db_channel