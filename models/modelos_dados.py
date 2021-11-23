from pydantic import BaseModel, Field


# Model da Lista de usuários
class UserList(BaseModel):
    id: str
    username: str
    password: str
    nome: str
    sobrenome: str
    sexo: str
    estado: str
    cidade: str
    create_at: str
    status: str


# Model de Registro de usuário
class UserEntry(BaseModel):
    username: str = Field(..., example="edkami")
    password: str = Field(..., example="edkami")
    nome: str = Field(..., example="Eduardo")
    sobrenome: str = Field(..., example="Kami")
    sexo: str = Field(..., example="Masculino")
    estado: str = Field(..., example="Minas Gerais")
    cidade: str = Field(..., exemple="Belo Horizonte")


# Model de Update de usuário
class UserUpdate(BaseModel):
    id: str = Field(..., example='Informe seu id')
    nome: str = Field(..., example="Novo Nome")
    sobrenome: str = Field(..., example="Novo Sobrenome")
    sexo: str = Field(..., example="Novo Sexo")
    estado: str = Field(..., example="Novo Estado")
    cidade: str = Field(..., exemple="Nova Cidade")
    status: str = Field(..., example='1')


# Model de Delete de usuário
class UserDelete(BaseModel):
    id: str = Field(..., example='Informe seu id')
