from datetime import datetime
from decimal import Decimal

class Usuario:
    def __init__(self, nome_completo, nome_user, senha, email, sal_fixo, telefone=None, telegram_chat_id=None, id_user=None):

        self.nome_completo: str = nome_completo
        self.nome_user: str = nome_user
        self._senha: str = senha
        self.email: str = email
        self._sal_fixo: float = sal_fixo
        self.telefone: str = telefone
        self.tci: str = telegram_chat_id
        self.id_user: int = id_user
 
    @property
    def senha(self):
        return self._senha
    
    @property
    def sal_fixo(self):
        return self._sal_fixo
    
    def to_dict(self):
        """Monta o dicionário com as chaves limpas que a UI espera."""
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
    
 
class Receita:
    def __init__(self, fonte, valor, descricao, data, id=None):
        self.fonte: str = fonte
        self.valor: Decimal = valor
        self.descricao: str = descricao
        self.data: datetime = data
        self.id_receita: int = id

    def to_dict(self):
        """Converte o objeto em dicionário para as Frames."""
        return self.__dict__

class Despesa:
    def __init__(self, local, valor_total, parcelas, descricao, categoria, data_compra, data_pp, dia_venc, id_cc=None, id_desp=None):
        self.local: str = local
        self.valor_total: float = valor_total
        self.parcelas: int = parcelas
        self.descricao: str = descricao
        self.categoria: str = categoria
        self.data_compra: datetime = data_compra
        self.data_pp: datetime = data_pp
        self.dia_vencimento: int = dia_venc
        self.id_cc: int = id_cc
        self.id_desp: int = id_desp
        
    def to_dict(self):
        """Converte o objeto em dicionário para as Frames."""
        return self.__dict__
    

class DespesaDetalhadoDTO:
    def __init__(self, id, local, valor_total, parcelas, desc, cat, data_compra, nome_card, limite_card, fech_card, venc_card, bandeira, cor):
        self.id_desp: int = id
        self.local: str = local
        self.valor_total: float = valor_total
        self.parcelas: int = parcelas
        self.descricao: str = desc
        self.categoria: str = cat
        self.data_compra: datetime = data_compra

        #Entidade cartao_credito
        self.nome_cartao: str = nome_card
        self.limite_cartao: float = limite_card
        self.dia_fechamento: int = fech_card
        self.dia_vencimento: int = venc_card
        self.bandeira: str = bandeira
        self.cor: str = cor
    
    def to_dict(self):
        """Converte o objeto em dicionário para as Frames."""
        return self.__dict__


class Cartao_credito:
    def __init__(self, nome, limite, fech, venc, bandeira, cor, id=None):
        self.nome_cartao: str = nome
        self.limite_cartao: float = limite
        self.dia_fechamento: int = fech
        self.dia_vencimento: int = venc
        self.bandeira: str = bandeira
        self.cor: str = cor
        self.id_cartao: int = id
    
    def to_dict(self):
        """Converte o objeto em dicionário para as Frames."""
        return self.__dict__


class Assinatura:
    def __init__(self, nome, valor, descricao, categoria, data_aq, data_pp, dia_venc, id_cc=None, id=None):
        
        self.nome: str = nome
        self.valor: float = valor
        self.descricao: str = descricao
        self.categoria: str = categoria
        self.data_aquisicao: datetime = data_aq
        self.data_pp: datetime = data_pp
        self.dia_vencimento = dia_venc
        self.id_cc: int = id_cc
        self.id_ass: int = id
    
    def to_dict(self):
        """Converte o objeto em dicionário para as Frames."""
        return self.__dict__
    

class AssinaturaDetalhadoDTO:
    def __init__(self, id, nome, valor, desc, cat,  data_aq, data_pp, dia_venc, nome_card, limite_card, fech_card, venc_card, bandeira, cor):
        self.id_ass: int = id
        self.nome: str = nome
        self.valor: float = valor
        self.descricao: str = desc
        self.categoria: str = cat
        self.data_aquisicao: datetime = data_aq
        self.data_prim_pag: datetime = data_pp
        self.dia_vencimento: int = dia_venc

        self.nome_cartao: str = nome_card
        self.limite_cartao: float = limite_card
        self.dia_fechamento_cc: int = fech_card
        self.dia_vencimento_cc: int = venc_card
        self.bandeira: str = bandeira
        self.cor: str = cor
        
    def to_dict(self):
        """Converte o objeto em dicionário para as Frames."""
        return self.__dict__