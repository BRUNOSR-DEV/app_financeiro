
from utils.helper import(
    centralizar_janela
)
from ui.forms import(
    Cadastrar_receitas, Cadastrar_despesas, Cadastrar_car_cred, Cadastrar_assinaturas
)

from ui.detalhar import(
    Listar_receitas, Listar_despesas, Listar_car_cred, Listar_assinaturas, Listar_faturas_cartao, Listar_cat_grafico, Listar_desp_tabela
)   

from dateutil.relativedelta import relativedelta
from datetime import datetime

import customtkinter as ctk
ctk.set_appearance_mode('dark')


#Módulo Receitas
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
        else:
            print('ERRO: detalhar.py(Listar_receitas) não enviou os dados')
        

    def atualizar_lista(self):
        
        print("Atualizando a lista de receitas na tela...")
        self.frame_lista.listar()
        

#Módulo Despesas
class Despesas(ctk.CTkToplevel):

    def __init__(self, parent=None, user_id=None, dados_cartoes =None, trocar_mes=None, att_app=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.dados_cartoes = dados_cartoes
        self.trocar_mes = trocar_mes
        self.att_app = att_app

        # --------------- Criação da Jenela -----------------------
        self.title("Gerenciar Despesas")
        centralizar_janela(self, 1700, 800)
        self.transient(parent)
        self.focus_set() 

        # ---------------- Gerencimento de self ---------------------
        self.data_atual = datetime.now().date()


        # --------------- Configuração da janela/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=7) 
        self.grid_rowconfigure(0, weight=1)

         # ---------- formulário de cadastro -----------------------
        self.frame_cadastro = Cadastrar_despesas(parent=self, user_id=self.user_id, dados_cartoes=self.dados_cartoes, trocar_mes= self.trocar_mes, atualizar_lista= self.atualizar_lista)
        self.frame_cadastro.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")


        #-------------------- FRAME DA LISTA (Update/Delete) ----------------------------------
        self.frame_lista = Listar_despesas(parent=self, user_id=self.user_id, dados_cartoes= self.dados_cartoes, att_app = self.att_app, controle_dados=self.controle_dados)
        self.frame_lista.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
    
        self.frame_lista.grid_columnconfigure(0, weight=1)


    def controle_dados(self, dados):

        if dados:
            self.frame_cadastro.controla_campos(dados)
        else:
            print('ERRO: detalhar(despesas não mandou os dados esperados!)')


    def atualizar_lista(self):

        print("Atualizando a lista de despesas na tela...")
        self.frame_lista.listar()


#Módulo Cartões de Crédito
class Car_cred(ctk.CTkToplevel):

    def __init__(self,  parent=None, user_id=None, nomes_cards =None, att_app = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.att_app = att_app
        self.nomes_cards = nomes_cards

        # --------------- Criação da Jenela -----------------------
        self.title("Gerenciar Cartões de Crédito")
        centralizar_janela(self, 1200, 800)
        self.transient(parent)
        self.focus_set()

        # ---------------- Gerencimento de self ---------------------
        self.data_atual = datetime.now().date()

        # --------------- Configuração da janela/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=2) 
        self.grid_rowconfigure(0, weight=1)

         # ---------------- formulário de cadastro -----------------------
        self.frame_cadastro = Cadastrar_car_cred(parent=self, user_id=self.user_id, nomes_cards=self.nomes_cards, att_app= self.att_app, atualizar_lista= self.atualizar_lista)
        self.frame_cadastro.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        #------------------- FRAME DA LISTA (Update/Delete) ------------------------------
        self.frame_lista = Listar_car_cred(parent=self, user_id=self.user_id, controle_dados = self.controle_dados, att_app = self.att_app)
        self.frame_lista.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
    
        self.frame_lista.grid_columnconfigure(0, weight=1)


    def controle_dados(self, dados=None):
        
        if dados:
            self.frame_cadastro.controla_campos(dados)
        else:
            print('ERRO: Detalhar(car_cred não mandou os dados esperados!)')
        

    def atualizar_lista(self):


        print("Atualizando a lista de receitas na tela...")
        self.frame_lista.listar()


#Módulo Assinaturas
class Assinaturas(ctk.CTkToplevel):

    def __init__(self, parent=None, user_id=None, dados_cartoes=None, trocar_mes=None):
        super().__init__(parent)

        self.trocar_mes = trocar_mes
        self.user_id = user_id
        self.dados_cartoes = dados_cartoes 

        # --------------- Criação da Jenela -----------------------
        self.title("Gerenciar Assinaturas")
        centralizar_janela(self, 1800, 800)
        self.transient(parent) 
        self.focus_set() 
       

        # ---------------- Gerencimento de self ---------------------
        self.data_atual = datetime.now().date()
        self.data_futuro = (self.data_atual + relativedelta(years=73)).replace(day=1, month=1)


        # --------------- Configuração da janela/'labels' -----------------------

        self.grid_columnconfigure(0, weight=1) #coluna o - formulário
        self.grid_columnconfigure(1, weight=4) #coluna 1 - Lista
        self.grid_rowconfigure(0, weight=1)

         # ---------------- formulário de cadastro -----------------------
        self.frame_cadastro = Cadastrar_assinaturas(self, self.user_id, self.dados_cartoes, self.trocar_mes, self.atualizar_lista)
        self.frame_cadastro.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        #------------------- FRAME DA LISTA (Update/Delete) ------------------------------
        self.frame_lista = Listar_assinaturas(self, self.user_id, self.dados_cartoes, self.controle_dados, self.trocar_mes )
        self.frame_lista.grid(row=0, column=1, padx=(0,20), pady=20, sticky="nsew")
    
        self.frame_lista.grid_columnconfigure(0, weight=1)
        



    def controle_dados(self, dados=None):
        
        if dados:
            self.frame_cadastro.controla_campos(dados)
        else:
            print('ERRO: Detalhar(car_cred não mandou os dados esperados!)')
        

    def atualizar_lista(self):
        """Método que será chamado após um novo cadastro ou delete para recarregar a tabela"""
        
        print("Atualizando a lista de receitas na tela...")
        self.frame_lista.listar()


        
# --------------------- Detalhes da Fatura de Cartões ----------------------------

#Módulo Faturas
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
        self.focus_set() 

        self.grid_columnconfigure(0, weight=0) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)


        #-------------- FRAME Tabelas --------------------------
        self.frame_tabelas = Listar_faturas_cartao(self, self.id_user, self.id_card, self.nome_card, callback=self.calback)
        self.frame_tabelas.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
    


#Módulo Simulação
class Simulacao(ctk.CTkToplevel):

    def __init__(self, parent, id_user=None, despesas_avulsas=None, dados_cartoes=None, assinaturas_avulsas=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.id_user = id_user
        self.despesas_avulsas = despesas_avulsas
        self.dados_cartoes = dados_cartoes
        self.assinaturas_avulsas = assinaturas_avulsas


        # ---------------- Gerencimento de self ---------------------
        self.data_atual = datetime.now().date()

        # --------------- Configuração da janela/'labels' -----------------------
        self.title(f"Simulação de Despesas")
        centralizar_janela(self, 1600, 900)
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
        self.top_section.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ew")
        
        self.top_section.grid_columnconfigure(0, weight=1) # Bem-vindo
        self.top_section.grid_rowconfigure(0, weight=1) 
        

        # --------------- Main section ----------------------------------
        self.main_section = ctk.CTkFrame(self.container_principal, fg_color="transparent")
        self.main_section.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.main_section.grid_columnconfigure(0, weight=2) #formulário
        self.main_section.grid_columnconfigure(1, weight=5) #tabela
        self.main_section.grid_columnconfigure(2, weight=1) #gráfico
        self.main_section.grid_rowconfigure(0, weight=1)

        # ---------------- formulário de cadastro -----------------------
        self.frame_cadastro = Cadastrar_despesas(self.main_section, self.id_user, self.dados_cartoes, simulacao=True, controle_dados=self.controle_dados)

        self.frame_cadastro.grid(row=0, column=0, padx=10, pady=20, sticky="ns")

        # ------------------- FRAME TABELA -----------------------------
        self.tabela_frame = Listar_desp_tabela(parent=self.main_section, id_user=self.id_user, despesas_avulsas= self.despesas_avulsas, assinaturas_avulsas=self.assinaturas_avulsas, dados_cartoes=self.dados_cartoes)

        self.tabela_frame.grid(row=0, column=1, padx=10, pady=20, sticky="nsew") 

        self.tabela_frame.renderizar()

        # -------------------- FRAME GRÁFICO ------------------------------
        self.frame_grafico = Listar_cat_grafico(parent=self.main_section, id_user=self.id_user, despesas_avulsas= self.despesas_avulsas, assinaturas_avulsas=self.assinaturas_avulsas, dados_cartoes=self.dados_cartoes )

        self.frame_grafico.grid(row=0, column=2, padx=20, pady=20, sticky="nsew")

        self.frame_grafico.renderizar()



    def controle_dados(self, dados):

        if dados:
            pacote_dados = [dados, ]

            for dado in dados:
                cartao = dado.get('cartao')

                if cartao:
                    for card in self.dados_cartoes:
                        if card.get('nome') == cartao:
                           id_card = card.get('id_cartao')
                           fech = card.get('fechamento_fatura')
                           venc = card.get('vencimento_fatura')

                           dados_card = {
                               'id_cartao': {id_card},
                               'nome_cartao': {cartao},
                               'fechamento': {fech},
                               'vencimento': {venc},
                           }

                    if dados_card:
                        pacote_dados.append(dados_card)
                    else:
                        pacote_dados.append(None)

            # manipular as datas de compra e fechamento, considerar em qual fatura a compra aparece


            self.tabela_frame.renderizar(dados_simulacao=pacote_dados)
        else:
            print('ERRO: Forms não envio os dados esperados!')
        

