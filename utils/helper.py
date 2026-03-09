from datetime import datetime
from dateutil.relativedelta import relativedelta


def gerar_opcoes_meses():
    meses_nome = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 
                  5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 
                  9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
    hoje = datetime.now()
    opcoes = []
    for i in range(12):
        data = hoje + relativedelta(months=i)
        opcoes.append(f"{meses_nome[data.month]}/{data.year}")
    return opcoes


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
def controle_data_parc(data_compra_obj, primeira_parc, total_parcelas, data_atual=None):
    """
    Calcula a parcela atual baseada na data de compra e no fechamento da fatura.
    Retorna uma string no formato 'Atual/Total' (ex: '3/12').
    """
    if data_atual is None:
        data_atual = datetime.now()
    
    controle_mes =  None
        
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

    #Se ainda não chegou o dia do fechamento neste mês, 
    # não viramos a parcela ainda!
    if data_atual.day <= primeira_parc.day:
        meses_passados -= 1
        controle_mes = False
    else:
        meses_passados += 1
        controle_mes = data_atual + relativedelta(months=1)
    
    # A parcela atual é os meses que passaram + 1 (a parcela inicial)
    parcela_atual = meses_passados + 1
    
    # 3. Validações de segurança
    if parcela_atual < 1:
        return f"0/{total_parcelas}", True, controle_mes   #str (A vencer)
    elif parcela_atual > total_parcelas:
        return f"{total_parcelas}/{total_parcelas}", False, controle_mes  # str  (Quitado)
    else:
        return f"{parcela_atual}/{total_parcelas}", True, controle_mes