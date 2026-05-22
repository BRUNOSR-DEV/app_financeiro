
# ---------------------------------- IMPORTAÇÃO - MÓDULOS LOCAIS ------------------------------------
from models.database import Database
from models.repositorios import *

import models.conecte_bd as db 

from utils.helper import(
    centralizar_janela, 
    gerar_opcoes_meses, 
    formatar_moeda, 
    mysql_para_obj, 
    data_para_exibicao, 
)

from utils.audio_helper import(tocar_notificacao)

#------ IMPORTAÇÃO DE CLASSES PARA CADASTRO - (forms.py) --------
from ui.forms import *

#------ IMPORTAÇÃO DE CLASSES PARA LISTAGEM - (detalhar.py) --------
from ui.detalhar import *

#------ IMPORTAÇÃO DE CLASSES TYPEDDICT - (typedDict.py) --------
from utils.typedDict import *

# ------------------------------ IMPORTAÇÃO - MÓDULOS BIBLIOTECAS ---------------------------------
#BILIO PADRÕES
from typing import List
from datetime import datetime

#BIBLIO VIA PIP
import customtkinter as ctk
from dateutil.relativedelta import relativedelta

# ------------- CONFIGURAÇÃO INICIAL ---------------
ctk.set_appearance_mode('dark')


class  CrudManage:

    def __init__(
            self, parent=None,
            # ------- dependências de dados ---------
            user_id=None, dados_usuario=None, dados_receitas=None, dados_cartoes=None, 
            nomes_cartoes=None, despesas_avulsas=None, assinaturas_avulsas=None, dados_prontos=None,
            # ------- callbacks ----------
            cb_atualiza_bd=None, cb_vcmd_num=None, cb_att_app=None, cb_trocar_mes=None):
        
        self.parent = parent
        self.user_id = user_id
        self.dados_usuario = dados_usuario
        self.dados_receitas = dados_receitas
        self.dados_cartoes = dados_cartoes
        self.nomes_cartoes = nomes_cartoes
        self.despesas_avulsas = despesas_avulsas
        self.assinaturas_avulsas = assinaturas_avulsas
        self.dados_prontos = dados_prontos


        #------ callbacks
        self.atualiza_bd = cb_atualiza_bd #vem do login_app
        self.vcmd_num = cb_vcmd_num #vem do login_app e main_app
        self.att_app = cb_att_app # vem do main_app
        self.trocar_mes = cb_trocar_mes #vem do main_app


    def tela_usuarios(self):
        tocar_notificacao("open_w", True)

        register_window = Usuarios(parent=self.parent, cb_atualiza_bd=self.atualiza_bd, cb_vcmd_num=self.vcmd_num)
        self.parent.wait_window(register_window)


    def tela_receitas(self):
        tocar_notificacao('open_w', True)
        
        register_window = Receitas(parent=self.parent, user_id=self.user_id, dados_receitas=self.dados_receitas, att_app = self.att_app, cb_vcmd_num=self.vcmd_num)
        self.parent.wait_window(register_window) 


    def tela_despesas(self):
        tocar_notificacao('open_w', True)

        register_window = Despesas(parent=self.parent, user_id=self.user_id, dados_cartoes=self.dados_cartoes, cb_trocar_mes=self.trocar_mes, cb_att_app=self.att_app, cb_vcmd_num=self.vcmd_num)
        self.parent.wait_window(register_window)


    def tela_car_cred(self):
        tocar_notificacao('open_w', True)

        register_window = Car_cred(parent=self.parent, user_id=self.user_id, dados_cartoes=self.dados_cartoes, nomes_cards=self.nomes_cartoes, cb_att_app=self.att_app, cb_vcmd_num=self.vcmd_num)
        self.parent.wait_window(register_window)


    def tela_assinaturas(self):
        tocar_notificacao('open_w', True)

        register_window = Assinaturas(parent=self.parent, user_id=self.user_id, dados_cartoes=self.dados_cartoes, cb_att_app=self.att_app, cb_vcmd_num=self.vcmd_num)
        self.parent.wait_window(register_window)
        

    def tela_simulacao(self):
        tocar_notificacao('open_w', True)

        register_window = Simulacao(parent=self.parent, id_user=self.user_id, despesas_avulsas= self.despesas_avulsas, assinaturas_avulsas=self.assinaturas_avulsas, dados_cartoes=self.dados_cartoes, dados_usuario=self.dados_usuario, nomes_cartoes=self.nomes_cartoes, dados_prontos=self.dados_prontos, cb_vcmd_num=self.vcmd_num)

        self.parent.wait_window(register_window) 


    def tela_faturas(self, nome_select=None):

        id_card = [card['id_cartao'] for card in self.dados_cartoes if card['nome_cartao'] == nome_select]

        if id_card:
            tocar_notificacao('open_w', True)

            register_window = Faturas(parent=self.parent, id_user=self.user_id, id_card=id_card[0], nome_card=nome_select, dados_card=self.dados_cartoes, dados_prontos= self.dados_prontos)
            self.parent.wait_window(register_window)
        else:
            print('ERRO: ID card não encontrado!')


