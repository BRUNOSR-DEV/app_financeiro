from typing import TypedDict

from datetime import datetime


class Cartao(TypedDict):

    id_cartao: int
    nome_cartao: str
    fechamento: int
    vencimento: int
    limite: float

class Cartao_banco(TypedDict):

    id_cartao: int
    nome_cartao: str
    limite_cartao: float
    fechamento_fatura: int
    vencimento_fatura: int
    
class Despesa(TypedDict):

    id_desp: int
    local: str
    valor_total: float
    parcelas: int
    descricao: str
    categoria: str
    data_compra: datetime
    prim_data_pag: datetime
    nome_cartao: str
    info_cartao: Cartao




