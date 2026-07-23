"""
Módulo CRUD App (Gerenciamento de Janelas e Controladores)

Este módulo atua como a camada Controller do padrão MVC. Ele contém o `CrudManage` 
(Fábrica de Janelas) e as classes Toplevel (pop-ups) que integram os formulários (forms.py), 
as listagens (detalhar.py) e os repositórios do banco de dados, controlando o fluxo de 
inserção, atualização e exclusão de dados na interface.
"""

# ---------------------------------- IMPORTAÇÃO - MÓDULOS LOCAIS ------------------------------------
# ----- BANCO DE DADOS (models) ------
from models.database import Database
from models.repositorios import *

#------ IMPORTAÇÃO DE CLASSES PARA CADASTRO - (forms.py) --------
from ui.forms import *

#------ IMPORTAÇÃO DE CLASSES PARA LISTAGEM - (detalhar.py) --------
from ui.detalhar import *

#------ IMPORTAÇÃO DE CLASSES TYPEDDICT - (typedDict.py) --------
from utils.typedDict import *

# ----- FUNÇÕES DE AJUDA - (helper.py/audio_helper.py) -------
from utils.helper import(centralizar_janela_responsiva, gerar_opcoes_meses, formatar_moeda, mysql_para_obj, data_para_exibicao, formata_cor)
from utils.audio_helper import(tocar_notificacao)

# ------------------------------ IMPORTAÇÃO - MÓDULOS BIBLIOTECAS ---------------------------------
#BILIO PADRÕES
from typing import List, Optional, Callable, Any, Dict
from datetime import datetime

#BIBLIO VIA PIP
import customtkinter as ctk
from dateutil.relativedelta import relativedelta

# ------------- CONFIGURAÇÃO INICIAL ---------------
ctk.set_appearance_mode('dark')


# =================================================================================
# -1° MÓDULO: CrudManage - GERENCIADOR DE JANELAS (FACTORY)
# =================================================================================

class CrudManage:
    """
    Fábrica responsável por instanciar e abrir todas as janelas secundárias (Pop-ups/Toplevel).
    Armazena o estado global (dados do usuário logado) e repassa para as telas filhas.
    """

    def __init__(
            self, 
            parent: Any = None,
            # ------- dependências de dados
            user_id: Optional[int] = None, 
            dados_usuario: Optional[List[Dict[str, Any]]] = None, 
            dados_receitas: Optional[List[Dict[str, Any]]] = None, 
            dados_cartoes: Optional[List[Dict[str, Any]]] = None, 
            nomes_cartoes: Optional[List[str]] = None, 
            despesas_avulsas: Optional[List[Dict[str, Any]]] = None, 
            assinaturas_avulsas: Optional[List[Dict[str, Any]]] = None, 
            dados_prontos: Optional[List[Dict[str, Any]]] = None,
            # ------- callbacks (Eventos disparados entre janelas)
            cb_atualiza_bd: Optional[Callable] = None, 
            cb_vcmd_num: Optional[Callable] = None, 
            cb_att_app: Optional[Callable] = None, 
            cb_trocar_mes: Optional[Callable] = None
        ) -> None:
        
        self.parent = parent
        self.user_id = user_id
        self.dados_usuario = dados_usuario
        self.dados_receitas = dados_receitas
        self.dados_cartoes = dados_cartoes
        self.nomes_cartoes = nomes_cartoes
        self.despesas_avulsas = despesas_avulsas
        self.assinaturas_avulsas = assinaturas_avulsas
        self.dados_prontos = dados_prontos

        #------ callbacks mapeados
        self.atualiza_bd = cb_atualiza_bd # vem do login_app
        self.vcmd_num = cb_vcmd_num       # vem do login_app e main_app
        self.att_app = cb_att_app         # vem do main_app
        self.trocar_mes = cb_trocar_mes   # vem do main_app


    def tela_usuarios(self) -> None:
        """Abre a janela de cadastro e gerenciamento de novos usuários."""
        tocar_notificacao("open_w", True)
        register_window = Usuarios(parent=self.parent, cb_atualiza_bd=self.atualiza_bd, cb_vcmd_num=self.vcmd_num)
        self.parent.wait_window(register_window)

    def tela_receitas(self) -> None:
        """Abre a janela de CRUD de Receitas."""
        tocar_notificacao('open_w', True)
        register_window = Receitas(parent=self.parent, user_id=self.user_id, dados_receitas=self.dados_receitas, att_app=self.att_app, cb_vcmd_num=self.vcmd_num)
        self.parent.wait_window(register_window) 

    def tela_despesas(self) -> None:
        """Abre a janela de CRUD de Despesas avulsas e parceladas."""
        tocar_notificacao('open_w', True)
        register_window = Despesas(parent=self.parent, user_id=self.user_id, dados_cartoes=self.dados_cartoes, cb_trocar_mes=self.trocar_mes, cb_att_app=self.att_app, cb_vcmd_num=self.vcmd_num)
        self.parent.wait_window(register_window)

    def tela_car_cred(self) -> None:
        """Abre a janela de CRUD de Cartões de Crédito."""
        tocar_notificacao('open_w', True)
        register_window = Car_cred(parent=self.parent, user_id=self.user_id, dados_cartoes=self.dados_cartoes, nomes_cards=self.nomes_cartoes, cb_att_app=self.att_app, cb_vcmd_num=self.vcmd_num)
        self.parent.wait_window(register_window)

    def tela_assinaturas(self) -> None:
        """Abre a janela de CRUD de Assinaturas/Recorrências."""
        tocar_notificacao('open_w', True)
        register_window = Assinaturas(parent=self.parent, user_id=self.user_id, dados_cartoes=self.dados_cartoes, cb_att_app=self.att_app, cb_vcmd_num=self.vcmd_num)
        self.parent.wait_window(register_window)
        
    def tela_simulacao(self) -> None:
        """Abre o ambiente Sandbox para simulação de impacto de novas despesas."""
        tocar_notificacao('open_w', True)
        register_window = Simulacao(parent=self.parent, id_user=self.user_id, despesas_avulsas=self.despesas_avulsas, assinaturas_avulsas=self.assinaturas_avulsas, dados_cartoes=self.dados_cartoes, dados_usuario=self.dados_usuario, nomes_cartoes=self.nomes_cartoes, dados_prontos=self.dados_prontos, cb_vcmd_num=self.vcmd_num)
        self.parent.wait_window(register_window) 

    def tela_faturas(self, nome_select: Optional[str] = None) -> None:
        """
        Abre a visão detalhada (Fatura Fechada/Aberta) de um cartão específico.
        
        Args:
            nome_select (str): Nome do cartão selecionado no dropdown da Main_app.
        """
        tocar_notificacao('open_w', True)
        id_card = [card['id_cartao'] for card in self.dados_cartoes if card['nome_cartao'] == nome_select]

        if id_card:
            register_window = Faturas(parent=self.parent, id_user=self.user_id, id_card=id_card[0], nome_card=nome_select, dados_card=self.dados_cartoes, dados_prontos=self.dados_prontos)
            self.parent.wait_window(register_window)
        else:
            print('ERRO: ID card não encontrado!')


