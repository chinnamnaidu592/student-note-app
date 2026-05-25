from sqlalchemy import Column, Integer, String
from database import Base


class NoteDB(Base):

    __tablename__="notes"

    id=Column(
        Integer,
        primary_key=True,
        index=True
    )

    name=Column(String)

    note=Column(String)
    
    username=Column(String)


class UserDB(Base):

    __tablename__="users"

    id=Column(
        Integer,
        primary_key=True,
        index=True
    )

    username=Column(
        String,
        unique=True
    )

    password=Column(String)

    