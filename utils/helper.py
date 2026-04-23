from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar

import re

from utils.audio_helper import tocar_notificacao


#-------- opções meses ----------
def gerar_opcoes_meses():
    meses_nome = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 
                  5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 
                  9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}

    return meses_nome


# -------- Validação de entratada ----------
def check_entry_num(P):
    """
    P é o valor que o campo terá SE a tecla for aceita.
    Retorna True se for válido, False se for inválido.
    """
    placeholders_permitidos = [
        "",             # Permite apagar tudo
        "R$ 0,00",      # Placeholder de Despesas/Receitas
        "Ex: 4500.00",  # Placeholder da Renda Fixa
        "Valor Ganho",
    ]

    if P == placeholders_permitidos: # Permite que o usuário apague tudo com o Backspace
        return True
    
    # Regex: aceita números, opcionalmente um ponto ou vírgula, e mais números
    padrao = r'^[0-9]*[.,]?[0-9]*$'
    
    if re.match(padrao, P):
        return True
    else:
        tocar_notificacao('erro')
        return False


# ---- formatação de datas --------
def str_para_data(data_str):
    """Converte 'DD/MM/AAAA' para objeto datetime."""
    try:
        return datetime.strptime(data_str, "%d/%m/%Y")
    except ValueError:
        print(f"Erro: Formato de data inválido ({data_str})")
        return None


def data_para_exibicao(data_obj):
    """Converte objeto date/datetime para 'DD/MM/AAAA'."""
    if data_obj:
        return data_obj.strftime("%d/%m/%Y")
    return ""


def data_para_mysql(data_obj):
    """Converte objeto date/datetime para 'YYYY-MM-DD'."""
    if data_obj:
        return data_obj.strftime("%Y-%m-%d")
    return None


def mysql_para_obj(data_mysql):
    """
    Converte uma string 'YYYY-MM-DD' (vinda do banco) em objeto datetime.
    Se já for um objeto date/datetime, apenas o retorna.
    """
    if isinstance(data_mysql, str):
        try:
            return datetime.strptime(data_mysql, "%Y-%m-%d")
        except ValueError:
            print(f"Erro: Formato MySQL inválido ({data_mysql})")
            return None
    return data_mysql


