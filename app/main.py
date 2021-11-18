from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List
from passlib.context import CryptContext
import databases
import sqlalchemy
import datetime
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# PostgreSQL
user_db = 'postgres_user'
pass_db = 'python_test'
name_db = 'dbtest'
DATABASE_URL = 'postgresql://postgres:local@localhost:5432/dbtest'
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# Modelando o banco de dados
users = sqlalchemy.Table(
    "usuarios",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column('username', sqlalchemy.String),
    sqlalchemy.Column('password', sqlalchemy.String),
    sqlalchemy.Column('nome', sqlalchemy.String),
    sqlalchemy.Column('sobrenome', sqlalchemy.String),
    sqlalchemy.Column('sexo', sqlalchemy.CHAR),
    sqlalchemy.Column('create_at', sqlalchemy.String),
    sqlalchemy.Column('status', sqlalchemy.CHAR),
)

# Criando a engine
engine = sqlalchemy.create_engine(
    DATABASE_URL
)
metadata.create_all(engine)


# Models
class UserList(BaseModel):
    id: str
    username: str
    password: str
    nome: str
    sobrenome: str
    sexo: str
    create_at: str
    status: str


class UserEntry(BaseModel):
    username: str = Field(..., example="edkami")
    password: str = Field(..., example="edkami")
    nome: str = Field(..., example="Eduardo")
    sobrenome: str = Field(..., example="Kami")
    sexo: str = Field(..., example="M")


class UserUpdate(BaseModel):
    id: str = Field(..., example='Informe seu id')
    nome: str = Field(..., example="Eduardo")
    sobrenome: str = Field(..., example="Kami")
    sexo: str = Field(..., example="M")
    status: str = Field(..., example='1')


class UserDelete(BaseModel):
    id: str = Field(..., example='Informe seu id')


# Instanciando a aplicação
app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get('/users', response_model=List[UserList])
async def todos_usuarios():
    """
    Função retorna todos os usuários cadastrados
    """
    query = users.select()
    return await database.fetch_all(query)


@app.post('/users', response_model=UserList)
async def register_user(user: UserEntry):
    """
    Registrando um usuário
    """
    gID = str(uuid.uuid1())
    gDate = str(datetime.datetime.now())
    query = users.insert().values(
        id=gID,
        username=user.username,
        password=pwd_context.hash(user.password),
        nome=user.nome,
        sobrenome=user.sobrenome,
        sexo=user.sexo,
        create_at=gDate,
        status='1'
    )
    await database.execute(query)
    return {
        "id": gID,
        **user.dict(),
        "create_at": gDate,
        "status": '1',
    }


@app.get('/users/{userId}', response_model=UserList)
async def buscar_usuario_por_id(userId: str):
    """
    Função irá retornar os dados de um usuário informando o seu userId
    """
    query = users.select().where(users.c.id == userId)
    return await database.fetch_one(query)


@app.put('/users', response_model=UserList)
async def update_user(user: UserUpdate):
    """
    Função irá executar o update dos dados do usuario informado
    """
    gDate = str(datetime.datetime.now())
    query = users.update().\
        where(users.c.id == user.id).\
        values(
        nome=user.nome,
        sobrenome=user.sobrenome,
        sexo=user.sexo,
        status=user.status,
        create_at=gDate
        )
    await database.execute(query)
    return await buscar_usuario_por_id(user.id)


@app.delete('/users/{userId}')
async def delete_user(user: UserDelete):
    query = users.delete().where(users.c.id == user.id)
    await database.execute(query)

    return {
        "status": True,
        "message": "Este usuário foi deletado com sucesso!"
    }