"""
Módulo de Entidades de Domínio e Objetos de Transferência de Dados (DTO).

Este módulo define a estrutura de dados centralizada do sistema financeiro (AVIR AF),
mapeando as tabelas do banco de dados relacional para Objetos Python (POO), além de 
estruturar os DTOs para consultas complexas de JOIN exigidas pela interface gráfica.
"""

# ------------------------------ IMPORTAÇÃO - MÓDULOS BIBLIOTECAS ---------------------------------
#BILIO PADRÕES
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any

# =================================================================================
# --- ENTIDADE USUARIO ---
# =================================================================================

class Usuario:
    """
    Representa um usuário do sistema com credenciais e configurações financeiras.
    
    Attributes:
        id_user (int): Chave primária gerada automaticamente pelo banco de dados.
        nome_completo (str): Nome completo ou razão social do usuário.
        nome_user (str): Nome de login exclusivo (username).
        email (str): Endereço de e-mail para contato e recuperações.
        telefone (str): Número de telefone formatado.
        tci (str): ID do chat do Telegram usado pelo bot de alertas.
    """

    def __init__(self, nome_completo: str, nome_user: str, senha: str, email: str, sal_fixo: Decimal, telefone: Optional[str] = None, telegram_chat_id: Optional[str] = None, id_user: Optional[int] = None) -> None:

        """Inicializa a entidade Usuario com validação de tipos básicos."""
        self.nome_completo: str = nome_completo
        self.nome_user: str = nome_user
        self._senha: str = senha
        self.email: str = email
        self._sal_fixo: Decimal = sal_fixo
        self.telefone: Optional[str] = telefone
        self.tci: Optional[str] = telegram_chat_id
        self.id_user: Optional[int] = id_user
 
    @property
    def senha(self) -> str:
        """str: Retorna o Hash protegido da senha (Bcrypt)."""
        return self._senha
    
    @property
    def sal_fixo(self) -> Decimal:
        """float: Retorna o salário fixo do usuário cadastrado."""
        return self._sal_fixo
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a entidade em um dicionário para consumo seguro na UI.
        
        Returns:
            Dict[str, Any]: Chaves padronizadas esperadas pelos formulários da interface.
        """
        return {
            'id_user': self.id_user,
            'nome_completo': self.nome_completo,
            'nome_user': self.nome_user,
            'senha': self.senha,
            'email': self.email,       
            'sal_fixo': self.sal_fixo,
            'telefone': self.telefone,
            'tci': self.tci 
        }


# =================================================================================
# --- ENTIDADE RECEITA ---
# =================================================================================

class Receita:
    """Representa uma entrada financeira ou rendimento no sistema."""

    def __init__(self, fonte: str, valor: Decimal, descricao: str, data: datetime, id: Optional[int] = None) -> None:
        self.fonte: str = fonte
        self._valor: Decimal = valor 
        self.descricao: str = descricao
        self.data: datetime = data
        self.id_receita: Optional[int] = id

    @property
    def valor(self) -> Decimal:
        return self._valor

    @valor.setter
    def valor(self, novo_valor: Decimal) -> None:
        if novo_valor <= 0:
            raise ValueError("O valor da receita deve ser maior que zero.")
        self._valor = novo_valor

    def to_dict(self) -> Dict[str, Any]:
        """Garante o mapeamento limpo sem expor o underline interno."""
        return {
            'fonte': self.fonte,
            'valor': self.valor,
            'descricao': self.descricao,
            'data': self.data,
            'id_receita': self.id_receita
        }


# =================================================================================
# --- ENTIDADE DESPESA ---
# =================================================================================

class Despesa:
    """
    Representa um gasto pontual ou parcelado vinculado ou não a um cartão.
    """

    def __init__(self, local: str, valor_total: Decimal, parcelas: int, descricao: str, categoria: str, data_compra: datetime, data_pp: datetime, dia_venc: int, id_cc: Optional[int] = None, id_desp: Optional[int] = None) -> None:
        
        self.local: str = local
        self._valor_total: Decimal = valor_total
        self.parcelas: int = parcelas
        self.descricao: str = descricao
        self.categoria: str = categoria
        self.data_compra: datetime = data_compra
        self.data_pp: datetime = data_pp
        self.dia_vencimento: int = dia_venc
        self.id_cc: Optional[int] = id_cc
        self.id_desp: Optional[int] = id_desp
        

    @property
    def valor_total(self) -> Decimal:
        return self._valor_total

    @valor_total.setter
    def valor_total(self, novo_valor: Decimal) -> None:
        if novo_valor <= 0:
            raise ValueError("O valor total da compra precisa ser maior que zero!")
        self._valor_total = novo_valor

    @property
    def parcelas(self) -> int:
        return self._parcelas

    @parcelas.setter
    def parcelas(self, qtd: int) -> None:
        if qtd <= 0:
            raise ValueError("A quantidade de parcelas deve ser maior ou igual a 1.")
        self._parcelas = qtd

    @property
    def dia_vencimento(self) -> int:
        return self._dia_vencimento

    @dia_vencimento.setter
    def dia_vencimento(self, dia: int) -> None:
        if not (1 <= dia <= 31):
            raise ValueError("O dia de vencimento deve estar entre 1 e 31.")
        self._dia_vencimento = dia

    def to_dict(self) -> Dict[str, Any]:
        return {
            'local': self.local,
            'valor_total': self.valor_total,
            'parcelas': self.parcelas,
            'descricao': self.descricao,
            'categoria': self.categoria,
            'data_compra': self.data_compra,
            'data_pp': self.data_pp,
            'dia_vencimento': self.dia_vencimento,
            'id_cc': self.id_cc,
            'id_desp': self.id_desp,
        }
    

# --- DATA TRANSFER OBJECTS (DTOs para consultas complexas de JOIN) ---
class DespesaDetalhadoDTO:
    """
    Objeto de transferência para agregação de dados entre Despesa e Cartão de Crédito.
    Utilizado puramente na renderização detalhada de faturas e tabelas na UI.
    """

    def __init__(self, id: int, local: str, valor_total: float, parcelas: int, desc: str, cat: str, data_compra: datetime, nome_card: str, limite_card: float, fech_card: int, venc_card: int, bandeira: str, cor: str) -> None:

        self.id_desp: int = id
        self.local: str = local
        self.valor_total: float = valor_total
        self.parcelas: int = parcelas
        self.descricao: str = desc
        self.categoria: str = cat
        self.data_compra: datetime = data_compra

        # Propriedades do cartão acopladas para exibição direta
        self.nome_cartao: str = nome_card
        self.limite_cartao: float = limite_card
        self.dia_fechamento: int = fech_card
        self.dia_vencimento: int = venc_card
        self.bandeira: str = bandeira
        self.cor: str = cor
    
    def to_dict(self) -> Dict[str, Any]:
        """Retorna o mapeamento do JOIN em dicionário plano."""
        return self.__dict__


# =================================================================================
# --- ENTIDADE CARTAO DE CRÉDITO ---
# =================================================================================

class Cartao_credito:
    """
    Representa um cartão de crédito associador de despesas parceladas.
    """

    def __init__(self, nome: str, limite: Decimal, fech: int, venc: int, bandeira: Optional[str], cor: Optional[str], id: Optional[int] = None) -> None:
        self.nome_cartao: str = nome
        self._limite_cartao: Decimal = limite
        self._dia_fechamento: int = fech
        self._dia_vencimento: int = venc
        self.bandeira: Optional[str] = bandeira
        self.cor: Optional[str] = cor
        self.id_cartao: Optional[int] = id


    @property
    def limite_cartao(self) -> Decimal:
        return self._limite_cartao

    @limite_cartao.setter
    def limite_cartao(self, novo_limite: Decimal) -> None:
        if novo_limite <= 0:
            raise ValueError('O valor do limite precisa ser maior que zero!')
        self._limite_cartao = novo_limite
    
    @property
    def dia_fechamento(self) -> int:
        return self._dia_fechamento
    
    @dia_fechamento.setter
    def dia_fechamento(self, dia_f: int) -> None:
        if not (1 <= dia_f <= 31):
            raise ValueError('Dia de fechamento válido precisa ser de 1 á 31!')
        self._dia_fechamento = dia_f

    @property
    def dia_vencimento(self) -> int:
        return self._dia_vencimento
    
    @dia_vencimento.setter
    def dia_vencimento(self, dia_v: int) -> None:
        if not (1 <= dia_v <= 31):
            raise ValueError('Dia de vencimenro válido precisa ser de 1 á 31!')
        self._dia_vencimento = dia_v

    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'local': self.local,
            'valor_total': self.valor_total,
            'parcelas': self.parcelas,
            'descricao': self.descricao,
            'categoria': self.categoria,
            'data_compra': self.data_compra,
            'data_pp': self.data_pp,
            'dia_vencimento': self.dia_vencimento,
            'id_cc': self.id_cc,
            'id_desp': self.id_desp
        }


# =================================================================================
# --- ENTIDADE ASSINATURA ---
# =================================================================================

class Assinatura:
    """
    Representa cobranças recorrentes (mensais ou anuais) fixas do usuário.
    """

    def __init__(self, nome: str, valor: Decimal, descricao: str, categoria: str, data_aq: datetime, data_pp: datetime, dia_venc: int, id_cc: Optional[int] = None, id: Optional[int] = None) -> None:
        
        self.nome: str = nome
        self.valor: Decimal = valor
        self.descricao: str = descricao
        self.categoria: str = categoria
        self.data_aquisicao: datetime = data_aq
        self.data_pp: datetime = data_pp
        self.dia_vencimento: int = dia_venc
        self.id_cc: Optional[int] = id_cc
        self.id_ass: Optional[int] = id
        
    @property
    def valor(self) -> Decimal:
        return self._valor

    @valor.setter
    def valor(self, novo_valor: Decimal) -> None:
        if novo_valor <= 0:
            raise ValueError("O valor de uma assinatura tem que ser maior que zero.")
        self._valor = novo_valor


    def to_dict(self) -> Dict[str, Any]:
        return {
            'nome': self.nome,
            'valor': self.valor,
            'descricao': self.descricao,
            'categoria': self.categoria,
            'data_aquisicao': self.data_aquisicao,
            'data_pp': self.data_pp,
            'dia_vencimento': self.dia_vencimento,
            'id_cc': self.id_cc,
            'id_ass': self.id_ass
        }
    

# --- DATA TRANSFER OBJECTS (DTOs para consultas complexas de JOIN) ---
class AssinaturaDetalhadoDTO:
    """
    Objeto de transferência para agregação de dados entre Assinatura e Cartão de Crédito.
    Utilizado para carregar a listagem analítica na interface gráfica de gerenciamento.
    """

    def __init__(self, id: int, nome: str, valor: float, desc: str, cat: str,  data_aq: datetime, data_pp: datetime, dia_venc: int, nome_card: str, limite_card: float, fech_card: int, venc_card: int, bandeira: str, cor: str) -> None:

        self.id_ass: int = id
        self.nome: str = nome
        self.valor: float = valor
        self.descricao: str = desc
        self.categoria: str = cat
        self.data_aquisicao: datetime = data_aq
        self.data_prim_pag: datetime = data_pp
        self.dia_vencimento: int = dia_venc

        # Propriedades do cartão injetadas
        self.nome_cartao: str = nome_card
        self.limite_cartao: float = limite_card
        self.dia_fechamento_cc: int = fech_card
        self.dia_vencimento_cc: int = venc_card
        self.bandeira: str = bandeira
        self.cor: str = cor
        
    def to_dict(self) -> Dict[str, Any]:
        """Retorna o agrupamento completo da assinatura."""
        return self.__dict__