# --------- formatação de moeda -------------
def formatar_moeda(valor):
    """Para formatar R$ 1.234,56."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# ---------- Centralizar Janela Tkinter ------------
def centralizar_janela(janela, largura, altura):
    # Pega a largura e altura da tela do PC do usuário

    janela.update_idletasks()
    
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()

    # Calcula a posição X e Y para o centro
    pos_x = (largura_tela // 2) - (largura // 2)
    pos_y = (altura_tela // 2) - (altura // 2)

    # Aplica a geometria: "300x150+500+300" por exemplo
    janela.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")


# ---------- Engine Controle de data e parcelas -----------------
def controle_data_parc(data_pp, dia_vencimento, total_parcelas=None, controle_mes=None, data_atual=None):
    """
    Calcula a parcela atual baseada na data de compra e no fechamento da fatura.
    Retorna uma string no formato 'Atual/Total' (ex: '3/12').
    """
    if data_atual is None:
        data_atual = datetime.now().date()
    

    assinatura = False

    if total_parcelas is None:
        assinatura = True


    mes_vigente = data_atual.month
    prox_mes = (data_atual + relativedelta(months=1)).month
    seg_prox_mes = (data_atual + relativedelta(months=2)).month
    ter_prox_mes = (data_atual + relativedelta(months=3)).month
    quart_prox_mes = (data_atual + relativedelta(months=4)).month

    if controle_mes == mes_vigente:
        data_alvo = data_atual

    elif controle_mes == prox_mes:
        data_alvo = data_atual + relativedelta(months=1)

    elif controle_mes == seg_prox_mes:
        data_alvo = data_atual + relativedelta(months=2)
    
    elif controle_mes == ter_prox_mes:
        data_alvo = (data_atual + relativedelta(months=3))

    elif controle_mes == quart_prox_mes:
        data_alvo = (data_atual + relativedelta(months=4))
        
    """   # 1. Descobre o mês da PRIMEIRA cobrança
    mes_primeira_cobranca = data_compra_obj.month
    ano_primeira_cobranca = data_compra_obj.year"""
    
    # Se a compra foi DEPOIS do fechamento, a 1ª parcela cai só no mês seguinte
    
    mes_primeira_cobranca = data_pp.month
    ano_primeira_cobranca = data_pp.year
            
        
    if not assinatura:

        # 2. Calcula a diferença de meses entre o mês de atual e o mês da 1ª cobrança
        diferenca_anos = data_alvo.year - ano_primeira_cobranca
        diferenca_meses = data_alvo.month - mes_primeira_cobranca
        meses_passados = (diferenca_anos * 12) + diferenca_meses

    
        # A parcela atual é os meses que passaram + 1 (a parcela inicial)
    
        parcela_atual = meses_passados + 1

    
    try:
        data_pagamento = data_alvo.replace(day=dia_vencimento)

    except ValueError:
        # Prevenção de erro: Se o vencimento for dia 31 e o mês alvo for Fevereiro (28)
        ultimo_dia = calendar.monthrange(data_alvo.year, data_alvo.month)[1]
        data_pagamento = data_alvo.replace(day=ultimo_dia)

    
    if assinatura:

        data_inicio_cobranca = data_pp.replace(day=1)
        data_alvo_inicio = data_alvo.replace(day=1)

        if data_alvo_inicio >= data_inicio_cobranca:
            return "Mensal", True, data_pagamento
        else:
            return "Mensal", False, data_pagamento
        

    if not assinatura:

        if parcela_atual < 1:
            # Se for menor que 1, a cobrança ainda não chegou neste mês alvo
            return f"0/{total_parcelas}", False, data_pagamento #a vencer
    
        elif parcela_atual > total_parcelas:
            # Já acabou de pagar antes deste mês alvo
            return f"{total_parcelas}/{total_parcelas}", False, data_pagamento #quitado
        
        else:
            # Está na janela de pagamento! Vai pra tabela!
            return f"{parcela_atual}/{total_parcelas}", True, data_pagamento
    

def controle_data_parc_cc(data_compra_obj, dia_fechamento, dia_vencimento, total_parcelas=None, controle_mes=None, data_atual=None):
    """
    Returns: 
    """

    if data_atual is None:
        data_atual = datetime.now().date()

    assinatura = False

    if total_parcelas is None:
        assinatura = True
    
    mes_vigente = data_atual.month
    prox_mes = (data_atual + relativedelta(months=1)).month
    seg_prox_mes = (data_atual + relativedelta(months=2)).month
    ter_prox_mes = (data_atual + relativedelta(months=3)).month
    quart_prox_mes = (data_atual + relativedelta(months=4)).month

    data_alvo = None
    # Define qual é a FATURA ALVO (Mês Atual ou Próximo Mês)
    if controle_mes == mes_vigente:
        data_alvo = data_atual

    elif controle_mes == prox_mes:
        data_alvo = (data_atual + relativedelta(months=1))
        
    elif controle_mes == seg_prox_mes:
        data_alvo = (data_atual + relativedelta(months=2))

    elif controle_mes == ter_prox_mes:
        data_alvo = (data_atual + relativedelta(months=3))

    elif controle_mes == quart_prox_mes:
        data_alvo = (data_atual + relativedelta(months=4))
        
    
    # Descobre a Fatura da PRIMEIRA cobrança (com base no fechamento)
    primeira_cobranca = data_compra_obj
    if data_compra_obj.day >= dia_fechamento: 
        primeira_cobranca += relativedelta(months=1)


    # Quantos meses se passaram entre a 1ª Cobrança e a Fatura Alvo
    if not assinatura:
        diferenca_anos = data_alvo.year - primeira_cobranca.year
        diferenca_meses = data_alvo.month - primeira_cobranca.month
        meses_passados = (diferenca_anos * 12) + diferenca_meses

        # A parcela atual nesta fatura alvo
        parcela_atual = meses_passados + 1
    

    try:
        data_pagamento = data_alvo.replace(day=dia_vencimento)
        
    except ValueError:
        # Prevenção de erro: Se o vencimento for dia 31 e o mês alvo for Fevereiro (28)
        ultimo_dia = calendar.monthrange(data_alvo.year, data_alvo.month)[1]
        data_pagamento = data_alvo.replace(day=ultimo_dia)


    if assinatura:
        data_inicio_cobranca = primeira_cobranca.replace(day=1)
        data_alvo_inicio = data_alvo.replace(day=1)

        if data_alvo_inicio >= data_inicio_cobranca:
            return "Mensal", True, data_pagamento
        else:
            return "Mensal", False, data_pagamento
    
    if not assinatura:
        # Filtros para saber se a despesa entra na tabela
        if parcela_atual < 1:
            # Se for menor que 1, a cobrança ainda não chegou neste mês alvo, o segundo retorno é um bool de controle
            return f"0/{total_parcelas} (A vencer)", False, data_pagamento
        
        elif parcela_atual > total_parcelas:
            # Já acabou de pagar antes deste mês alvo
            return f"{total_parcelas}/{total_parcelas} (Quitado)", False, data_pagamento
        
        else:
            # Está na janela de pagamento! Vai pra tabela!
            return f"{parcela_atual}/{total_parcelas}", True, data_pagamento