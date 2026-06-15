"""
Módulo de Mapeamento de Tipos Estruturados (Data Contracts)

Concentra os contratos estáticos de transferência de dados (DTOs) via TypedDicts.
Substitui o uso de dicionários puros por estruturas tipadas em tempo de checagem estática.
"""

from typing import TypedDict, List, Optional, Union
from decimal import Decimal
from datetime import datetime, date

class Dados_usuarios_db(TypedDict):
    id_user: int
    nome_completo: str
    nome_user: str
    senha: str
    email: str
    telefone: str
    sal_fixo: Decimal


class Dados_receitas_db(TypedDict):
    id_receita: int
    fonte: str
    valor: float
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
    id_cc: Optional[int]


class Pega_despesas_cartao_db(TypedDict):
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
    id_cartao: int
    nome_cartao: str
    limite_cartao: float
    fechamento_fatura: int
    vencimento_fatura: int
    bandeira: str
    cor: str


class Dados_assinaturas_db(TypedDict):
    id_ass: int
    nome: str
    valor: float
    descricao: str
    data_aquisicao: datetime
    data_pp: datetime
    categoria: str
    dia_vencimento: int
    id_cc: Optional[int]


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
    data_compra: Union[datetime, date]
    prim_data_pag: Optional[Union[datetime, date]]
    nome_cartao: str
    info_cartao: Optional[Cartao]


class Pega_div_cartao_db(TypedDict):
    info: Dados_cartoes_db
    despesas: List[Pega_despesas_cartao_db]
    assinaturas: List[Pega_assinatuas_cartao_db]


class Envia_despesa_form(TypedDict):
    user_id_or_id_desp: int  # Pode representar user_id (Inclusão) ou id_desp (Edição)
    local: str
    valor_total: float
    parcelas: int
    descricao: str
    categoria: str
    dc_select_mysql: datetime
    prim_dc_select_mysql: datetime
    dia_venc: int
    id_card: Optional[int]


class Envia_ass_form(TypedDict):
    user_id_or_id_ass: int  # Pode representar user_id (Inclusão) ou id_ass (Edição)
    nome: str
    valor: float
    descricao: str
    data_aq_mysql: datetime
    data_pp_mysql: datetime
    dia_venc: int
    categoria: str
    id_card: Optional[int]