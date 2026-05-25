from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, NoteDB, UserDB

from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

app = FastAPI()

pwd = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

SECRET_KEY = "mysecret123"
ALGORITHM = "HS256"


# ---------------- JWT ----------------

def create_token(username):
    expire = datetime.utcnow() + timedelta(hours=1)

    data = {
        "sub": username,
        "exp": expire
    }

    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str):

    if not token:
        return None

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return data["sub"]

    except JWTError:
        return None


# ---------------- DB INIT ----------------

Base.metadata.create_all(bind=engine)


# ---------------- CORS ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- MODELS ----------------

class Note(BaseModel):
    name: str
    note: str


class User(BaseModel):
    username: str
    password: str


# ---------------- ROUTES ----------------

@app.get("/")
def home():
    return {"message": "Server running"}


# ---------------- ADD NOTE ----------------

@app.post("/add")
def add_note(data: Note, token: str = Header(default=None)):

    username = get_current_user(token)

    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    db = SessionLocal()

    note = NoteDB(
        name=data.name,
        note=data.note,
        username=username
    )

    db.add(note)
    db.commit()
    db.close()

    return {"message": "note added"}


# ---------------- GET NOTES (USER SPECIFIC) ----------------

@app.get("/notes")
def get_notes(token: str = Header(default=None)):

    username = get_current_user(token)

    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    db = SessionLocal()

    notes = db.query(NoteDB).filter(
        NoteDB.username == username
    ).all()

    result = [
        {
            "id": n.id,
            "name": n.name,
            "note": n.note
        }
        for n in notes
    ]

    db.close()
    return result


# ---------------- DELETE NOTE ----------------

@app.delete("/delete/{id}")
def delete_note(id: int, token: str = Header(default=None)):

    username = get_current_user(token)

    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    db = SessionLocal()

    item = db.query(NoteDB).filter(
        NoteDB.id == id,
        NoteDB.username == username
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(item)
    db.commit()
    db.close()

    return {"message": "deleted"}


# ---------------- UPDATE NOTE ----------------

@app.put("/update/{id}")
def update_note(id: int, data: Note, token: str = Header(default=None)):

    username = get_current_user(token)

    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    db = SessionLocal()

    item = db.query(NoteDB).filter(
        NoteDB.id == id,
        NoteDB.username == username
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Note not found")

    item.name = data.name
    item.note = data.note

    db.commit()
    db.close()

    return {"message": "updated"}


# ---------------- SIGNUP ----------------

@app.post("/signup")
def signup(data: User):

    db = SessionLocal()

    check = db.query(UserDB).filter(
        UserDB.username == data.username
    ).first()

    if check:
        db.close()
        raise HTTPException(status_code=400, detail="username already exists")

    hashed = pwd.hash(data.password)

    user = UserDB(
        username=data.username,
        password=hashed
    )

    db.add(user)
    db.commit()
    db.close()

    return {"message": "signup success"}


# ---------------- LOGIN ----------------

@app.post("/login")
def login(data: User):

    db = SessionLocal()

    user = db.query(UserDB).filter(
        UserDB.username == data.username
    ).first()

    if not user:
        db.close()
        raise HTTPException(status_code=404, detail="user not found")

    if not pwd.verify(data.password, user.password):
        db.close()
        raise HTTPException(status_code=401, detail="wrong password")

    token = create_token(user.username)

    db.close()

    return {"token": token}