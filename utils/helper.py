"""
Módulo Helper (Utilitários e Regras de Negócio Globais)

Concentra funções auxiliares para formatação de dados (moeda, data, cores), 
validação de entradas na interface gráfica e os motores de cálculo de 
vencimentos e parcelamentos do sistema financeiro.
"""

# ---------------------------------- IMPORTAÇÃO - MÓDULOS LOCAIS ------------------------------------

# ----- BANCO DE DADOS ------
from models.database import Database
from models.repositorios import *

# ----- FUNÇÕES DE AJUDA - (UTILS) -------
from utils.audio_helper import tocar_notificacao

# ------------------------------ IMPORTAÇÃO - MÓDULOS BIBLIOTECAS ---------------------------------
#BILIO PADRÕES
from datetime import datetime, date
import calendar
import re
from typing import List, Dict, Optional, Union, Any, Tuple

#BIBLIO VIA PIP
from dateutil.relativedelta import relativedelta
import holidays 



# =================================================================================
# -------- OPÇÕES MESES ----------
# =================================================================================

def gerar_opcoes_meses(id: Optional[int] = None, str_mes: Optional[str] = None) -> Union[str, int, Dict[int, str]]:
    """
    Converte identificadores de meses para seus nomes em string e vice-versa.
    Se nenhum argumento for passado, retorna o dicionário completo.

    Args:
        id (Optional[int]): O número do mês (1 a 12).
        str_mes (Optional[str]): O nome do mês (ex: "Janeiro").

    Returns:
        Union[str, int, Dict[int, str]]: O nome do mês, o ID numérico ou o dicionário mapeado.
    """
    meses_nome = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    
    if id:
        return meses_nome[id]
    
    if str_mes: 
        for chave, valor in meses_nome.items():
            if valor == str_mes:
                return chave

    return meses_nome


