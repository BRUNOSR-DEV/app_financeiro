

# BIBLIO PADRÕES
from decimal import Decimal
from typing import Optional, Union
from datetime import date, datetime
# =================================================================================
# -------- FORMATAÇÃO DE DATAS --------
# =================================================================================

def str_para_data(data_str: str) -> Optional[datetime]:
    """
    Converte uma string brasileira em um objeto datetime.

    Args:
        data_str (str): Data no formato 'DD/MM/AAAA'.

    Returns:
        Optional[datetime]: Objeto convertido ou None em caso de falha.
    """
    try:
        return datetime.strptime(data_str, "%d/%m/%Y")
    except ValueError:
        print(f"Erro: Formato de data inválido ({data_str})")
        return None


def data_para_exibicao(data_obj: Union[datetime, date, str, None]) -> str:
    """
    Formata objetos datetime para o padrão de leitura da UI brasileira.

    Args:
        data_obj: Objeto de data a ser formatado.

    Returns:
        str: Data no formato 'DD/MM/AAAA', ou string vazia se nulo.
    """
    if data_obj and hasattr(data_obj, "strftime"):
        return data_obj.strftime("%d/%m/%Y")
    return ""


def data_para_mysql(data_obj: Union[datetime, date, None]) -> Optional[str]:
    """
    Formata objetos datetime para a inserção padronizada no MySQL.

    Args:
        data_obj: Objeto de data a ser formatado.

    Returns:
        Optional[str]: String no formato 'YYYY-MM-DD', ou None se nulo.
    """
    if data_obj and hasattr(data_obj, "strftime"):
        return data_obj.strftime("%Y-%m-%d")
    return None


def mysql_para_obj(data_mysql: Union[str, datetime, date, None]) -> Union[datetime, date, None]:
    """
    Reidrata a string devolvida pelo MySQL transformando-a novamente em datetime.

    Args:
        data_mysql: A data extraída do banco de dados.

    Returns:
        Union[datetime, date, None]: O objeto datetime resultante.
    """
    if isinstance(data_mysql, str):
        try:
            return datetime.strptime(data_mysql, "%Y-%m-%d")
        except ValueError:
            print(f"Erro: Formato MySQL inválido ({data_mysql})")
            return None
    return data_mysql


# =================================================================================
# --------- FORMATAÇÃO DE MOEDA -------------
# =================================================================================

def formatar_moeda(valor: Union[float, Decimal, int]) -> str:
    """
    Formata números brutos para a representação monetária brasileira (BRL).

    Args:
        valor: Valor numérico a ser formatado.

    Returns:
        str: Representação no formato 'R$ X.XXX,XX'.
    """
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")