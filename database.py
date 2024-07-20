# database.py
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone_number = Column(String)
    telegram_id = Column(String, unique=True)
    wallet_balance = Column(Float, default=0.0)

engine = create_engine('sqlite:///bot_database.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
