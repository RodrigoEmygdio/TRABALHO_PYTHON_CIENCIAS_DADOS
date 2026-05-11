from src.util.graifcos import Coluna


def concentracao_dados_dataframe(dataframe, filtro, coluna: Coluna):
    if filtro is not None:
        return dataframe[filtro][coluna.nome_coluna].value_counts(normalize=True) * 100
    else:
        return dataframe[coluna.nome_coluna].value_counts(normalize=True)
