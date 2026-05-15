from datetime import datetime

class Usuarios:
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
    
 
class Receitas:
    def __init__(self, id, valor, desc, data):
        self.id_receita: int = id
        self.valor_recebido: float = valor
        self.descricao: str = desc
        self.data: datetime = data


class Despesa:
    def __init__(self, id, local, valor_total, parcelas, desc, cat, data_compra, data_pp, dia_venc, id_cc):
        self.id_desp: int = id
        self.local: str = local
        self.valor_total: float = valor_total
        self.parcelas: int = parcelas
        self.descricao: str = desc
        self.categoria: str = cat
        self.data_compra: datetime = data_compra
        self.data_pp: datetime = data_pp
        self.dia_venc: int = dia_venc
        self.id_cc: int = id_cc


class Card_credito:
    def __init__(self, id, nome, limite, fech, venc):
        self.id_cartao: int = id
        self.nome_cartao: str = nome
        self.limite_cartao: float = limite
        self.fechamento_fatura: int = fech
        self.vencimento_fatura: int = venc


class Assinaturas:
    def __init__(self, id, nome, valor, desc, data_aq, data_pp, cat, id_cc):
        self.id_ass: int = id
        self.nome: str = nome
        self.valor: float = valor
        self.descricao: str = desc
        self.data_aquisicao: datetime = data_aq
        self.data_prim_pag: datetime = data_pp
        self.categoria: str = cat
        self.id_cc: int = id_cc