from fastapi import FastAPI
import databases, sqlalchemy, datetime, uuid
from pydantic import BaseModel, Field
from typing import List, Optional
# Postgres database
DATABASE_URL = "postgresql://usertest:usertest222@127.0.0.1:5432/dbtest"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "py_users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String),
    sqlalchemy.Column("password", sqlalchemy.String),
    sqlalchemy.Column("first_name", sqlalchemy.String),
    sqlalchemy.Column("last_name", sqlalchemy.String),
    sqlalchemy.Column("gender", sqlalchemy.CHAR),
    sqlalchemy.Column("created_at", sqlalchemy.String),
    sqlalchemy.Column("status", sqlalchemy.CHAR),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL
)

metadata.create_all(engine)

# models
class UserList(BaseModel):
    id: str
    username: str
    password: Optional[str]
    first_name: str
    last_name: str
    gender: str
    created_at: str
    status: str

class UserEntry(BaseModel):
    username: str = Field(..., example="potinejj")
    password: str = Field(..., example="potinejj")
    first_name: str = Field(..., example="Potine")
    last_name: str = Field(..., example="Sambo")
    gender: str = Field(..., example="M")

class UserUpdate(BaseModel):
    id: str = Field(..., example="Enter your id")
    first_name: str = Field(..., example="Potine")
    last_name: str = Field(..., example="Sambo")
    gender: str = Field(..., example="M")
    status: str = Field(..., example="1")
app = FastAPI()
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get('/users', response_model=List[UserList])
async def find_all_users():
    query = users.select()
    return await database.fetch_all(query)

@app.post("/users", response_model=UserList)
async def register_user(user: UserEntry):
    gID = str(uuid.uuid1())
    gDate = str(datetime.datetime.now())
    query = users.insert().values(
        id = gID,
        username = user.username,
        password = user.password,
        first_name = user.first_name,
        last_name = user.last_name,
        gender = user.gender,
        created_at = gDate,
        status = "1"
    )

    await database.execute(query)
    return {
        "id": gID,
        **user.dict(),
        "created_at": gDate,
        "status": 1
    }


@app.get("/users/{userId}", response_model=UserList)
async def find_user_by_id(userId: str):
    query = users.select().where(users.c.id == userId)
    return await database.fetch_one(query)

@app.put("/users", response_model=UserList)
async def update_user(user: UserUpdate):
    gDate = str(datetime.datetime.now())
    query = users.update().\
        where(users.c.id == user.id).\
            values(
                first_name = user.first_name,
                last_name = user.last_name,
                gender = user.gender,
                status = user.status,
                created_at = gDate,
            )
    await database.execute(query)
    return await find_user_by_id(user.id)
