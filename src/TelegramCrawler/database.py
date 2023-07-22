import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import configparser 
# Import config parser
config = configparser.ConfigParser()
config.sections()

config.read("config.ini")

SQLALCHEMY_DATABASE_URL = config["API"]["POSTGRESRW"]

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
