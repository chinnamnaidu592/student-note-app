from sqlalchemy import Column,Integer,String
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