#-1° Módulo Usuarios
class Usuarios(ctk.CTkToplevel):

    def __init__(self,  parent=None, cb_atualiza_bd=None, cb_vcmd_num=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
    
        self.parent = parent 
        self.atualiza_bd = cb_atualiza_bd
        self.vcmd_num = cb_vcmd_num

        #instância do db - classe Rep_Usuario - entidade Usuario
        self.db_conn= Database()
        self.db = Rep_Usuario(self.db_conn)

        # --------------- Configuração da janela/'labels' -----------------------
        self.title("Registrar Novo Usuário")
        centralizar_janela(self, 350, 500)
        self.transient(parent) 
        self.grab_set() 
        self.focus_set()

        self.grid_columnconfigure(0, weight=1) 

        # ---------------- Gerencimento ---------------------
        self.dados_usuarios: List[Dados_usuarios_db] = self.db.dados_usuarios()

        self.nome_users = [dado['nome_user'] for dado in self.dados_usuarios]

        # ---------------- Frame Cadastro ------------------------
        self.frame_cadastro = Cadastrar_usuario(self, cb_comandante_crud=self.comandante_crud, cb_fechar=self.fechar, nome_users=self.nome_users, cb_vcmd_num=self.vcmd_num)
        self.frame_cadastro.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")


    def comandante_crud(self, inserir=None):

        sucesso = None

        if inserir:
            sucesso = self.db.inserir_usuario(inserir['nome_comp'], inserir['usuario'], inserir['senha'], inserir['sal_fixo'] )
        
        if sucesso:
            tocar_notificacao("dv_sucesso", True)
            
            self.atualiza_bd()
        else:
            tocar_notificacao("dv_erro", True)
        
        return sucesso

    def fechar(self):
        self.destroy()
        

#-2° Módulo Receitas
class Receitas(ctk.CTkToplevel): 

    def __init__(self,  parent=None, user_id=None, dados_receitas=None, att_app=None, cb_vcmd_num=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.user_id = user_id
        self.dados_receitas = dados_receitas
        self.att_app = att_app
        self.vcmd_num = cb_vcmd_num

        #instância do db - classe Rep_Usuario - entidade Usuario
        self.db_conn= Database()
        self.db = Rep_Receita(self.db_conn)

        # --------------- Criação da Jenela -----------------------
        self.title("Gerenciar Receitas")
        centralizar_janela(self, 1000, 800)
        self.transient(self.parent) # Faz a popup aparecer sobre a janela principal e fechar com ela
        self.focus_set() # Define o foco para esta janela

        # ---------------- Gerencimento de self ---------------------
        self.data_atual = datetime.now().date()

        self.notifica_delete = False

        # --------------- Configuração da janela/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=2) 
        self.grid_rowconfigure(0, weight=1)

        # ---------- formulário de cadastro -----------------------
        self.frame_cadastro = Cadastrar_receita(parent=self, user_id=self.user_id, callback_comandante_crud=self.comandante_crud, cb_vcmd_num=self.vcmd_num)
        self.frame_cadastro.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")


        #-------------- FRAME DA LISTA (Update/Delete) --------------------------
        self.frame_lista = Listar_receitas(parent=self, user_id=self.user_id, dados_receitas=self.dados_receitas, controle_dados= self.controle_dados, callback_comandante_crud=self.comandante_crud)
        self.frame_lista.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
    
        self.frame_lista.grid_columnconfigure(0, weight=1)
        


    def comandante_crud(self, inserir:dict=None, atualizar:dict=None, deletar:dict=None):

        sucesso = None

        if inserir:
            sucesso = self.db.inserir_receita(inserir['user_id'], inserir['valor'], inserir['descricao'], inserir['data_mysql'])
        elif atualizar:
            sucesso = self.db.atualizar_receita(atualizar['id_rec'], atualizar['valor'], atualizar['descricao'], atualizar['data_mysql'])
        elif deletar:
            self.notifica_delete = True
            sucesso = self.db.deletar_receita(deletar['id_rec'])
        
            
        if sucesso:
            self.definicao_sucesso()
        else:
            self.definicao_insucesso()

        return sucesso
    

    def definicao_sucesso(self):

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


    def definicao_insucesso(self):
        tocar_notificacao("dv_erro", True)


    def controle_dados(self, dados=None):
        
        if dados:
            self.frame_cadastro.controla_campos(dados)
        else:
            print('ERRO: detalhar.py(Listar_receitas) não enviou os dados')
        

#-3° Módulo Despesas
class Despesas(ctk.CTkToplevel):

    def __init__(self, parent=None, user_id=None, dados_cartoes =None, cb_trocar_mes=None, cb_att_app=None, cb_vcmd_num=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.dados_cartoes = dados_cartoes
        self.trocar_mes = cb_trocar_mes
        self.att_app = cb_att_app
        self.vcmd_num = cb_vcmd_num

        #instância do db - classe Rep_Usuario - entidade Usuario
        self.db_conn= Database()
        self.db = Rep_Despesa(self.db_conn)

        # --------------- Configuração da janela/'labels' -----------------------
        self.title("Gerenciar Despesas")
        centralizar_janela(self, 1700, 800)
        self.transient(parent)
        self.focus_set() 

        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=7) 
        self.grid_rowconfigure(0, weight=1)

        # ---------------- Gerencimento ---------------------
        self.data_atual = datetime.now().date()

        self.dados_despesas: List[Dados_despesas_db] = self.db.dados_despesas(self.user_id)

        self.notifica_delete = False

         # ---------- formulário de cadastro -----------------------
        self.frame_cadastro = Cadastrar_despesa(parent=self, user_id=self.user_id, dados_cartoes=self.dados_cartoes, cb_comandante_crud=self.comandante_crud, cb_vcmd_num=self.vcmd_num)
        self.frame_cadastro.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")


        #-------------------- FRAME DA LISTA (Update/Delete) ----------------------------------
        self.frame_lista = Listar_despesas(parent=self, user_id=self.user_id, dados_cartoes= self.dados_cartoes, dados_despesas=self.dados_despesas, controle_dados=self.controle_dados, cb_comandante_crud=self.comandante_crud)
        self.frame_lista.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
    
        self.frame_lista.grid_columnconfigure(0, weight=1)



    def comandante_crud(self, inserir:dict=None, atualizar:dict=None, deletar:dict=None):

        inserir: Envia_despesa_form = inserir
        atualizar: Envia_despesa_form = atualizar

        sucesso = None

        if inserir:
            sucesso = self.db.inserir_despesa(inserir['user_id'], inserir['local'], inserir['valor_total'], inserir['parcelas'], inserir['descricao'], inserir['categoria'], inserir['dc_select_mysql'], inserir['prim_dc_select_mysql'], inserir['dia_venc'], inserir['id_card'])

        elif atualizar:
            sucesso = self.db.atualizar_despesa(atualizar['id_desp'], atualizar['local'], atualizar['valor_total'], atualizar['parcelas'], atualizar['descricao'], atualizar['categoria'], atualizar['dc_select_mysql'], atualizar['prim_dc_select_mysql'], atualizar['dia_venc'], atualizar['id_card'])

        elif deletar:
            self.notifica_delete = True
            sucesso = self.db.deletar_despesa(deletar['id_desp'])
        
            
        if sucesso:
            self.definicao_sucesso()
        else:
            self.definicao_insucesso()

        return sucesso
    

    def definicao_sucesso(self):

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


    def definicao_insucesso(self):
        tocar_notificacao("dv_erro", True)


    def controle_dados(self, dados):

        if dados:
            self.frame_cadastro.controla_campos(dados)
        else:
            print('ERRO: detalhar(despesas não mandou os dados esperados!)')


#-4 Módulo Cartões de Crédito
class Car_cred(ctk.CTkToplevel):

    def __init__(self,  parent=None, user_id=None, dados_cartoes=None, nomes_cards =None, cb_att_app = None, cb_vcmd_num=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.nomes_cards = nomes_cards
        self.dados_cartoes = dados_cartoes

        self.vcmd_num = cb_vcmd_num
        self.att_app = cb_att_app

        #instância do db - classe Rep_Usuario - entidade Usuario
        self.db_conn= Database()
        self.db = Rep_Cartao_credito(self.db_conn)

        # --------------- Criação da Jenela -----------------------
        self.title("Gerenciar Cartões de Crédito")
        centralizar_janela(self, 1200, 800)
        self.transient(parent)
        self.focus_set()

        # ---------------- Gerencimento de self ---------------------
        self.data_atual = datetime.now().date()

        self.notifica_delete = False

        # --------------- Configuração da janela/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=2) 
        self.grid_rowconfigure(0, weight=1)

         # ---------------- formulário de cadastro -----------------------
        self.frame_cadastro = Cadastrar_car_cred(parent=self, user_id=self.user_id, nomes_cards=self.nomes_cards, cb_comandante_crud=self.comandante_crud, cb_vcmd_num=self.vcmd_num)
        self.frame_cadastro.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        #------------------- FRAME DA LISTA (Update/Delete) ------------------------------
        self.frame_lista = Listar_car_cred(parent=self, user_id=self.user_id, dados_cartoes=self.dados_cartoes, controle_dados = self.controle_dados, cb_comandante_crud=self.comandante_crud)
        self.frame_lista.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
    
        self.frame_lista.grid_columnconfigure(0, weight=1)


    def comandante_crud(self, inserir=None, atualizar=None, deletar=None):
    
        if inserir:
            sucesso = self.db.inserir_cc(inserir['user_id'], inserir['nome'], inserir['limite'], inserir['dia_fech'], inserir['dia_venc'])
        elif atualizar:
            sucesso = self.db.atualizar_cartao(atualizar['id_card'], atualizar['nome'], atualizar['limite'], atualizar['dia_fech'], atualizar['dia_venc'])
        elif deletar:
            self.notifica_delete = True
            sucesso =  self.db.deletar_cartao(deletar['id_card'])

        if sucesso:
            self.definicao_sucesso()
        else:
            self.definicao_insucesso()
        
        return sucesso


    def definicao_sucesso(self):

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


    def definicao_insucesso(self):
        tocar_notificacao("dv_erro", True)


    def controle_dados(self, dados=None):
        
        if dados:
            self.frame_cadastro.controla_campos(dados)
        else:
            print('ERRO: Detalhar(car_cred não mandou os dados esperados!)')
        

#-5° Módulo Assinaturas
class Assinaturas(ctk.CTkToplevel):

    def __init__(self, parent=None, user_id=None, dados_cartoes=None, cb_att_app= None, cb_vcmd_num=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.dados_cartoes = dados_cartoes

        self.att_app = cb_att_app
        self.vcmd_num = cb_vcmd_num

        #instância do db - classe Rep_Usuario - entidade Usuario
        self.db_conn= Database()
        self.db = Rep_Assinatura(self.db_conn)

        # --------------- Criação da Jenela -----------------------
        self.title("Gerenciar Assinaturas")
        centralizar_janela(self, 1800, 800)
        self.transient(parent) 
        self.focus_set() 
       
        # ---------------- Gerencimento de self ---------------------
        self.data_atual = datetime.now().date()
        self.data_futuro = (self.data_atual + relativedelta(years=73)).replace(day=1, month=1)

        self.dados_assinaturas = self.db.dados_assinaturas(self.user_id)

        self.notifica_delete = False

        # --------------- Configuração da janela/'labels' -----------------------

        self.grid_columnconfigure(0, weight=1) #coluna o - formulário
        self.grid_columnconfigure(1, weight=4) #coluna 1 - Lista
        self.grid_rowconfigure(0, weight=1)

         # ---------------- formulário de cadastro -----------------------
        self.frame_cadastro = Cadastrar_assinatura(self, self.user_id, self.dados_cartoes, cb_comandante_crud=self.comandante_crud, cb_vcmd_num=self.vcmd_num)
        self.frame_cadastro.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        #------------------- FRAME DA LISTA (Update/Delete) ------------------------------
        self.frame_lista = Listar_assinaturas(self, self.user_id, self.dados_cartoes, self.dados_assinaturas, self.controle_dados, cb_comandante_crud=self.comandante_crud )
        self.frame_lista.grid(row=0, column=1, padx=(0,20), pady=20, sticky="nsew")
    
        self.frame_lista.grid_columnconfigure(0, weight=1)
        

    def comandante_crud(self, inserir:dict=None, atualizar:dict=None, deletar:dict=None):

        inserir: Envia_ass_form = inserir
        atualizar: Envia_ass_form = atualizar

        sucesso = None

        if inserir:
            sucesso = self.db.inserir_assinatura(inserir['user_id'], inserir['nome'], inserir['valor'], inserir['descricao'], inserir['data_aq_mysql'], inserir['data_pp_mysql'], inserir['dia_venc'], inserir['categoria'], inserir['id_card'])

        elif atualizar:
            sucesso = self.db.atualizar_assinatura(atualizar['id_ass'], atualizar['nome'], atualizar['valor'], atualizar['descricao'], atualizar['data_aq_mysql'], atualizar['data_pp_mysql'], atualizar['dia_venc'], atualizar['categoria'], atualizar['id_card'])
        elif deletar:
            self.notifica_delete = True
            sucesso = self.db.deletar_assinatura(deletar['id_ass'])
        
            
        if sucesso:
            self.definicao_sucesso()
        else:
            self.definicao_insucesso()

        return sucesso


    def definicao_sucesso(self):

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


    def definicao_insucesso(self):
        tocar_notificacao("dv_erro", True)


    def controle_dados(self, dados=None):
        
        if dados:
            self.frame_cadastro.controla_campos(dados)
        else:
            print('ERRO: Detalhar(car_cred não mandou os dados esperados!)')
        

#-6° Módulo Faturas
class Faturas(ctk.CTkToplevel):
    
    def __init__(self, parent, id_user=None, id_card=None, nome_card=None, dados_prontos=None, dados_card=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.id_user = id_user
        self.id_card = id_card
        self.nome_card = nome_card
        self.dados_card: List[Dados_cartoes_db]  = dados_card
        self.dados_prontos = dados_prontos

        # --------------- Configuração da janela/'labels' -----------------------
        self.title(f"Detalhes: {self.nome_card}")
        centralizar_janela(self, 1200, 800)
        self.transient(parent)
        self.focus_set() 

        self.grid_columnconfigure(0, weight=1)
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

        if self.data_atual.day < self.fechamento:
            proximo_venc = self.data_atual.replace(day=self.vencimento)
        else:
            proximo_venc = self.prox_mes_data.replace(day=self.vencimento)

        opcoes = gerar_opcoes_meses()
        self.mes_atual_str = opcoes.get(self.mes_atual)
        self.prox_mes_str = opcoes.get(self.prox_mes)
        self.seg_prox_mes_str = opcoes.get(self.seg_prox_mes)
        self.ter_prox_mes_str = opcoes.get(self.ter_prox_mes)
        self.quart_prox_mes_str = opcoes.get(self.quart_prox_mes)
        self.quint_prox_mes_str = opcoes.get(self.quint_prox_mes)

        e = ' - '
        self.nomes_datas = [self.mes_atual_str + e + self.prox_mes_str, self.seg_prox_mes_str + e + self.ter_prox_mes_str, self.quart_prox_mes_str + e + self.quint_prox_mes_str]


        mes_a = f"#{self.nome_card} - Mês: {self.mes_atual_str}"
        mes_b = f"#{self.nome_card} - Mês: {self.prox_mes_str}"

        # ----------------- Top section ---------------------------------
        self.top_section = ctk.CTkFrame(self.container_principal, fg_color="transparent")
        self.top_section.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.top_section.grid_columnconfigure(0, weight=2) # fatura
        self.top_section.grid_columnconfigure((1, 2, 3), weight=1) #infos cartao
        self.top_section.grid_columnconfigure((4, 5), weight=0) # lebel e menu datas

        self.label_titulo = ctk.CTkLabel(self.top_section, text=f"Fatura: {nome_card}", font=("Arial", 22, "bold"))
        self.label_titulo.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        self.venc = ctk.CTkLabel(self.top_section, text=f"Próximo Vencimento: {data_para_exibicao(proximo_venc)}", font=("Arial", 16, "bold"))
        self.venc.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.fech = ctk.CTkLabel(self.top_section, text=f"Dia de Fechamento: {self.fechamento}", font=("Arial", 16, "bold"))
        self.fech.grid(row=0, column=2, padx=10, pady=5, sticky="w")

        self.limite = ctk.CTkLabel(self.top_section, text=f"Limite Cartão: {formatar_moeda(self.limite)}", font=("Arial", 16, "bold"))
        self.limite.grid(row=0, column=3, padx=10, pady=5, sticky="w")

        self.label_mes = ctk.CTkLabel(self.top_section, text=f"Meses: ", font=ctk.CTkFont(size=16, weight="bold"))
        self.label_mes.grid(row=0, column=4, padx=(10, 5), pady=5, sticky="e")

        self.menu_mes = ctk.CTkOptionMenu(self.top_section, values= self.nomes_datas, command=self.trocar_meses, fg_color="#676666")
        self.menu_mes.grid(row=0, column=5, padx=(0, 10), pady=5, sticky="e")

        # --------------- Main section ----------------------------------
        self.main_section = ctk.CTkFrame(self.container_principal, fg_color="transparent")
        self.main_section.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.main_section.grid_columnconfigure(0, weight=1) #tabela um
        self.main_section.grid_columnconfigure(1, weight=1) #tabela dois
        self.main_section.grid_rowconfigure(0, weight=1)

        #Instancia tabelas
        #-------------- Tabela mês mes_a --------------------------
        self.frame_tabela_um = Listar_faturas_cartao(self.main_section, self.id_user, self.id_card, self.nome_card, self.dados_prontos)
        self.frame_tabela_um.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.frame_tabela_um.tabela_cartao(id_user=self.id_user, id_card=self.id_card, escolha=mes_a, controle_mes=self.mes_atual)

        # ---------------- Tabela próximo mês ------------------------------
        self.frame_tabela_dois = Listar_faturas_cartao(self.main_section, self.id_user, self.id_card, self.nome_card, self.dados_prontos)
        self.frame_tabela_dois.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.frame_tabela_dois.tabela_cartao(id_user=self.id_user, id_card=self.id_card, escolha=mes_b, controle_mes=self.prox_mes)


    def trocar_meses(self, escolha):

        meses = [m.strip() for m in escolha.split('-')]

        controle_mes_a = gerar_opcoes_meses(str_mes=meses[0])
        controle_mes_b = gerar_opcoes_meses(str_mes=meses[1])

        mes_a = f"#{self.nome_card} - Mês: {meses[0]}"
        mes_b = f"#{self.nome_card} - Mês: {meses[1]}"

        #tabela 1
        self.frame_tabela_um.tabela_cartao(id_user=self.id_user, id_card=self.id_card, escolha=mes_a, controle_mes=controle_mes_a)

        #tabela 2
        self.frame_tabela_dois.tabela_cartao(id_user=self.id_user, id_card=self.id_card, escolha=mes_b, controle_mes=controle_mes_b)
      

#-7° Módulo Simulação
class Simulacao(ctk.CTkToplevel):

    def __init__(self, parent, id_user=None, despesas_avulsas=None, dados_cartoes=None, assinaturas_avulsas=None, dados_usuario=None, nomes_cartoes=None, dados_prontos=None, cb_vcmd_num=None,  *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.id_user = id_user
        self.despesas_avulsas = despesas_avulsas
        self.dados_cartoes = dados_cartoes
        self.assinaturas_avulsas = assinaturas_avulsas
        self.dados_usuario = dados_usuario
        self.nomes_cartoes = nomes_cartoes
        self.dados_prontos: List[Pega_div_cartao_db] = dados_prontos
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

        self.nomes_datas = [self.mes_atual_str, self.prox_mes_str, self.seg_prox_mes_str, self.ter_prox_mes_str, self.quart_prox_mes_str]

        self.dados_select = []
        self.len_dados_select = 0

        self.id_card_atual = None

        self.controle_mes = 0

        self.valor_renda = self.dados_usuario[0].get('sal_fixo', 0.0)


        # --------------- Configuração da janela/'labels' -----------------------
        self.title(f"Simulação de Despesas")
        centralizar_janela(self, 1400, 800)
        self.transient(parent)
        self.grab_set()
        self.focus_set() 

        self.configure(fg_color="#823737") #muda a cor da janela

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.container_principal = ctk.CTkFrame(self, fg_color="transparent")
        self.container_principal.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.container_principal.grid_columnconfigure(0, weight=1) 
        self.container_principal.grid_rowconfigure(1, weight=1) 

        # ----------------- Top section ---------------------------------
        self.top_section = ctk.CTkFrame(self.container_principal, fg_color="transparent")
        self.top_section.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.top_section.grid_columnconfigure(0, weight=1) # Bem-vindo
        self.top_section.grid_columnconfigure(1, weight=1) 

                        # ------------ Apresentação ------------------
        texto = f"Simulação: Usuário - {self.dados_usuario[0].get('nome_completo')}!"
        self.nomeusuario_label = ctk.CTkLabel(self.top_section, text=texto, font=ctk.CTkFont(size=18, weight="bold"))
        self.nomeusuario_label.grid(row=0, column=0, padx=5, sticky="w")

                            # --- DISPLAY DE RENDA FIXA ---
        self.frame_renda = ctk.CTkFrame(self.top_section, fg_color="transparent", width=150, height=100, corner_radius=15, border_width=3)
        self.frame_renda.grid(row=0, column=1, padx=10, pady=(0, 10), sticky="w") # Fica do lado do nome
        
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

        self.main_section.grid_columnconfigure(0, weight=1) #formulário
        self.main_section.grid_columnconfigure(1, weight=4) #tabela
        self.main_section.grid_columnconfigure(2, weight=3) #tab_fatura
        self.main_section.grid_rowconfigure(0, weight=1)

        # ---------------- formulário de cadastro -----------------------
        self.frame_cadastro = Cadastrar_despesa(self.main_section, self.id_user, self.dados_cartoes, simulacao=True, dados_select= self.dados_select, controle_dados=self.controle_dados, cb_vcmd_num=self.vcmd_num)
        self.frame_cadastro.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # ------------------- FRAME TABELA -----------------------------
        self.tabela_frame = Listar_desp_tabela(parent=self.main_section, id_user=self.id_user, despesas_avulsas= self.despesas_avulsas, assinaturas_avulsas=self.assinaturas_avulsas, dados_cartoes=self.dados_cartoes, dados_prontos=self.dados_prontos)
        self.tabela_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew") 

        self.tabela_frame.renderizar()

        # -------------------- FRAME TABELA DO CARTÃO DE CRÉDITO  ------------------------------
        self.frame_tab_fatura = Listar_faturas_cartao(parent=self.main_section, id_user=self.id_user, dados_prontos=self.dados_prontos)
        self.frame_tab_fatura.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")


    def resetar_lista(self):

        self.dados_select.clear()

        self.tabela_frame.renderizar()

        for widget in self.frame_tab_fatura.container_dados.winfo_children():
            widget.destroy()

        self.frame_tab_fatura.tabela_frame.configure(label_text=f"Detalhes do Cartão: [ ] - Mês: {self.mes_atual_str} / {self.data_atual.year}")

        self.frame_cadastro.limpa_campos()
        self.menu_cartao.set('Cartões')
        self.menu_mes.set(self.mes_atual_str)


    def controle_dados(self, dados=None, controle_mes=None, trocar_card=None):

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
            
            #dado['info_cartao'] = None    
            tem_cartao = nome_cartao and nome_cartao != "Cartão de Cobrança - Sem Cartão" and nome_cartao != "Cadastre Seus Cartões Na Área Destinada"

            if tem_cartao:
                    
                for card in self.dados_cartoes:
                        
                        if card.get('nome_cartao') == nome_cartao:
                            id_card = card.get('id_cartao')
                            fech = card.get('dia_fechamento')
                            venc = card.get('dia_vencimento')
                            
                            data_compra = mysql_para_obj(dado.get('data_compra'))

                            if venc < 12:
                                fech_dc = data_compra.month - 1
                                data_fech = data_compra.replace(day=fech, month=fech_dc) #formata data com dia de fechamento do cartão
                            else:
                                data_fech = data_compra.replace(day=fech)

                            if not controle_mes:
                                
                                if data_compra >= data_fech:
                                    controle_mes = (data_compra + relativedelta(months=1)).month
                                else:
                                    controle_mes = data_compra.month

                            dados_card: Cartao = {
                                'id_cartao': id_card,
                                'nome_cartao': nome_cartao,
                                'fechamento': fech,
                                'vencimento': venc
                            }
                            dado['info_cartao'] = dados_card
                            break 
  
            else: #Despesa avulsa
                data_pp = dado.get('prim_data_pag')

                if not controle_mes:
                    controle_mes = data_pp.month
            
            str_mes = gerar_opcoes_meses()[controle_mes]

            self.menu_mes.set(str_mes)

            self.tabela_frame.renderizar(controle_mes=controle_mes, escolha=str_mes, dados_simulacao=dados)

            if tem_cartao:
                escolha = f"[{nome_cartao}] - Mês: {str_mes}"

                if trocar_card:
                    id_card = trocar_card

                self.frame_tab_fatura.tabela_cartao(id_user=self.id_user, id_card=id_card, controle_mes=controle_mes, escolha=escolha, dados_simulacao=dados)

                self.menu_cartao.set(nome_cartao)   
            


    def trocar_mes(self, escolha):

        tocar_notificacao('open_w', True)

        dados= None
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

            mes_str = gerar_opcoes_meses()[self.controle_mes]
            self.menu_mes.set(mes_str)

            cartao = self.menu_cartao.get()
            self.trocar_frame_cartao(escolha=cartao)

        else:
            self.controle_dados(dados=dados, controle_mes=self.controle_mes, trocar_card=self.id_card_atual)


    def trocar_frame_cartao(self, escolha):
        
        cartoes = self.dados_cartoes
        id_card = None
        nome_cartao = None

        for cartao in cartoes:
            nome_cartao = cartao['nome_cartao']
            if nome_cartao == escolha:

                id_card = cartao['id_cartao']

        self.id_card_atual = id_card
        
        if self.dados_select:

            self.controle_dados(dados=self.dados_select, trocar_card= self.id_card_atual)

        else:
            if not self.controle_mes:
                self.controle_mes = self.mes_atual
                self.menu_mes.set(self.mes_atual_str)

                str_cartao_mes = f"[{escolha}] - Mês: {gerar_opcoes_meses()[self.controle_mes]}"

                self.frame_tab_fatura.tabela_cartao(id_user=self.id_user, id_card=id_card, escolha=str_cartao_mes, controle_mes=self.controle_mes)

            else:
                str_cartao_mes = f"[{escolha}] - Mês: {gerar_opcoes_meses()[self.controle_mes]}"

                self.frame_tab_fatura.tabela_cartao(id_user=self.id_user, id_card=id_card, escolha=str_cartao_mes, controle_mes=self.controle_mes)
                

