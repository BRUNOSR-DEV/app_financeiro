
from models.conecte_bd import (
    pega_despesas_cartao, dados_assinaturas_cartao
     )

from utils.helper import(
    gerar_opcoes_meses, mysql_para_obj, formatar_moeda, data_para_exibicao, controle_data_parc_cc, centralizar_janela
)
from ui.forms import(
    Cadastrar_receitas, Cadastrar_despesas, Cadastrar_car_cred, Cadastrar_assinaturas
)

from ui.detalhar import(
    Listar_receitas, Listar_despesas, Listar_car_cred, Listar_assinaturas, Listar_faturas_cartao
)   

from dateutil.relativedelta import relativedelta
from datetime import datetime

import customtkinter as ctk
ctk.set_appearance_mode('dark')

from decimal import Decimal


class Receitas(ctk.CTkToplevel):

    def __init__(self,  parent=None, user_id=None, trocar_mes = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.trocar_mes = trocar_mes

        # --------------- Criação da Jenela -----------------------
        self.title("Gerenciar Receitas")
        centralizar_janela(self, 1000, 800)
        self.transient(parent) # Faz a popup aparecer sobre a janela principal e fechar com ela
        self.focus_set() # Define o foco para esta janela

        # ---------------- Gerencimento de self ---------------------
        self.data_atual = datetime.now().date()


        # --------------- Configuração da janela/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=2) 
        self.grid_rowconfigure(0, weight=1)

        # ---------- formulário de cadastro -----------------------
        self.frame_cadastro = Cadastrar_receitas(parent=self, user_id=self.user_id, trocar_mes = trocar_mes, atualizar_lista= self.atualizar_lista)
        self.frame_cadastro.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")



        #-------------- FRAME DA LISTA (Update/Delete) --------------------------
        self.frame_lista = Listar_receitas(parent=self, user_id=self.user_id, controle_dados= self.controle_dados, trocar_mes= trocar_mes )
        self.frame_lista.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
    
        self.frame_lista.grid_columnconfigure(0, weight=1)
        
        
    
    def controle_dados(self, dados=None):
        
        if dados:
            self.frame_cadastro.controla_campos(dados)
        


    def atualizar_lista(self, escolha=None):
        """Método que será chamado após um novo cadastro ou delete para recarregar a tabela"""
        
        print("Atualizando a lista de receitas na tela...")
        self.frame_lista.listar()
        
        # Lógica para puxar do banco 
        #if self.trocar_mes:
        #    self.trocar() # Atualiza a tela principal (Main) também, se necessário



class Despesas(ctk.CTkToplevel):

    def __init__(self, parent=None, user_id=None, dados_cartoes =None, callback=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.dados_cartoes = dados_cartoes
        self.callback = callback

        # --------------- Criação da Jenela -----------------------
        self.title("Gerenciar Despesas")
        centralizar_janela(self, 1000, 800)
        self.transient(parent)
        self.grab_set() 
        self.focus_set() 

        # ---------------- Gerencimento de self ---------------------
        self.data_atual = datetime.now().date()


        # --------------- Configuração da janela/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=3) 
        self.grid_rowconfigure(0, weight=1)

         # ---------- formulário de cadastro -----------------------
        self.frame_cadastro = Cadastrar_despesas(parent=self, user_id=self.user_id, dados_cartoes=self.dados_cartoes, callback= callback)
        self.frame_cadastro.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")


        #-------------------- FRAME DA LISTA (Update/Delete) ----------------------------------
        self.frame_lista = Listar_despesas(parent=self, user_id=self.user_id, callback = self.atualizar_lista )
        self.frame_lista.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
    
        self.frame_lista.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.frame_lista, text="Despesas Cadastradas", font=("Arial", 18, "bold")).grid(row=0, column=0,padx=10, pady=10)


    def atualizar_lista(self, escolha=None):
        """Método que será chamado após um novo cadastro ou delete para recarregar a tabela"""

        print("Atualizando a lista de despesas na tela...")

        
        # Lógica para puxar do banco 


        if self.callback:
            self.callback() # Atualiza a tela principal (Main) também, se necessário



class Car_cred(ctk.CTkToplevel):

    def __init__(self,  parent=None, user_id=None, nomes_cards =None, callback = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.callback = callback
        self.nomes_cards = nomes_cards

        # --------------- Criação da Jenela -----------------------
        self.title("Gerenciar Cartões de Crédito")
        centralizar_janela(self, 1000, 800)
        self.transient(parent)
        self.grab_set() 
        self.focus_set()

        # ---------------- Gerencimento de self ---------------------
        self.data_atual = datetime.now().date()


        # --------------- Configuração da janela/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=2) 
        self.grid_rowconfigure(0, weight=1)

         # ---------------- formulário de cadastro -----------------------
        self.frame_cadastro = Cadastrar_car_cred(parent=self, user_id=self.user_id, callback= callback)
        self.frame_cadastro.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")


        #------------------- FRAME DA LISTA (Update/Delete) ------------------------------

        self.frame_lista = Listar_car_cred(parent=self, user_id=self.user_id, callback = self.atualizar_lista )
        self.frame_lista.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
    
        self.frame_lista.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.frame_lista, text="Cartões Cadastrados", font=("Arial", 18, "bold")).grid(row=0, column=0,padx=10, pady=10)


    def atualizar_lista(self, escolha=None):
        """Método que será chamado após um novo cadastro ou delete para recarregar a tabela"""

        print("Atualizando a lista de cartões de crédito na tela...")

        # Lógica para puxar do banco 

        if self.callback:
            self.callback() # Atualiza a tela principal (Main) também, se necessário



class Assinaturas(ctk.CTkToplevel):

    def __init__(self, parent=None, user_id=None, dados_cartoes=None, callback=None):
        super().__init__(parent)

        self.callback = callback
        self.user_id = user_id
        self.dados_cartoes = dados_cartoes 

        # --------------- Criação da Jenela -----------------------
        self.title("Gerenciar Assinaturas")
        centralizar_janela(self, 1000, 800)
        self.grab_set() 
        self.focus_set()

        # ---------------- Gerencimento de self ---------------------
        self.data_atual = datetime.now().date()
        self.data_futuro = (self.data_atual + relativedelta(years=73)).replace(day=1, month=1)


        # --------------- Configuração da janela/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=2) 
        self.grid_rowconfigure(0, weight=1)

         # ---------------- formulário de cadastro -----------------------
        self.frame_cadastro = Cadastrar_assinaturas(parent=self, user_id=self.user_id, dados_cartoes=self.dados_cartoes,  callback= callback)
        self.frame_cadastro.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")


        #------------------- FRAME DA LISTA (Update/Delete) ------------------------------
        self.frame_lista = Listar_assinaturas(parent=self, user_id=self.user_id, callback = self.atualizar_lista )
        self.frame_lista.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
    
        self.frame_lista.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.frame_lista, text="Assinaturas Cadastradas", font=("Arial", 18, "bold")).grid(row=0, column=0, padx=10, pady=10)


    def atualizar_lista(self, escolha=None):
        """Método que será chamado após um novo cadastro ou delete para recarregar a tabela"""

        print("Atualizando a lista assinaturas na tela...")

        # Lógica para puxar do banco 

        if self.callback:
            self.callback() # Atualiza a tela principal (Main) também, se necessário


        
# --------------------- Detalhes da Fatura de Cartões ----------------------------
class Faturas(ctk.CTkToplevel):
    
    def __init__(self, parent, id_user=None, id_card=None, nome_card=None, callback=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.calback = callback
        self.id_user = id_user
        self.id_card = id_card
        self.nome_card = nome_card

        # --------------- Configuração da janela/'labels' -----------------------
        self.title(f"Detalhes: {nome_card}")
        centralizar_janela(self, 1000, 800)
        self.transient(parent)
        self.attributes("-topmost", True) 

        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=2) 
        self.grid_rowconfigure(0, weight=1)


        #-------------- FRAME Tabelas --------------------------
        self.frame_tabelas = Listar_faturas_cartao(self, self.id_user, self.id_card, self.nome_card, callback=self.calback)
        self.frame_tabelas.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
    
        self.frame_tabelas.grid_columnconfigure(0, weight=1)



