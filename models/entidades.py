from datetime import datetime

class Usuario:
    def __init__(self, id, nome_comp, user, senha, sal_fixo):
        self.id_user: int = id
        self.nome_completo: str = nome_comp
        self.nome_user: str = user
        self._senha: str = senha
        self._sal_fixo: float = sal_fixo
 
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
            'sal_fixo': self.sal_fixo  
        }
    
 
class Receita:
    def __init__(self, id, valor, desc, data):
        self.id_receita: int = id
        self.valor_recebido: float = valor
        self.descricao: str = desc
        self.data: datetime = data

    def to_dict(self):
        """Converte o objeto em dicionário para as Frames."""
        return self.__dict__

class Despesa:
    def __init__(self, id, local, valor_total, parcelas, desc, cat, data_compra, data_pp, dia_venc, id_cc=None):
        self.id_desp: int = id
        self.local: str = local
        self.valor_total: float = valor_total
        self.parcelas: int = parcelas
        self.descricao: str = desc
        self.categoria: str = cat
        self.data_compra: datetime = data_compra
        self.data_pp: datetime = data_pp
        self.dia_vencimento: int = dia_venc
        self.id_cc: int = id_cc
    
    def to_dict(self):
        """Converte o objeto em dicionário para as Frames."""
        return self.__dict__
    

class DespesaDetalhadoDTO:
    def __init__(self, id, local, valor_total, parcelas, desc, cat, data_compra, nome_card, limite_card, fech_card, venc_card ):
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
    
    def to_dict(self):
        """Converte o objeto em dicionário para as Frames."""
        return self.__dict__


class Cartao_credito:
    def __init__(self, id, nome, limite, fech, venc):
        self.id_cartao: int = id
        self.nome_cartao: str = nome
        self.limite_cartao: float = limite
        self.dia_fechamento: int = fech
        self.dia_vencimento: int = venc
    
    def to_dict(self):
        """Converte o objeto em dicionário para as Frames."""
        return self.__dict__


class Assinatura:
    def __init__(self, id, nome, valor, desc, data_aq, data_pp, dia_venc, cat, id_cc=None):
        self.id_ass: int = id
        self.nome: str = nome
        self.valor: float = valor
        self.descricao: str = desc
        self.data_aquisicao: datetime = data_aq
        self.data_pp: datetime = data_pp
        self.dia_vencimento = dia_venc
        self.categoria: str = cat
        self.id_cc: int = id_cc

    
    def to_dict(self):
        """Converte o objeto em dicionário para as Frames."""
        return self.__dict__
    

class AssinaturaDetalhadoDTO:
    def __init__(self, id, nome, valor, desc, data_aq, data_pp, cat, nome_card, limite_card, fech_card, venc_card):
        self.id_ass: int = id
        self.nome: str = nome
        self.valor: float = valor
        self.descricao: str = desc
        self.data_aquisicao: datetime = data_aq
        self.data_prim_pag: datetime = data_pp
        self.categoria: str = cat

        self.nome_cartao: str = nome_card
        self.limite_cartao: float = limite_card
        self.dia_fechamento_cc: int = fech_card
        self.dia_vencimento_cc: int = venc_card
        
    
    def to_dict(self):
        """Converte o objeto em dicionário para as Frames."""
        return self.__dict__