# =================================================================================
# -2° MÓDULO: Usuarios
# =================================================================================

class Usuarios(ctk.CTkToplevel):
    """Interface de criação e gestão de usuários (Login/Senha)."""

    def __init__(self, parent: Any = None, cb_atualiza_bd: Optional[Callable] = None, cb_vcmd_num: Optional[Callable] = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
    
        self.parent = parent 
        self.atualiza_bd = cb_atualiza_bd
        self.vcmd_num = cb_vcmd_num

        self.db_conn = Database()
        self.db = Rep_Usuario(self.db_conn)

        self.title("Registrar Novo Usuário")
        centralizar_janela_responsiva(janela=self, tipo_janela='medio')
        self.transient(parent) 
        self.grab_set() 
        self.focus_set()

        self.grid_columnconfigure(0, weight=1) 

        # ---------------- Gerencimento ---------------------
        self.dados_usuarios = self.db.dados_usuarios()
        self.nome_users = [dado['nome_user'] for dado in self.dados_usuarios]

        # ---------------- Frame Cadastro ------------------------
        self.frame_cadastro = Cadastrar_usuario(self, cb_comandante_crud=self.comandante_crud, cb_fechar=self.fechar, nome_users=self.nome_users, cb_vcmd_num=self.vcmd_num)
        self.frame_cadastro.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")


    def comandante_crud(self, inserir: Optional[Usuario] = None) -> Optional[bool]:
        """Recebe o objeto de formulário e orquestra a inserção no banco."""
        sucesso = None
        if inserir:
            sucesso = self.db.inserir_usuario(usuario=inserir)
        
        if sucesso:
            tocar_notificacao("dv_sucesso", True)
            self.atualiza_bd()
        else:
            tocar_notificacao("dv_erro", True)
        
        return sucesso

    def fechar(self) -> None:
        """Destroi a Toplevel de forma limpa."""
        self.destroy()
        

# =================================================================================
# -3° MÓDULO: Receitas
# =================================================================================

class Receitas(ctk.CTkToplevel): 
    """Interface para visualização, inserção, edição e exclusão de Rendas Variáveis."""

    def __init__(self, parent: Any = None, user_id: Optional[int] = None, dados_receitas: Optional[List] = None, att_app: Optional[Callable] = None, cb_vcmd_num: Optional[Callable] = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.user_id = user_id
        self.dados_receitas = dados_receitas
        self.att_app = att_app
        self.vcmd_num = cb_vcmd_num

        self.db_conn= Database()
        self.db = Rep_Receita(self.db_conn)

        self.title("Gerenciar Receitas")
        centralizar_janela_responsiva(janela=self, tipo_janela='medio')
        self.transient(self.parent) 
        self.focus_set() 

        # ---------------- Gerencimento de self ---------------------
        self.data_atual = datetime.now().date()
        self.notifica_delete = False

        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=2) 
        self.grid_rowconfigure(0, weight=1)

        # ---------- formulário de cadastro -----------------------
        self.frame_cadastro = Cadastrar_receita(parent=self, user_id=self.user_id, callback_comandante_crud=self.comandante_crud, cb_vcmd_num=self.vcmd_num)
        self.frame_cadastro.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        #-------------- FRAME DA LISTA (Update/Delete) --------------------------
        self.frame_lista = Listar_receitas(parent=self, user_id=self.user_id, dados_receitas=self.dados_receitas, controle_dados=self.controle_dados, callback_comandante_crud=self.comandante_crud)
        self.frame_lista.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.frame_lista.grid_columnconfigure(0, weight=1)
        

    def comandante_crud(self, inserir: Optional[Receita] = None, atualizar: Optional[Receita] = None, deletar: Optional[int] = None) -> Optional[bool]:
        """Roteador principal de transações (CRUD) para a entidade Receita."""

        sucesso = None

        if inserir:
            sucesso = self.db.inserir_receita(id_user=self.user_id, receita=inserir)
        elif atualizar:
            sucesso = self.db.atualizar_receita(receita=atualizar)
        elif deletar:
            self.notifica_delete = True
            sucesso = self.db.deletar_receita(id_rec=deletar)
            
        if sucesso:
            self.definicao_sucesso()
        else:
            self.definicao_insucesso()

        return sucesso
    

    def definicao_sucesso(self) -> None:
        """Gatilho visual e sonoro de sucesso + Update assíncrono do Dashboard."""
        if not self.notifica_delete:
            tocar_notificacao("dv_sucesso", True)
        else:
            tocar_notificacao('dv_delete', True)

        if self.att_app:
            new_dados = self.att_app()
            self.dados_receitas = new_dados['dados_receitas']
        
        self.update()
        self.frame_lista.listar(dados_receitas=self.dados_receitas)
        self.frame_cadastro.limpa_campos()

    def definicao_insucesso(self) -> None:
        """Gatilho de falha de validação ou erro de banco."""
        tocar_notificacao("dv_erro", True)

    def controle_dados(self, dados: Optional[Dict] = None) -> None:
        """Repassa os dados selecionados na tabela para edição no formulário."""
        if dados:
            self.frame_cadastro.controla_campos(dados)
        else:
            print('ERRO: detalhar.py(Listar_receitas) não enviou os dados')
        

# =================================================================================
# -4° MÓDULO: Despesas
# =================================================================================

class Despesas(ctk.CTkToplevel):
    """Interface principal para lançamento e edição de Despesas gerais."""

    def __init__(self, parent: Any = None, user_id: Optional[int] = None, dados_cartoes: Optional[List] = None, cb_trocar_mes: Optional[Callable] = None, cb_att_app: Optional[Callable] = None, cb_vcmd_num: Optional[Callable] = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.dados_cartoes = dados_cartoes
        self.trocar_mes = cb_trocar_mes
        self.att_app = cb_att_app
        self.vcmd_num = cb_vcmd_num

        self.db_conn= Database()
        self.db = Rep_Despesa(self.db_conn)

        self.title("Gerenciar Despesas")
        centralizar_janela_responsiva(janela=self, tipo_janela='despass')
        self.transient(parent)
        self.focus_set() 

        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=7) 
        self.grid_rowconfigure(0, weight=1)

        # ---------------- Gerencimento ---------------------
        self.data_atual = datetime.now().date()
        self.dados_despesas = self.db.dados_despesas(self.user_id)
        self.notifica_delete = False

        # ---------- formulário de cadastro -----------------------
        self.frame_cadastro = Cadastrar_despesa(parent=self, user_id=self.user_id, dados_cartoes=self.dados_cartoes, cb_comandante_crud=self.comandante_crud, cb_vcmd_num=self.vcmd_num)
        self.frame_cadastro.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        #-------------------- FRAME DA LISTA (Update/Delete) ----------------------------------
        self.frame_lista = Listar_despesas(parent=self, user_id=self.user_id, dados_cartoes=self.dados_cartoes, dados_despesas=self.dados_despesas, controle_dados=self.controle_dados, cb_comandante_crud=self.comandante_crud)
        self.frame_lista.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.frame_lista.grid_columnconfigure(0, weight=1)


    def comandante_crud(self, inserir: Optional[Despesa] = None, atualizar: Optional[Despesa] = None, deletar: Optional[int] = None) -> Optional[bool]:
        """Controlador de transações CRUD para a entidade Despesa."""

        sucesso = None

        if inserir:
            sucesso = self.db.inserir_despesa(id_user=self.user_id, despesa=inserir)
        elif atualizar:
            sucesso = self.db.atualizar_despesa(despesa=atualizar)
        elif deletar:
            self.notifica_delete = True
            sucesso = self.db.deletar_despesa(id_desp=deletar)
            
        if sucesso:
            self.definicao_sucesso()
        else:
            self.definicao_insucesso()

        return sucesso
    

    def definicao_sucesso(self) -> None:
        """Confirmação de transação e reload da grid."""
        if not self.notifica_delete:
            tocar_notificacao("dv_sucesso", True)
        else:
            tocar_notificacao('dv_delete', True)

        if self.att_app:
            self.att_app()
        
        self.dados_despesas = self.db.dados_despesas(self.user_id)
        self.update()
        self.frame_lista.listar(dados_despesas=self.dados_despesas)
        self.frame_cadastro.limpa_campos()

    def definicao_insucesso(self) -> None:
        tocar_notificacao("dv_erro", True)

    def controle_dados(self, dados: Optional[Dict] = None) -> None:
        """Injeta dados selecionados da listagem para o painel de edição (Form)."""
        if dados:
            self.frame_cadastro.controla_campos(dados)
        else:
            print('ERRO: detalhar(despesas não mandou os dados esperados!)')


# =================================================================================
# -5° MÓDULO: Cartões de Crédito
# =================================================================================

class Car_cred(ctk.CTkToplevel):
    """Interface para gerenciamento de Cartões, bandeiras, dias de corte e limite."""

    def __init__(self, parent: Any = None, user_id: Optional[int] = None, dados_cartoes: Optional[List] = None, nomes_cards: Optional[List] = None, cb_att_app: Optional[Callable] = None, cb_vcmd_num: Optional[Callable] = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.nomes_cards = nomes_cards
        self.dados_cartoes = dados_cartoes
        self.vcmd_num = cb_vcmd_num
        self.att_app = cb_att_app

        self.db_conn= Database()
        self.db = Rep_Cartao_credito(self.db_conn)

        self.title("Gerenciar Cartões de Crédito")
        centralizar_janela_responsiva(janela=self, tipo_janela='outro')
        self.transient(parent)
        self.focus_set()

        self.data_atual = datetime.now().date()
        self.notifica_delete = False

        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=2) 
        self.grid_rowconfigure(0, weight=1)

         # ---------------- formulário de cadastro -----------------------
        self.frame_cadastro = Cadastrar_car_cred(parent=self, user_id=self.user_id, nomes_cards=self.nomes_cards, cb_comandante_crud=self.comandante_crud, cb_vcmd_num=self.vcmd_num)
        self.frame_cadastro.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        #------------------- FRAME DA LISTA (Update/Delete) ------------------------------
        self.frame_lista = Listar_car_cred(parent=self, user_id=self.user_id, dados_cartoes=self.dados_cartoes, controle_dados=self.controle_dados, cb_comandante_crud=self.comandante_crud)
        self.frame_lista.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.frame_lista.grid_columnconfigure(0, weight=1)


    def comandante_crud(self, inserir: Optional[Cartao_credito] = None, atualizar: Optional[Cartao_credito] = None, deletar: Optional[int] = None) -> Optional[bool]:
        """Mediador do fluxo de transação de Cartões de Crédito, com conversão HEX automática."""

        if inserir:
            inserir.cor = formata_cor(nome_cor=inserir.cor)
            sucesso = self.db.inserir_cc(id_user=self.user_id, cartao=inserir)

        elif atualizar:
            atualizar.cor = formata_cor(nome_cor=atualizar.cor)
            sucesso = self.db.atualizar_cartao(cartao=atualizar)

        elif deletar:
            self.notifica_delete = True
            sucesso =  self.db.deletar_cartao(id_card=deletar)

        if sucesso:
            self.definicao_sucesso()
        else:
            self.definicao_insucesso()
        
        return sucesso

    def definicao_sucesso(self) -> None:
        if not self.notifica_delete:
            tocar_notificacao("dv_sucesso", True)
        else:
            tocar_notificacao('dv_delete', True)

        if self.att_app:
            retorno = self.att_app()
            self.dados_cartoes = retorno['dados_cartoes']
        
        self.update()
        self.frame_lista.listar(dados_cartoes=self.dados_cartoes)
        self.frame_cadastro.limpa_campos()

    def definicao_insucesso(self) -> None:
        tocar_notificacao("dv_erro", True)

    def controle_dados(self, dados: Optional[Dict] = None) -> None:
        if dados:
            self.frame_cadastro.controla_campos(dados)
        else:
            print('ERRO: Detalhar(car_cred não mandou os dados esperados!)')
        

# =================================================================================
# -6° MÓDULO: Assinaturas
# =================================================================================

class Assinaturas(ctk.CTkToplevel):
    """Interface para gestão de débitos contínuos (Streamings, Lazer, Software)."""

    def __init__(self, parent: Any = None, user_id: Optional[int] = None, dados_cartoes: Optional[List] = None, cb_att_app: Optional[Callable] = None, cb_vcmd_num: Optional[Callable] = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.dados_cartoes = dados_cartoes
        self.att_app = cb_att_app
        self.vcmd_num = cb_vcmd_num

        self.db_conn= Database()
        self.db = Rep_Assinatura(self.db_conn)

        self.title("Gerenciar Assinaturas")
        centralizar_janela_responsiva(janela=self, tipo_janela='despass')
        self.transient(parent) 
        self.focus_set() 
       
        self.data_atual = datetime.now().date()
        # Assinaturas não têm fim por padrão (Simulado até +73 anos)
        self.data_futuro = (self.data_atual + relativedelta(years=73)).replace(day=1, month=1)
        self.dados_assinaturas = self.db.dados_assinaturas(self.user_id)
        self.notifica_delete = False

        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=4) 
        self.grid_rowconfigure(0, weight=1)

         # ---------------- formulário de cadastro -----------------------
        self.frame_cadastro = Cadastrar_assinatura(self, self.user_id, self.dados_cartoes, cb_comandante_crud=self.comandante_crud, cb_vcmd_num=self.vcmd_num)
        self.frame_cadastro.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        #------------------- FRAME DA LISTA (Update/Delete) ------------------------------
        self.frame_lista = Listar_assinaturas(self, self.user_id, self.dados_cartoes, self.dados_assinaturas, self.controle_dados, cb_comandante_crud=self.comandante_crud )
        self.frame_lista.grid(row=0, column=1, padx=(0,20), pady=20, sticky="nsew")
        self.frame_lista.grid_columnconfigure(0, weight=1)
        

    def comandante_crud(self, inserir: Optional[Assinatura] = None, atualizar: Optional[Assinatura] = None, deletar: Optional[int] = None) -> Optional[bool]:
        """Gerencia o disparo de inserts/updates de recorrências."""

        sucesso = None

        if inserir:
            sucesso = self.db.inserir_assinatura(id_user=self.user_id, assinatura=inserir)
        elif atualizar:
            sucesso = self.db.atualizar_assinatura(assinatura=atualizar)
        elif deletar:
            self.notifica_delete = True
            sucesso = self.db.deletar_assinatura(id_ass=deletar)
            
        if sucesso:
            self.definicao_sucesso()
        else:
            self.definicao_insucesso()

        return sucesso


    def definicao_sucesso(self) -> None:
        if not self.notifica_delete:
            tocar_notificacao("dv_sucesso", True)
        else:
            tocar_notificacao('dv_delete', True)

        if self.att_app:
            self.att_app()
        
        self.dados_assinaturas = self.db.dados_assinaturas(self.user_id)
        self.update()
        self.frame_lista.listar(dados_ass=self.dados_assinaturas)
        self.frame_cadastro.limpa_campos()

    def definicao_insucesso(self) -> None:
        tocar_notificacao("dv_erro", True)

    def controle_dados(self, dados: Optional[Dict] = None) -> None:
        if dados:
            self.frame_cadastro.controla_campos(dados)
        else:
            print('ERRO: Detalhar(car_cred não mandou os dados esperados!)')
        

# =================================================================================
# -7° MÓDULO: Faturas (Visão Analítica Mensal)
# =================================================================================

class Faturas(ctk.CTkToplevel):
    """
    Interface de "Fatura Fechada". 
    Mostra em tempo real as parcelas e assinaturas de um cartão para o mês atual e o próximo.
    """
    
    def __init__(self, parent: Any, id_user: Optional[int] = None, id_card: Optional[int] = None, nome_card: Optional[str] = None, dados_prontos: Optional[List] = None, dados_card: Optional[List] = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.id_user = id_user
        self.id_card = id_card
        self.nome_card = nome_card
        self.dados_card = dados_card
        self.dados_prontos = dados_prontos

        self.title(f"Detalhes: {self.nome_card}")
        centralizar_janela_responsiva(janela=self)
        self.transient(parent)
        self.focus_set() 

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.container_principal = ctk.CTkFrame(self, fg_color="transparent")
        self.container_principal.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.container_principal.grid_columnconfigure(0, weight=1) 
        self.container_principal.grid_rowconfigure(1, weight=1) 

        # ---------------- Gerencimento ---------------------
        self.limite = None
        self.fechamento = None
        self.vencimento = None

        if self.dados_card:
            for card in self.dados_card:
                if self.id_card == card['id_cartao']:
                    self.limite = card["limite_cartao"]
                    self.fechamento = card['dia_fechamento']
                    self.vencimento = card['dia_vencimento']
        
        self.data_atual = datetime.now().date()
        self.prox_mes_data = self.data_atual + relativedelta(months=1)

        self.mes_atual = self.data_atual.month
        self.prox_mes =  (self.data_atual + relativedelta(months=1)).month
        self.seg_prox_mes =  (self.data_atual + relativedelta(months=2)).month
        self.ter_prox_mes =  (self.data_atual + relativedelta(months=3)).month
        self.quart_prox_mes =  (self.data_atual + relativedelta(months=4)).month
        self.quint_prox_mes =  (self.data_atual + relativedelta(months=5)).month

        if self.fechamento and self.vencimento:
            if self.data_atual.day < self.fechamento:
                proximo_venc = self.data_atual.replace(day=self.vencimento)
            else:
                proximo_venc = self.prox_mes_data.replace(day=self.vencimento)
        else:
            proximo_venc = self.data_atual # Fallback

        opcoes = gerar_opcoes_meses()
        self.mes_atual_str = opcoes.get(self.mes_atual)
        self.prox_mes_str = opcoes.get(self.prox_mes)
        self.seg_prox_mes_str = opcoes.get(self.seg_prox_mes)
        self.ter_prox_mes_str = opcoes.get(self.ter_prox_mes)
        self.quart_prox_mes_str = opcoes.get(self.quart_prox_mes)
        self.quint_prox_mes_str = opcoes.get(self.quint_prox_mes)

        e = ' - '
        self.nomes_datas = [str(self.mes_atual_str) + e + str(self.prox_mes_str), 
                            str(self.seg_prox_mes_str) + e + str(self.ter_prox_mes_str), 
                            str(self.quart_prox_mes_str) + e + str(self.quint_prox_mes_str)]

        mes_a = f"#{self.nome_card} - Mês: {self.mes_atual_str}"
        mes_b = f"#{self.nome_card} - Mês: {self.prox_mes_str}"

        # ----------------- Top section ---------------------------------
        self.top_section = ctk.CTkFrame(self.container_principal, fg_color="transparent")
        self.top_section.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.top_section.grid_columnconfigure(0, weight=2) 
        self.top_section.grid_columnconfigure((1, 2, 3), weight=1) 
        self.top_section.grid_columnconfigure((4, 5), weight=0) 

        self.label_titulo = ctk.CTkLabel(self.top_section, text=f"Fatura: {nome_card}", font=("Arial", 22, "bold"))
        self.label_titulo.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        self.venc = ctk.CTkLabel(self.top_section, text=f"Próximo Vencimento: {data_para_exibicao(proximo_venc)}", font=("Arial", 16, "bold"))
        self.venc.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.fech = ctk.CTkLabel(self.top_section, text=f"Dia de Fechamento: {self.fechamento}", font=("Arial", 16, "bold"))
        self.fech.grid(row=0, column=2, padx=10, pady=5, sticky="w")

        self.limite = ctk.CTkLabel(self.top_section, text=f"Limite Cartão: {formatar_moeda(self.limite or 0)}", font=("Arial", 16, "bold"))
        self.limite.grid(row=0, column=3, padx=10, pady=5, sticky="w")

        self.label_mes = ctk.CTkLabel(self.top_section, text=f"Meses: ", font=ctk.CTkFont(size=16, weight="bold"))
        self.label_mes.grid(row=0, column=4, padx=(10, 5), pady=5, sticky="e")

        self.menu_mes = ctk.CTkOptionMenu(self.top_section, values=self.nomes_datas, command=self.trocar_meses, fg_color="#676666")
        self.menu_mes.grid(row=0, column=5, padx=(0, 10), pady=5, sticky="e")

        # --------------- Main section ----------------------------------
        self.main_section = ctk.CTkFrame(self.container_principal, fg_color="transparent")
        self.main_section.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.main_section.grid_columnconfigure(0, weight=1) 
        self.main_section.grid_columnconfigure(1, weight=1) 
        self.main_section.grid_rowconfigure(0, weight=1)

        #Instancia tabelas
        self.frame_tabela_um = Listar_faturas_cartao(self.main_section, self.id_user, self.id_card, self.nome_card, self.dados_prontos)
        self.frame_tabela_um.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.frame_tabela_um.tabela_cartao(id_user=self.id_user, id_card=self.id_card, escolha=mes_a, controle_mes=self.mes_atual)

        self.frame_tabela_dois = Listar_faturas_cartao(self.main_section, self.id_user, self.id_card, self.nome_card, self.dados_prontos)
        self.frame_tabela_dois.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.frame_tabela_dois.tabela_cartao(id_user=self.id_user, id_card=self.id_card, escolha=mes_b, controle_mes=self.prox_mes)


    def trocar_meses(self, escolha: str) -> None:
        """Comuta as visões das duas tabelas de faturas simuladas nos meses selecionados."""

        meses = [m.strip() for m in escolha.split('-')]

        controle_mes_a = gerar_opcoes_meses(str_mes=meses[0])
        controle_mes_b = gerar_opcoes_meses(str_mes=meses[1])

        mes_a = f"#{self.nome_card} - Mês: {meses[0]}"
        mes_b = f"#{self.nome_card} - Mês: {meses[1]}"

        self.frame_tabela_um.tabela_cartao(id_user=self.id_user, id_card=self.id_card, escolha=mes_a, controle_mes=controle_mes_a)
        self.frame_tabela_dois.tabela_cartao(id_user=self.id_user, id_card=self.id_card, escolha=mes_b, controle_mes=controle_mes_b)
      

# =================================================================================
# -8° MÓDULO: Simulação (Modo Sandbox)
# =================================================================================

class Simulacao(ctk.CTkToplevel):
    """
    Ambiente isolado onde o usuário adiciona despesas provisórias.
    O sistema recalcula dinamicamente se a conta (Despesas vs Receitas) 
    fecha no azul ou no vermelho nos meses subsequentes. NADA É SALVO NO BD.
    """

    def __init__(self, parent: Any, id_user: Optional[int] = None, despesas_avulsas: Optional[List] = None, dados_cartoes: Optional[List] = None, assinaturas_avulsas: Optional[List] = None, dados_usuario: Optional[List] = None, nomes_cartoes: Optional[List] = None, dados_prontos: Optional[List] = None, cb_vcmd_num: Optional[Callable] = None,  *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.id_user = id_user
        self.despesas_avulsas = despesas_avulsas
        self.dados_cartoes = dados_cartoes
        self.assinaturas_avulsas = assinaturas_avulsas
        self.dados_usuario = dados_usuario
        self.nomes_cartoes = nomes_cartoes
        self.dados_prontos = dados_prontos
        self.vcmd_num = cb_vcmd_num

        # ---------------- Gerencimento de self ---------------------
        self.data_atual = datetime.now().date()
        self.mes_atual = self.data_atual.month
        self.prox_mes =  (self.data_atual + relativedelta(months=1)).month
        self.seg_prox_mes =  (self.data_atual + relativedelta(months=2)).month
        self.ter_prox_mes =  (self.data_atual + relativedelta(months=3)).month
        self.quart_prox_mes =  (self.data_atual + relativedelta(months=4)).month
        self.quint_prox_mes =  (self.data_atual + relativedelta(months=5)).month

        opcoes = gerar_opcoes_meses()
        self.mes_atual_str = opcoes.get(self.mes_atual)
        self.prox_mes_str = opcoes.get(self.prox_mes)
        self.seg_prox_mes_str = opcoes.get(self.seg_prox_mes)
        self.ter_prox_mes_str = opcoes.get(self.ter_prox_mes)
        self.quart_prox_mes_str = opcoes.get(self.quart_prox_mes)
        self.quint_prox_mes_str = opcoes.get(self.quint_prox_mes)

        self.nomes_datas = [str(self.mes_atual_str), str(self.prox_mes_str), str(self.seg_prox_mes_str), str(self.ter_prox_mes_str), str(self.quart_prox_mes_str)]

        self.dados_select = []
        self.len_dados_select = 0

        self.id_card_atual = None
        self.controle_mes = 0

        self.valor_renda = self.dados_usuario[0].get('sal_fixo', 0.0) if self.dados_usuario else 0.0

        # --------------- Configuração da janela/'labels' -----------------------
        self.title(f"Simulação de Despesas")
        centralizar_janela_responsiva(janela=self)
        self.transient(parent)
        self.grab_set()
        self.focus_set() 

        self.configure(fg_color="#823737") 

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.container_principal = ctk.CTkFrame(self, fg_color="transparent")
        self.container_principal.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.container_principal.grid_columnconfigure(0, weight=1) 
        self.container_principal.grid_rowconfigure(1, weight=1) 

        # ----------------- Top section ---------------------------------
        self.top_section = ctk.CTkFrame(self.container_principal, fg_color="transparent")
        self.top_section.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.top_section.grid_columnconfigure(0, weight=1) 
        self.top_section.grid_columnconfigure(1, weight=1) 

        # ------------ Apresentação ------------------
        nome_completo = self.dados_usuario[0].get('nome_completo') if self.dados_usuario else "Usuário"
        texto = f"Simulação: Usuário - {nome_completo}!"
        self.nomeusuario_label = ctk.CTkLabel(self.top_section, text=texto, font=ctk.CTkFont(size=18, weight="bold"))
        self.nomeusuario_label.grid(row=0, column=0, padx=5, sticky="w")

        # --- DISPLAY DE RENDA FIXA ---
        self.frame_renda = ctk.CTkFrame(self.top_section, fg_color="transparent", width=150, height=100, corner_radius=15, border_width=3)
        self.frame_renda.grid(row=0, column=1, padx=10, pady=(0, 10), sticky="w") 
        
        self.label_renda = ctk.CTkLabel(self.frame_renda, text=f"Renda Fixa: {formatar_moeda(self.valor_renda)}", text_color="#27ae60", font=ctk.CTkFont(size=18,weight="bold"))
        self.label_renda.pack(side="left", padx=5)

        # -------- Botões de funções ------------
        self.btn_resete = ctk.CTkButton(self.top_section, text='Resete', command=self.resetar_lista, fg_color="#F87979", hover_color="#823737")
        self.btn_resete.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

        self.label_mes = ctk.CTkLabel(self.top_section, text=f"Mês: ", font=ctk.CTkFont(size=16, weight="bold"))
        self.label_mes.grid(row=0, column=4, padx=10, pady=10, sticky="w")

        self.menu_mes = ctk.CTkOptionMenu(self.top_section, values=self.nomes_datas, command=self.trocar_mes, fg_color="#676666")
        self.menu_mes.grid(row=0, column=5, padx=10, pady=5, sticky="w")

        self.label_cartao = ctk.CTkLabel(self.top_section, text=f"Selecione o Cartão: ", font=ctk.CTkFont(size=16, weight="bold"))
        self.label_cartao.grid(row=0, column=6, padx=10, pady=10, sticky="w")

        self.menu_cartao = ctk.CTkOptionMenu(self.top_section, values=self.nomes_cartoes, command=self.trocar_frame_cartao, fg_color="#676666")
        self.menu_cartao.grid(row=0, column=7, padx=10, pady=5, sticky="w")
        self.menu_cartao.set("Cartões")
        
        # --------------- Main section ----------------------------------
        self.main_section = ctk.CTkFrame(self.container_principal, fg_color="transparent")
        self.main_section.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.main_section.grid_columnconfigure(0, weight=1) 
        self.main_section.grid_columnconfigure(1, weight=4) 
        self.main_section.grid_columnconfigure(2, weight=3) 
        self.main_section.grid_rowconfigure(0, weight=1)

        # ---------------- formulário de cadastro (Mock DB) -----------------------
        self.frame_cadastro = Cadastrar_despesa(self.main_section, self.id_user, self.dados_cartoes, simulacao=True, dados_select=self.dados_select, controle_dados=self.controle_dados, cb_vcmd_num=self.vcmd_num)
        self.frame_cadastro.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # ------------------- FRAME TABELA GERAL -----------------------------
        self.tabela_frame = Listar_desp_tabela(parent=self.main_section, id_user=self.id_user, despesas_avulsas=self.despesas_avulsas, assinaturas_avulsas=self.assinaturas_avulsas, dados_cartoes=self.dados_cartoes, dados_prontos=self.dados_prontos)
        self.tabela_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew") 

        self.tabela_frame.renderizar()

        # -------------------- FRAME TABELA DO CARTÃO DE CRÉDITO  ------------------------------
        self.frame_tab_fatura = Listar_faturas_cartao(parent=self.main_section, id_user=self.id_user, dados_prontos=self.dados_prontos)
        self.frame_tab_fatura.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")


    def resetar_lista(self) -> None:
        """Limpa o Sandbox, recarregando a tabela apenas com as despesas reais."""
        self.dados_select.clear()
        self.tabela_frame.renderizar()

        for widget in self.frame_tab_fatura.container_dados.winfo_children():
            widget.destroy()

        self.frame_tab_fatura.tabela_frame.configure(label_text=f"Detalhes do Cartão: [ ] - Mês: {self.mes_atual_str} / {self.data_atual.year}")

        self.frame_cadastro.limpa_campos()
        self.menu_cartao.set('Cartões')
        self.menu_mes.set(self.mes_atual_str)


    def controle_dados(self, dados: Optional[List[Dict]] = None, controle_mes: Optional[int] = None, trocar_card: Optional[int] = None) -> None:
        """
        Engine do Sandbox de Simulação:
        Recebe as despesas falsas vindas do formulário, emula o impacto de parcelamento e 
        vencimento dos cartões (passando pelas regras do Helper) e repassa os dados manipulados 
        direto para as tabelas (Listar_desp_tabela), sem salvar no banco de dados.
        """
        if dados:
            tocar_notificacao('open_w', True)

            if self.len_dados_select < len(self.dados_select):
                self.len_dados_select = len(self.dados_select)
                trocar_card = None
        else:
            print('ERRO: Forms não enviou os dados!')
            tocar_notificacao('dv_erro', True)
            return

        for dado in dados:
            nome_cartao = dado['nome_cartao']
            tem_cartao = nome_cartao and nome_cartao != "Cartão de Cobrança - Sem Cartão" and nome_cartao != "Cadastre Seus Cartões Na Área Destinada"

            if tem_cartao and self.dados_cartoes:
                    
                for card in self.dados_cartoes:
                        
                        if card.get('nome_cartao') == nome_cartao:
                            id_card = card.get('id_cartao')
                            fech = card.get('dia_fechamento')
                            venc = card.get('dia_vencimento')
                            
                            data_compra = mysql_para_obj(dado.get('data_compra'))

                            if data_compra and venc and fech:
                                if venc < 12:
                                    fech_dc = data_compra.month - 1
                                    data_fech = data_compra.replace(day=fech, month=fech_dc) 
                                else:
                                    data_fech = data_compra.replace(day=fech)

                                if not controle_mes:
                                    if data_compra >= data_fech:
                                        controle_mes = (data_compra + relativedelta(months=1)).month
                                    else:
                                        controle_mes = data_compra.month

                            dados_card_dict = {
                                'id_cartao': id_card,
                                'nome_cartao': nome_cartao,
                                'fechamento': fech,
                                'vencimento': venc
                            }
                            dado['info_cartao'] = dados_card_dict
                            break 
  
            else: # Despesa avulsa
                data_pp = dado.get('prim_data_pag')


                if not controle_mes and data_pp:
                    controle_mes = data_pp.month
            
            str_mes = str(gerar_opcoes_meses().get(controle_mes))

            self.menu_mes.set(str_mes)
            self.tabela_frame.renderizar(controle_mes=controle_mes, escolha=str_mes, dados_simulacao=dados)

            id_card_render = trocar_card if trocar_card else self.id_card_atual
            cartao_selecionado = self.menu_cartao.get()

            if cartao_selecionado:
                escolha = f"[{cartao_selecionado}] - Mês: {str_mes}"

                if trocar_card:
                    id_card = trocar_card

                self.frame_tab_fatura.tabela_cartao(id_user=self.id_user, id_card=id_card_render, controle_mes=controle_mes, escolha=escolha, dados_simulacao=dados)

  


    def trocar_mes(self, escolha: str) -> None:
        """Gatilho de seleção de mês no menu superior (Dropdown). Recarrega o Mock Engine."""

        tocar_notificacao('open_w', True)

        dados = None
        if self.dados_select:
            dados = self.dados_select

        if self.mes_atual_str == escolha:
            self.controle_mes = self.mes_atual
         
        elif self.prox_mes_str == escolha:
            self.controle_mes = self.prox_mes

        elif self.seg_prox_mes_str == escolha:
            self.controle_mes = self.seg_prox_mes

        elif self.ter_prox_mes_str == escolha:
            self.controle_mes = self.ter_prox_mes

        elif self.quart_prox_mes_str == escolha:
            self.controle_mes = self.quart_prox_mes

        else:
            self.controle_mes = self.mes_atual
 
        if not dados:
            self.tabela_frame.renderizar(controle_mes=self.controle_mes, escolha=escolha)

            mes_str = gerar_opcoes_meses().get(self.controle_mes)
            self.menu_mes.set(str(mes_str))

            cartao = self.menu_cartao.get()
            self.trocar_frame_cartao(escolha=cartao)

        else:
            self.controle_dados(dados=dados, controle_mes=self.controle_mes, trocar_card=self.id_card_atual)


    def trocar_frame_cartao(self, escolha: str) -> None:
        """Comsuta as métricas do Sandbox para visualizar as faturas de outro cartão."""

        cartoes = self.dados_cartoes
        id_card = None
        nome_cartao = None

        if cartoes:
            for cartao in cartoes:
                nome_cartao = cartao['nome_cartao']
                if nome_cartao == escolha:
                    id_card = cartao['id_cartao']

        self.id_card_atual = id_card
        
        if self.dados_select:
            self.controle_dados(dados=self.dados_select, trocar_card=self.id_card_atual)

        else:
            if not self.controle_mes:
                self.controle_mes = self.mes_atual
                self.menu_mes.set(str(self.mes_atual_str))

                str_cartao_mes = f"[{escolha}] - Mês: {gerar_opcoes_meses().get(self.controle_mes)}"

                self.frame_tab_fatura.tabela_cartao(id_user=self.id_user, id_card=id_card, escolha=str_cartao_mes, controle_mes=self.controle_mes)

            else:
                str_cartao_mes = f"[{escolha}] - Mês: {gerar_opcoes_meses().get(self.controle_mes)}"

                self.frame_tab_fatura.tabela_cartao(id_user=self.id_user, id_card=id_card, escolha=str_cartao_mes, controle_mes=self.controle_mes)