import requests


def importar_estados():
    estado = requests.get('https://servicodados.ibge.gov.br/api/v1/localidades/estados?orderBy=nome')
    r = estado.json()
    return r


def importar_cidades(uf):
    estado = requests.get(f'https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios')
    r = estado.json()
    return r