import sqlalchemy
from sqlalchemy.orm import sessionmaker, declarative_base

from config import DB_URI

engine = sqlalchemy.create_engine(DB_URI, echo=True)
Session = sessionmaker(bind=engine)

Base = declarative_base()