def preparar_dados_completos_cartao(id_user: int, dados_cartoes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transforma uma lista simples de cartões em uma lista robusta (DTO), 
    agregando todas as despesas e assinaturas vinculadas a cada cartão.

    Args:
        id_user (int): O ID do usuário logado.
        dados_cartoes (List[Dict[str, Any]]): Lista com os dados brutos dos cartões.

    Returns:
        List[Dict[str, Any]]: Lista de dicionários contendo informações do cartão, despesas e assinaturas.
    """
    db_conn = Database()
    rep_despesa = Rep_Despesa(db_conn)
    rep_assinatura = Rep_Assinatura(db_conn)

    dados_completos = []
    
    for cartao in dados_cartoes:
        id_card = cartao['id_cartao']
        
        despesas = rep_despesa.pega_despesas_cartao(id_user, id_card)
        assinaturas = rep_assinatura.pega_assinaturas_cartao(id_user, id_card)
        
        dados_completos.append({
            'info': cartao,
            'despesas': despesas,
            'assinaturas': assinaturas,
        })
        
    return dados_completos


# =================================================================================
# -------- VALIDAÇÃO DE ENTRADA ----------
# =================================================================================

def check_entry_num(P: str) -> bool:
    """
    Callback de validação para widgets Entry (Tkinter/CustomTkinter).
    Garante que o usuário digite apenas formatos monetários válidos.

    Args:
        P (str): O valor futuro do campo, caso o keystroke seja aceito pela UI.

    Returns:
        bool: True se o caractere for válido, False caso contrário (toca notificação de erro).
    """
    placeholders_permitidos = [
        "",             # Permite apagar tudo
        "R$ 0,00",      # Placeholder de Despesas/Receitas
        "Ex: 4500.00",  # Placeholder da Renda Fixa
    ]

    if P in placeholders_permitidos: # Correção implícita recomendada: 'in' no lugar de '=='
        return True
    
    # Regex: aceita números, opcionalmente um ponto ou vírgula, e mais números
    padrao = r'^[0-9]*[.,]?[0-9]*$'
    
    if re.match(padrao, P):
        return True
    else:
        tocar_notificacao('erro')
        return False


# =================================================================================
# -------- FORMATAÇÃO DE CORES ----------
# =================================================================================

def formata_cor(nome_cor: Optional[str] = None, cor: Optional[str] = None) -> str:
    """
    Traduz os nomes de cores exibidos na UI para códigos HEX usados no banco, 
    ou reverte códigos HEX para nomes legíveis.

    Args:
        nome_cor (Optional[str]): O nome da cor (ex: 'Roxo').
        cor (Optional[str]): O código hexadecimal da cor (ex: '#b20398').

    Returns:
        str: O equivalente em HEX (se nome fornecido) ou o nome em texto (se HEX fornecido).
    """
    if nome_cor:
        if nome_cor == 'Laranja': return "#ff9500"
        elif nome_cor == 'Roxo': return "#b20398"
        elif nome_cor == 'Preto': return "#000000"
        elif nome_cor == 'Vermelho': return "#dd0404"
        elif nome_cor == 'Cinza': return "#616161"
        elif nome_cor == 'Verde': return "#2CBA00"
        else:
            print('Cor selecionada não está registrada!')
            return '' # Retorno de segurança
        
    elif cor:
        if cor == "#ff9500": return 'Laranja'
        elif cor == "#b20398": return 'Roxo'
        elif cor == "#000000": return "Preto"
        elif cor == "#dd0404": return 'Vermelho'
        elif cor == "#616161": return 'Cinza'
        elif cor == "#2CBA00": return 'Verde'
        else:
            print("Campo 'Cor' do db veio nula, retornando 'Sem Cor'")
            return 'Sem Cor'
        
    else:
        return 'Sem Cor'
    

# =================================================================================
# -------- FORMATAÇÃO DE DATAS --------
# =================================================================================

def str_para_data(data_str: str) -> Optional[datetime]:
    """
    Converte uma string brasileira em um objeto datetime.

    Args:
        data_str (str): Data no formato 'DD/MM/AAAA'.

    Returns:
        Optional[datetime]: Objeto convertido ou None em caso de falha.
    """
    try:
        return datetime.strptime(data_str, "%d/%m/%Y")
    except ValueError:
        print(f"Erro: Formato de data inválido ({data_str})")
        return None


def data_para_exibicao(data_obj: Union[datetime, date, str, None]) -> str:
    """
    Formata objetos datetime para o padrão de leitura da UI brasileira.

    Args:
        data_obj: Objeto de data a ser formatado.

    Returns:
        str: Data no formato 'DD/MM/AAAA', ou string vazia se nulo.
    """
    if data_obj and hasattr(data_obj, "strftime"):
        return data_obj.strftime("%d/%m/%Y")
    return ""


def data_para_mysql(data_obj: Union[datetime, date, None]) -> Optional[str]:
    """
    Formata objetos datetime para a inserção padronizada no MySQL.

    Args:
        data_obj: Objeto de data a ser formatado.

    Returns:
        Optional[str]: String no formato 'YYYY-MM-DD', ou None se nulo.
    """
    if data_obj and hasattr(data_obj, "strftime"):
        return data_obj.strftime("%Y-%m-%d")
    return None


def mysql_para_obj(data_mysql: Union[str, datetime, date, None]) -> Union[datetime, date, None]:
    """
    Reidrata a string devolvida pelo MySQL transformando-a novamente em datetime.

    Args:
        data_mysql: A data extraída do banco de dados.

    Returns:
        Union[datetime, date, None]: O objeto datetime resultante.
    """
    if isinstance(data_mysql, str):
        try:
            return datetime.strptime(data_mysql, "%Y-%m-%d")
        except ValueError:
            print(f"Erro: Formato MySQL inválido ({data_mysql})")
            return None
    return data_mysql


# =================================================================================
# --------- FORMATAÇÃO DE MOEDA -------------
# =================================================================================

def formatar_moeda(valor: Union[float, Decimal, int]) -> str:
    """
    Formata números brutos para a representação monetária brasileira (BRL).

    Args:
        valor: Valor numérico a ser formatado.

    Returns:
        str: Representação no formato 'R$ X.XXX,XX'.
    """
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# =================================================================================
# ---------- CENTRALIZAR JANELA TKINTER ------------
# =================================================================================

def centralizar_janela_responsiva(janela: Any, tipo_janela: str = "main") -> None:
    """
    Centraliza e redimensiona a janela dinamicamente adaptando-se 
    ao tamanho do monitor detectado (Notebook vs Monitor Grande).

    Args:
        janela (Any): A instância da janela ou frame principal (Tk/CTk).
        tipo_janela (str): Identificador do tipo de tela para definir as proporções de escalonamento.
    """
    janela.update_idletasks()
    
    largura_tela = janela.winfo_screenwidth()
    altura_tela = janela.winfo_screenheight()

    if tipo_janela == "main":
        if largura_tela <= 1920:
            pct_largura = 0.90
            pct_altura = 0.82
        else:
            pct_largura = 0.60
            pct_altura = 0.60
            
    elif tipo_janela == "login":
        pct_largura = 0.15 if largura_tela > 1920 else 0.25
        pct_altura = 0.30 if altura_tela > 1080 else 0.45
        
    elif tipo_janela == 'despass':
        pct_largura = 0.70 if largura_tela > 1920 else 0.99
        pct_altura = 0.60 if altura_tela > 1080 else 0.80

    elif tipo_janela == 'medio':
        pct_largura = 0.40 if largura_tela > 1920 else 0.67
        pct_altura = 0.50 if altura_tela > 1080 else 0.73
    
    elif tipo_janela == 'pequeno':
        pct_largura = 0.20 if largura_tela > 1920 else 0.30
        pct_altura = 0.15 if altura_tela > 1080 else 0.20
    
    else:
        pct_largura = 0.55 if largura_tela > 1920 else 0.75
        pct_altura = 0.50 if altura_tela > 1080 else 0.70


    largura_final = int(largura_tela * pct_largura)
    altura_final = int(altura_tela * pct_altura)

    pos_x = (largura_tela // 2) - (largura_final // 2)
    pos_y = (altura_tela // 2) - (altura_final // 2)

    janela.geometry(f"{largura_final}x{altura_final}+{pos_x}+{pos_y}")


# =================================================================================
# ---------- ENGINES: CONTROLE DE DATA E PARCELAS -----------------
# =================================================================================



def obter_proximo_dia_util(data_base: datetime.date) -> datetime.date:
    """
    Recebe uma data e, se ela cair em um final de semana (sábado/domingo) 
    ou feriado nacional brasileiro, empurra consecutivamente para o próximo dia útil.
    """
    # Instancia os feriados do Brasil
    feriados_br = holidays.Brazil()
    data_aux = data_base

    # Loop continua enquanto for sábado (5), domingo (6) ou estiver na lista de feriados
    while data_aux.weekday() in (5, 6) or data_aux in feriados_br:
        data_aux += datetime.timedelta(days=1)
        
    return data_aux


def calcular_datas_reais_cartao(ano: int, mes: int, dia_vencimento_fixo: int, dia_fechamento_nominal: int) -> Tuple[datetime.date, datetime.date]:
    """
    Calcula o vencimento e o fechamento reais para um determinado mês/ano.
    
    A janela de dias corridos entre o fechamento nominal e o vencimento é preservada,
    e o vencimento real é ajustado para dias úteis (sábados, domingos e feriados).
    """
    # 1. Calcular a janela original de dias corridos entre fechamento e vencimento
    # Tratando o caso comum onde o fechamento nominal é no mês anterior ao vencimento (ex: fecha 25, vence 05)

    if dia_fechamento_nominal > dia_vencimento_fixo:
        # Cria uma data fictícia de vencimento e fechamento para calcular a diferença de dias
        data_v_ficticia = datetime.date(2026, 2, dia_vencimento_fixo)
        data_f_ficticia = datetime.date(2026, 1, dia_fechamento_nominal)
        janela_dias = (data_v_ficticia - data_f_ficticia).days
    else:
        janela_dias = dia_vencimento_fixo - dia_fechamento_nominal

    # 2. Construir o vencimento nominal para o mês solicitado
    # Proteção defensiva para meses que não possuem o dia fixo (ex: dia 31 em meses de 30 dias ou fevereiro)
    ano_alvo = ano
    mes_alvo = mes
    dia_alvo = dia_vencimento_fixo
    
    while True:
        try:
            data_vencimento_nominal = datetime.date(ano_alvo, mes_alvo, dia_alvo)
            break
        except ValueError:
            # Se o dia estourar o mês, reduz o dia em 1 até encontrar o último dia válido do mês (ex: 28 de fevereiro)
            dia_alvo -= 1

    # 3. Aplicar a regra de dias úteis no Vencimento (Finais de semana e Feriados pulam para frente)
    data_vencimento_real = obter_proximo_dia_util(data_vencimento_nominal)

    # 4. Calcular o Fechamento Real subtraindo a janela de dias corridos do Vencimento Real
    # Isso garante que se o vencimento pulou por causa de um feriado, o fechamento acompanha a flutuação!
    data_fechamento_real = data_vencimento_real - datetime.timedelta(days=janela_dias)

    return data_fechamento_real, data_vencimento_real




def controle_data_parc(
    data_pp: datetime, 
    dia_vencimento: int, 
    total_parcelas: Optional[int] = None, 
    controle_mes: Optional[int] = None, 
    data_atual: Optional[datetime] = None
) -> Tuple[str, bool, datetime]:
    """
    Motor de processamento de regras de negócio para Despesas Avulsas e Assinaturas.
    Calcula a exibição correta da parcela (Ex: '2/10') e define se o registro deve aparecer 
    no dashboard no mês em questão.

    Args:
        data_pp (datetime): Data do Primeiro Pagamento cadastrado.
        dia_vencimento (int): Dia padrão em que a cobrança cai.
        total_parcelas (Optional[int]): Total de cotas da compra (se None, assume-se como Assinatura contínua).
        controle_mes (Optional[int]): O mês referencial do filtro ativo na UI.
        data_atual (Optional[datetime]): Mock injetável para a data de "Hoje" (usado para testes ou fallback).

    Returns:
        Tuple[str, bool, datetime]: Retorna a label da parcela, a flag indicando se a despesa
        deve estar visível no mês atual, e o objeto date final do pagamento.
    """
    if data_atual is None:
        data_atual = datetime.now().date() # type: ignore
    
    assinatura = False

    if total_parcelas is None:
        assinatura = True

    mes_vigente = data_atual.month
    prox_mes = (data_atual + relativedelta(months=1)).month
    seg_prox_mes = (data_atual + relativedelta(months=2)).month
    ter_prox_mes = (data_atual + relativedelta(months=3)).month
    quart_prox_mes = (data_atual + relativedelta(months=4)).month
    quint_prox_mes = (data_atual + relativedelta(months=5)).month

    # Nota: Risco de 'UnboundLocalError' caso controle_mes > quint_prox_mes
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
    elif controle_mes == quint_prox_mes:
        data_alvo = (data_atual + relativedelta(months=5))
        
    mes_primeira_cobranca = data_pp.month
    ano_primeira_cobranca = data_pp.year
            
    if not assinatura:
        diferenca_anos = data_alvo.year - ano_primeira_cobranca # type: ignore
        diferenca_meses = data_alvo.month - mes_primeira_cobranca # type: ignore
        meses_passados = (diferenca_anos * 12) + diferenca_meses
    
        parcela_atual = meses_passados + 1

    try:
        data_pagamento = data_alvo.replace(day=dia_vencimento) # type: ignore

    except ValueError:
        ultimo_dia = calendar.monthrange(data_alvo.year, data_alvo.month)[1] # type: ignore
        data_pagamento = data_alvo.replace(day=ultimo_dia) # type: ignore

    if assinatura:
        data_inicio_cobranca = data_pp.replace(day=1)
        data_alvo_inicio = data_alvo.replace(day=1) # type: ignore

        if data_alvo_inicio >= data_inicio_cobranca:
            return "Mensal", True, data_pagamento
        else:
            return "Mensal", False, data_pagamento
        
    if not assinatura:
        if parcela_atual < 1: # type: ignore
            return f"0/{total_parcelas}", False, data_pagamento 
    
        elif parcela_atual > total_parcelas: # type: ignore
            return f"{total_parcelas}/{total_parcelas}", False, data_pagamento 
        
        else:
            return f"{parcela_atual}/{total_parcelas}", True, data_pagamento # type: ignore


def controle_data_parc_cc(
    data_compra_obj: datetime, 
    dia_fechamento: int, 
    dia_vencimento: int, 
    total_parcelas: Optional[int] = None, 
    controle_mes: Optional[int] = None, 
    data_atual: Optional[datetime] = None
) -> Tuple[str, bool, datetime]:
    
    """
    Motor de processamento de regras de negócio para Cartões de Crédito.
    Identifica "pulos de fatura" de acordo com o fechamento do cartão (Ex: Melhor dia de compra).

    Args:
        data_compra_obj (datetime): Data de execução da compra.
        dia_fechamento (int): Dia de virada/corte da fatura.
        dia_vencimento (int): Dia final de pagamento.
        total_parcelas (Optional[int]): Total de parcelas (None para assinaturas).
        controle_mes (Optional[int]): Mês do filtro ativo.
        data_atual (Optional[datetime]): Mock data atual.

    Returns:
        Tuple[str, bool, datetime]: Label de exibição da parcela, controle de visibilidade (bool) 
        e data exata de vencimento no mês.
    """
    if data_atual is None:
        data_atual = datetime.now().date() # type: ignore

    assinatura = False

    if total_parcelas is None:
        assinatura = True
    
    mes_vigente = data_atual.month
    prox_mes = (data_atual + relativedelta(months=1)).month
    seg_prox_mes = (data_atual + relativedelta(months=2)).month
    ter_prox_mes = (data_atual + relativedelta(months=3)).month
    quart_prox_mes = (data_atual + relativedelta(months=4)).month
    quint_prox_mes = (data_atual + relativedelta(months=5)).month

    data_alvo = None

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
    elif controle_mes == quint_prox_mes:
        data_alvo = (data_atual + relativedelta(months=5))
        
    primeira_cobranca = data_compra_obj

    if dia_fechamento > dia_vencimento: #ATENÇÃO: Se o cartão vence antes do dia 12, com certeza a fatura dele fecha no mês anterior! 
        fech_dc = primeira_cobranca.month - 1

        if fech_dc == 0:
            fech_dc = 12

        data_fechamento = data_compra_obj.replace(day=dia_fechamento, month=fech_dc)
    else:
        data_fechamento = data_compra_obj.replace(day=dia_fechamento)

    if data_compra_obj >= data_fechamento: 
        primeira_cobranca += relativedelta(months=1)

    if not assinatura:
        diferenca_anos = data_alvo.year - primeira_cobranca.year # type: ignore
        diferenca_meses = data_alvo.month - primeira_cobranca.month # type: ignore
        meses_passados = (diferenca_anos * 12) + diferenca_meses

        parcela_atual = meses_passados + 1
    
    try:
        data_pagamento = data_alvo.replace(day=dia_vencimento) # type: ignore
        
    except ValueError:
        ultimo_dia = calendar.monthrange(data_alvo.year, data_alvo.month)[1] # type: ignore
        data_pagamento = data_alvo.replace(day=ultimo_dia) # type: ignore

    if assinatura:
        data_inicio_cobranca = primeira_cobranca.replace(day=1)
        data_alvo_inicio = data_alvo.replace(day=1) # type: ignore

        if data_alvo_inicio >= data_inicio_cobranca:
            return "Mensal", True, data_pagamento
        else:
            return "Mensal", False, data_pagamento
    
    if not assinatura:
        if parcela_atual < 1: # type: ignore
            return f"0/{total_parcelas} (A vencer)", False, data_pagamento
        
        elif parcela_atual > total_parcelas: # type: ignore
            return f"{total_parcelas}/{total_parcelas} (Quitado)", False, data_pagamento
        
        else:
            return f"{parcela_atual}/{total_parcelas}", True, data_pagamento # type: ignore