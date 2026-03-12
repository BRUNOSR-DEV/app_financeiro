from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar


def gerar_opcoes_meses():
    meses_nome = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 
                  5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 
                  9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}

    return meses_nome


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



def formatar_moeda(valor):
    """Auxiliar extra para formatar R$ 1.234,56."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")



#rename - control_pags()
def controle_data_parc(data_compra_obj, primeira_parc, dia_vencimento, total_parcelas, vigente=True, data_atual=None):
    """
    Calcula a parcela atual baseada na data de compra e no fechamento da fatura.
    Retorna uma string no formato 'Atual/Total' (ex: '3/12').
    """
    if data_atual is None:
        data_atual = datetime.now()
    
    controle_mes =  None

    if vigente:
        data_alvo = data_atual
    else:
        data_alvo = data_atual + relativedelta(months=1)
        
    # 1. Descobre o mês da PRIMEIRA cobrança
    mes_primeira_cobranca = data_compra_obj.month
    ano_primeira_cobranca = data_compra_obj.year
    
    # Se a compra foi DEPOIS do fechamento, a 1ª parcela cai só no mês seguinte
    
    mes_primeira_cobranca = primeira_parc.month
    ano_primeira_cobranca = primeira_parc.year
            
    # 2. Calcula a diferença de meses entre o mês atual e o mês da 1ª cobrança
    diferenca_anos = data_atual.year - ano_primeira_cobranca
    diferenca_meses = data_atual.month - mes_primeira_cobranca
    meses_passados = (diferenca_anos * 12) + diferenca_meses

    
    # A parcela atual é os meses que passaram + 1 (a parcela inicial)
    parcela_atual = meses_passados + 1
    
    try:
        data_pagamento = data_alvo.replace(day=dia_vencimento)
    except ValueError:
        # Prevenção de erro: Se o vencimento for dia 31 e o mês alvo for Fevereiro (28)
        ultimo_dia = calendar.monthrange(data_alvo.year, data_alvo.month)[1]
        data_pagamento = data_alvo.replace(day=ultimo_dia)

    # 3. Validações de segurança
    if parcela_atual < 1:
        # Se for menor que 1, a cobrança ainda não chegou neste mês alvo
        return f"0/{total_parcelas}", False, data_pagamento #a vencer
        
    elif parcela_atual > total_parcelas:
        # Já acabou de pagar antes deste mês alvo
        return f"{total_parcelas}/{total_parcelas}", False, data_pagamento #quitado
        
    else:
        # Está na janela de pagamento! Vai pra tabela!
        return f"{parcela_atual}/{total_parcelas}", True, data_pagamento
    


def controle_data_parc_cc(data_compra_obj, dia_fechamento, dia_vencimento, total_parcelas, vigente=True, data_atual=None):
    """
    Retorna: (string_parcela, deve_aparecer_na_tabela, data_pagamento_exata)
    """
    if data_atual is None:
        data_atual = datetime.now()
        
    # Define qual é a FATURA ALVO (Mês Atual ou Próximo Mês)
    if vigente:
        data_alvo = data_atual
    else:
        data_alvo = data_atual + relativedelta(months=1)
        
    # Descobre a Fatura da PRIMEIRA cobrança (com base no fechamento)
    primeira_cobranca = data_compra_obj
    if data_compra_obj.day >= dia_fechamento: # Se comprou no dia do fechamento ou depois, vai pro outro mês
        primeira_cobranca += relativedelta(months=1)

    # Quantos meses se passaram entre a 1ª Cobrança e a Fatura Alvo?
    diferenca_anos = data_alvo.year - primeira_cobranca.year
    diferenca_meses = data_alvo.month - primeira_cobranca.month
    meses_passados = (diferenca_anos * 12) + diferenca_meses

    # A parcela atual nesta fatura alvo
    parcela_atual = meses_passados + 1
    
    # Monta a data de vencimento exata desta fatura
    try:
        data_pagamento = data_alvo.replace(day=dia_vencimento)
    except ValueError:
        # Prevenção de erro: Se o vencimento for dia 31 e o mês alvo for Fevereiro (28)
        ultimo_dia = calendar.monthrange(data_alvo.year, data_alvo.month)[1]
        data_pagamento = data_alvo.replace(day=ultimo_dia)

    # Filtros para saber se a despesa entra na tabela
    if parcela_atual < 1:
        # Se for menor que 1, a cobrança ainda não chegou neste mês alvo
        return f"0/{total_parcelas} (A vencer)", False, data_pagamento
        
    elif parcela_atual > total_parcelas:
        # Já acabou de pagar antes deste mês alvo
        return f"{total_parcelas}/{total_parcelas} (Quitado)", False, data_pagamento
        
    else:
        # Está na janela de pagamento! Vai pra tabela!
        return f"{parcela_atual}/{total_parcelas}", True, data_pagamento