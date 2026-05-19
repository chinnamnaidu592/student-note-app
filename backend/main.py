from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from database import SessionLocal,engine
from models import Base,NoteDB

from passlib.context import CryptContext
from models import UserDB

from jose import jwt
from datetime import datetime,timedelta

from fastapi import Header
from jose import JWTError

app=FastAPI()

pwd=CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

SECRET_KEY="mysecret123"

ALGORITHM="HS256"

def create_token(username):

    expire=datetime.utcnow()+timedelta(
        hours=1
    )

    data={

        "sub":username,

        "exp":expire

    }

    return jwt.encode(
        data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def get_current_user(token:str):

    try:

        data=jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username=data["sub"]

        return username

    except JWTError:

        return None

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

class User(BaseModel):

    username:str
    password:str


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
def get_notes(token:str=Header(default=None)):

    username=get_current_user(
        token
    )

    if not username:

        return{
            "message":"invalid token"
        }

    db=SessionLocal()

    notes=db.query(
        NoteDB
    ).all()

    db.close()

    return notes


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

@app.post("/signup")

def signup(data:User):

    db=SessionLocal()

    check=db.query(
        UserDB
    ).filter(
        UserDB.username==data.username
    ).first()

    if check:

        db.close()

        return{
            "message":"username already exists"
        }

    hashed=pwd.hash(
        data.password
    )

    user=UserDB(

        username=data.username,

        password=hashed

    )

    db.add(user)

    db.commit()

    db.close()

    return{
        "message":"signup success"
    }

@app.post("/login")

@app.post("/login")

def login(data:User):

    db=SessionLocal()

    user=db.query(
        UserDB
    ).filter(
        UserDB.username==data.username
    ).first()

    if not user:

        db.close()

        return{
            "message":"user not found"
        }

    if not pwd.verify(
        data.password,
        user.password
    ):

        db.close()

        return{
            "message":"wrong password"
        }

    token=create_token(
        user.username
    )

    db.close()

    return{

        "token":token

    }