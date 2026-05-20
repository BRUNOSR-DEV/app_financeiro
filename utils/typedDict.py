from typing import TypedDict, List

from datetime import datetime

class Dados_usuarios_db(TypedDict):

    id_user: int
    nome_completo: str
    nome_user: str
    senha: str
    sal_fixo: float


class Dados_receitas_db(TypedDict):
    """Dict de receitas"""

    id_receita: int
    valor_recebido: float
    descricao: str
    data: datetime


class Dados_despesas_db(TypedDict):

    id_desp: int
    local: str
    valor_total: float
    parcelas: int
    descricao: str
    categoria: str
    data_compra: datetime
    data_pp: datetime
    dia_vencimento: int
    id_cc: int

class Pega_despesas_cartao_db(TypedDict):
    """ Dict de despesas do cartão informado """

    id_desp: int
    local: str
    valor_total: float
    parcelas: int
    descricao: str
    categoria: str
    data_compra: str
    nome_cartao: str
    limite_cartao: float
    fechamento_fatura: int
    vencimento_fatura: int


class Pega_despesas_avulsas_bd(TypedDict):

    id_desp: int
    local: str
    valor_total: float
    parcelas: int
    descricao: str
    categoria: str
    data_compra: datetime
    data_pp: datetime
    dia_vencimento: int


class Dados_cartoes_db(TypedDict):
    """ Dict dos cartões """

    id_cartao: int
    nome_cartao: str
    limite_cartao: float
    fechamento_fatura: int
    vencimento_fatura: int


class Dados_assinaturas_db(TypedDict):

    id_ass: int
    nome: str
    valor: float
    descricao: str
    data_aquisicao: datetime
    data_prim_pag: datetime
    categoria: str
    dia_vencimento: int
    id_cc: int


class Pega_assinaturas_avulças_db(TypedDict):

    id_ass: int
    nome: str
    valor: float
    descricao: str
    data_pp: datetime
    dia_vencimento: int
    categoria: str


class Pega_assinatuas_cartao_db(TypedDict):

    id_assinatura: int
    nome: str
    valor: float
    descricao: str
    data_aquisicao: datetime
    data_prim_pag: datetime
    dia_vencimento: int
    categoria: str
    nome_cartao: str
    limite: float
    dia_fechamento_cc: int
    dia_vencimento_cc: int



class Cartao(TypedDict):

    id_cartao: int
    nome_cartao: str
    fechamento: int
    vencimento: int
    limite: float


class Despesa_simulacao(TypedDict):

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


class Pega_div_cartao_db(TypedDict):

    info: Dados_cartoes_db
    despesas: List[Pega_despesas_cartao_db]
    assinaturas: List[Pega_assinatuas_cartao_db]



class Envia_despesa_form(TypedDict):

    user_id_or_id_desp: int #user_id ou id_desp
    local: str
    valor_total: float
    parcelas: int
    descricao: str
    categoria: str
    dc_select_mysql: datetime
    prim_dc_select_mysql: datetime
    dia_venc: int
    id_card: int


class Envia_ass_form(TypedDict):

    user_id_or_id_ass: int
    nome: str
    valor: float
    descricao: str
    data_aq_mysql: datetime
    data_pp_mysql: datetime
    dia_venc: int
    categoria:str
    id_card: int