import sqlalchemy
from asyncpg import UniqueViolationError
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List
from passlib.context import CryptContext
from controllers.importar_dados_ibge import importar_estados, importar_cidades
from models.postgres_database import users, estados, database, create_db, cidades
from models.modelos_dados import UserList, UserEntry, UserUpdate, UserDelete
import datetime
import uuid
import json


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Instanciando a aplicação
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Validação de criação do banco de dados
create_db()


# Inclusão dos dados do IBGE - estados
async def estado_ibge():
    result = importar_estados()
    for item in result:
        id = item.get("id")
        nome = item.get("nome")
        sigla = item.get("sigla")
        try:
            query = estados.insert().values(id=id, nome=nome, sigla=sigla)
            await database.execute(query)
        except UniqueViolationError:
            pass


# Inclusão dos dados do IBGE - cidades
async def cidade_ibge():
    query = estados.select()
    ufs = await database.fetch_all(query)
    for uf in ufs:
        result = importar_cidades(uf.get("id"))
        print(f"incluso cidades de id = {uf.get('id')}")
        for item in result:
            id = item.get("id")
            nome_estado = uf.get("nome")
            nome = item.get("nome")
            try:
                query = cidades.insert().values(id=id, nome_estado=nome_estado, nome=nome)
                await database.execute(query)
            except UniqueViolationError:
                pass


async def cidade_idestado():
    query = cidades.select()
    cidades_db = await database.fetch_all(query)
    query2 = estados.select()
    estados_db = await database.fetch_all(query2)
    dict_cidade = {}
    for cidade in cidades_db:
        estado = str(cidade.get('nome_estado'))
        if estado in dict_cidade:
            dict_cidade[estado].append(cidade.get('nome'))
        else:
            dict_cidade[estado] = [cidade.get('nome')]
    json_cidades = json.dumps(dict_cidade)
    json_estados = json.dumps([str(e.get('nome')) for e in estados_db])
    print(json_cidades)
    print(json_estados)
    return json_cidades, json_estados


@app.on_event("startup")
async def startup():
    await database.connect()
    await estado_ibge()
    await cidade_ibge()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get('/')
@app.get('/index', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


@app.get('/users', response_model=List[UserList])
async def todos_usuarios():
    """
    Função retorna todos os usuários cadastrados
    """
    query = users.select()
    return await database.fetch_all(query)


@app.get('/new_user', response_class=HTMLResponse)
async def new_user(request: Request):
    json_cidade, json_estado = await cidade_idestado()
    return templates.TemplateResponse("cadastro.html", context={"request": request,
                                                                'estados': json_estado,
                                                                'cidades': json_cidade})


@app.post('/users')
async def register_user(username: str = Form(...), password: str = Form(...), nome: str = Form(...),
                        sobrenome: str = Form(...), sexo: str = Form(...), estado: str = Form(...),
                        cidade: str = Form(...)):
    """
    Registrando um usuário
    """
    gID = str(uuid.uuid1())
    gDate = str(datetime.datetime.now())
    query = users.insert().values(
        id=gID,
        username=username,
        password=pwd_context.hash(password),
        nome=nome,
        sobrenome=sobrenome,
        sexo=sexo,
        estado=estado,
        cidade=cidade,
        create_at=gDate,
        status='1'
    )
    await database.execute(query)
    return {
        "id": gID,
        "username": username,
        "password": password,
        "nome": nome,
        "sobrenome": sobrenome,
        "sexo": sexo,
        "estado": estado,
        "cidade": cidade,
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
        estado=user.estado,
        cidade=user.cidade,
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
