import databases
import sqlalchemy
from sqlalchemy_utils.functions import database_exists, create_database


# PostgreSQL
user_db = 'postgres_user'
pass_db = 'python_test'
name_db = 'DBFastAPi'
DATABASE_URL = f'postgresql://{user_db}:{pass_db}@localhost:5432/{name_db}'
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()


# --- Modelando o banco de dados

# Tabela de Usuários
users = sqlalchemy.Table(
    "usuarios",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column('username', sqlalchemy.String),
    sqlalchemy.Column('password', sqlalchemy.String),
    sqlalchemy.Column('nome', sqlalchemy.String),
    sqlalchemy.Column('sobrenome', sqlalchemy.String),
    sqlalchemy.Column('sexo', sqlalchemy.String),
    sqlalchemy.Column('estado', sqlalchemy.String),
    sqlalchemy.Column('cidade', sqlalchemy.String),
    sqlalchemy.Column('create_at', sqlalchemy.String),
    sqlalchemy.Column('status', sqlalchemy.CHAR),
)

# Tabela Estado
estados = sqlalchemy.Table(
    "estados",
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('nome', sqlalchemy.String, nullable=False, unique=True),
    sqlalchemy.Column('sigla', sqlalchemy.String, nullable=False),
)

# Tabela Cidades
cidades = sqlalchemy.Table(
    "cidades",
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('nome_estado', sqlalchemy.String, sqlalchemy.ForeignKey('estados.nome'), nullable=False),
    sqlalchemy.Column('nome', sqlalchemy.String, nullable=False),
)


def create_db():
    if not database_exists(DATABASE_URL):
        try:
            # Criando database
            create_database(DATABASE_URL)
            # Criando engine
            engine = sqlalchemy.create_engine(DATABASE_URL)
            # Criando todas as tabelas
            metadata.create_all(engine)
            print('DB criado com sucesso')
        except Exception as exc:
            print(f'Falha ao criar o banco de dados. Motivo: {exc}')
    else:
        print("DB existente")


def connect_database():
    database = databases.Database(DATABASE_URL)
    return database