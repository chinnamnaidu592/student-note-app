from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from database import SessionLocal,engine
from models import Base,NoteDB

app=FastAPI()

Base.metadata.create_all(
    bind=engine
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Note(BaseModel):

    name:str
    note:str


@app.get("/")
def home():

    return{
        "message":"Server running"
    }


@app.post("/add")
def add_note(data:Note):

    db=SessionLocal()

    item=NoteDB(
        name=data.name,
        note=data.note
    )

    db.add(item)

    db.commit()

    db.close()

    return{
        "message":"saved"
    }


@app.get("/notes")
def get_notes():

    db=SessionLocal()

    data=db.query(
        NoteDB
    ).all()

    result=[]

    for x in data:

        result.append({

            "id":x.id,
            "name":x.name,
            "note":x.note

        })

    db.close()

    return result


@app.delete("/delete/{id}")
def delete_note(id:int):

    db=SessionLocal()

    item=db.query(
        NoteDB
    ).filter(
        NoteDB.id==id
    ).first()

    if item:

        db.delete(item)

        db.commit()

    db.close()

    return{
        "message":"deleted"
    }

@app.put("/update/{id}")

def update_note(
    id:int,
    data:Note
):

    db=SessionLocal()

    item=db.query(
        NoteDB
    ).filter(
        NoteDB.id==id
    ).first()

    if item:

        item.name=data.name
        item.note=data.note

        db.commit()

    db.close()

    return{
        "message":"updated"
    }