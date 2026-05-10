from enum import Enum
from typing import NamedTuple

from matplotlib import pyplot as plt



def graf_evolu_pais( paises_por_ano,paises=["Brazil", "Portugal", "China"]):
    plt.figure(figsize=(10, 5))
    for pais, group in paises_por_ano:
        if pais in paises:
            plt.plot(
                group["year"],
                group['lifeExp'],
                marker='o',
                label=pais,
            )
    plt.legend()
    plt.show()


class Posicao(Enum):
    INICIAL = 0
    FINAL = 1


class Coluna(NamedTuple):
    nome_coluna: str
    label: str
    sortable: bool


def gerar_barh_grafico(
        ano,
        data_frame,
        colunas: tuple[Coluna,Coluna],
        titulo,
        posicao=Posicao.INICIAL,
        quantidade=10

):
    """

    :param ano:
    :param data_frame:
    :param colunas:
    :param titulo:
    :param posicao:
    :param quantidade: Quantidade de registros retornados
    """
    coluna_y, coluna_x = colunas
    sortable_by: str

    for coluna in colunas:
        if coluna.sortable:
            sortable_by = coluna.nome_coluna
            break

    if len(sortable_by):
        df = data_frame[data_frame['year'] == ano].sort_values(sortable_by ,ascending=False)
    else:
        df = data_frame[data_frame['year'] == ano]

    if posicao == Posicao.INICIAL:
        df = df.head(quantidade)
    elif posicao == Posicao.FINAL:
        df = df.tail(quantidade)

    plt.figure(figsize=(12, 20))
    plt.barh(
        df[coluna_y.nome_coluna],
        df[coluna_x.nome_coluna],
    )
    plt.gca().invert_xaxis()

    plt.title(titulo)
    plt.xlabel(coluna_x.label)
    plt.ylabel(coluna_y.label)

    plt.show()
