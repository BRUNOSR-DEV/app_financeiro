
from utils.helper import(
    centralizar_janela,gerar_opcoes_meses, formatar_moeda
)

from utils.audio_helper import(
    tocar_notificacao
)
from ui.forms import(
    Cadastrar_receitas, Cadastrar_despesas, Cadastrar_car_cred, Cadastrar_assinaturas
)

from utils.typedDict import(Despesa, Cartao)

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

        self.label_titulo = ctk.CTkLabel(self, text=f"Fatura: {nome_card}", font=("Arial", 22, "bold"))
        self.label_titulo.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        #-------------- FRAME Tabelas --------------------------
        self.frame_tabela = Listar_faturas_cartao(self, self.id_user, self.id_card, self.nome_card, callback=self.calback)
        self.frame_tabela.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        #self.frame_tabela.tabela_cartao()
    


#Módulo Simulação
class Simulacao(ctk.CTkToplevel):

    def __init__(self, parent, id_user=None, despesas_avulsas=None, dados_cartoes=None, assinaturas_avulsas=None, dados_usuario=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.id_user = id_user
        self.despesas_avulsas = despesas_avulsas
        self.dados_cartoes = dados_cartoes
        self.assinaturas_avulsas = assinaturas_avulsas
        self.dados_usuario = dados_usuario

        # ---------------- Gerencimento de self ---------------------
        self.data_atual = datetime.now().date()
        self.mes_atual = self.data_atual.month
        self.prox_mes =  (self.data_atual + relativedelta(months=1)).month
        self.seg_prox_mes =  (self.data_atual + relativedelta(months=2)).month
        self.ter_prox_mes =  (self.data_atual + relativedelta(months=3)).month
        self.quart_prox_mes =  (self.data_atual + relativedelta(months=4)).month

        opcoes = gerar_opcoes_meses()
        self.mes_atual_str = opcoes.get(self.mes_atual)
        self.prox_mes_str = opcoes.get(self.prox_mes)
        self.seg_prox_mes_str = opcoes.get(self.seg_prox_mes)
        self.ter_prox_mes_str = opcoes.get(self.ter_prox_mes)
        self.quart_prox_mes_str = opcoes.get(self.quart_prox_mes)

        self.nomes_datas = [self.mes_atual_str, self.prox_mes_str, self.seg_prox_mes_str, self.ter_prox_mes_str, self.quart_prox_mes_str]

        self.dados_select = []

        self.valor_renda = self.dados_usuario.get('sal_fixo', 0.0) 

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
        self.top_section.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.top_section.grid_columnconfigure(0, weight=1) # Bem-vindo
        self.top_section.grid_rowconfigure(0, weight=1)

                        # ------------ Apresentação ------------------
        texto = f"Simulação: Usuário - {self.dados_usuario.get('nome_completo')}!"
        self.nomeusuario_label = ctk.CTkLabel(self.top_section, text=texto, font=ctk.CTkFont(size=18, weight="bold"))
        self.nomeusuario_label.grid(row=0, column=0, padx=5, pady=(0, 10), sticky="w")

                            # --- DISPLAY DE RENDA FIXA ---
        self.frame_renda = ctk.CTkFrame(self.top_section, fg_color="transparent", width=150, height=100, corner_radius=15, border_width=3)
        self.frame_renda.grid(row=0, column=1, padx=10, pady=(0, 10), sticky="w") # Fica do lado do nome
        
        self.label_renda = ctk.CTkLabel(self.frame_renda, text=f"Renda Fixa: {formatar_moeda(self.valor_renda)}", text_color="#27ae60", font=ctk.CTkFont(size=18,weight="bold"))
        self.label_renda.pack(side="right", padx=(0, 10))

                            # -------- Botões de funções ------------
        
        self.label_mes = ctk.CTkLabel(self.top_section, text=f"Mês: ", font=ctk.CTkFont(size=16, weight="bold"))
        self.label_mes.grid(row=0, column=3, padx=10, pady=10, sticky="w")

        self.menu_mes = ctk.CTkOptionMenu(self.top_section, values=self.nomes_datas, command=self.trocar_mes, fg_color="#676666")
        self.menu_mes.grid(row=0, column=4, padx=10, pady=5, sticky="w")
        

        # --------------- Main section ----------------------------------
        self.main_section = ctk.CTkFrame(self.container_principal, fg_color="transparent")
        self.main_section.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.main_section.grid_columnconfigure(0, weight=1) #formulário
        self.main_section.grid_columnconfigure(1, weight=4) #tabela
        self.main_section.grid_columnconfigure(2, weight=3) #tab_fatura
        self.main_section.grid_rowconfigure(0, weight=1)

        # ---------------- formulário de cadastro -----------------------
        self.frame_cadastro = Cadastrar_despesas(self.main_section, self.id_user, self.dados_cartoes, simulacao=True, dados_select= self.dados_select, controle_dados=self.controle_dados)

        self.frame_cadastro.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # ------------------- FRAME TABELA -----------------------------
        self.tabela_frame = Listar_desp_tabela(parent=self.main_section, id_user=self.id_user, despesas_avulsas= self.despesas_avulsas, assinaturas_avulsas=self.assinaturas_avulsas, dados_cartoes=self.dados_cartoes)

        self.tabela_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew") 

        self.tabela_frame.renderizar()

        # -------------------- FRAME TABELA DO CARTÃO DE CRÉDITO  ------------------------------
        self.frame_tab_fatura = Listar_faturas_cartao(parent=self.main_section, id_user=self.id_user)

        self.frame_tab_fatura.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")



    def controle_dados(self, dados=None, controle_mes=None):

        if dados:
            tocar_notificacao('dv_sucesso', True)

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
                            fech = card.get('fechamento_fatura')
                            venc = card.get('vencimento_fatura')
                            
                            data_compra = dado.get('data_compra')

                            if not controle_mes:
                                if data_compra.day >= fech:
                                    controle_mes = (data_compra + relativedelta(months=1)).month

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


            self.tabela_frame.renderizar(controle_mes=controle_mes, escolha=str_mes, dados_simulacao=dados)

            if tem_cartao:
                escolha = f"{nome_cartao} - Mês: {str_mes}"
                self.frame_tab_fatura.tabela_cartao(id_user=self.id_user, id_card=id_card, controle_mes=controle_mes, escolha=escolha, dados_simulacao=dados)
            


    def trocar_mes(self, escolha):

        tocar_notificacao('open_w', True)

        dados= None
        if self.dados_select:
            dados = self.dados_select


        if self.mes_atual_str == escolha:
            controle_mes = self.mes_atual

            if not dados:
                self.tabela_frame.renderizar(controle_mes=controle_mes, escolha=escolha)
            else:
                self.controle_dados(dados=dados, controle_mes=controle_mes)
           
        elif self.prox_mes_str == escolha:
            controle_mes = self.prox_mes

            if not dados:
                self.tabela_frame.renderizar(controle_mes=controle_mes, escolha=escolha)
            else:
                self.controle_dados(dados=dados, controle_mes=controle_mes)

        elif self.seg_prox_mes_str == escolha:
            controle_mes = self.seg_prox_mes

            if not dados:
                self.tabela_frame.renderizar(controle_mes=controle_mes, escolha=escolha)
            else:
                self.controle_dados(dados=dados, controle_mes=controle_mes)

        elif self.ter_prox_mes_str == escolha:
            controle_mes = self.ter_prox_mes

            if not dados:
                self.tabela_frame.renderizar(controle_mes=controle_mes, escolha=escolha)
            else:
                self.controle_dados(dados=dados, controle_mes=controle_mes)
     
        elif self.quart_prox_mes_str == escolha:
            controle_mes = self.quart_prox_mes

            if not dados:
                self.tabela_frame.renderizar(controle_mes=controle_mes, escolha=escolha)
            else:
                self.controle_dados(dados=dados, controle_mes=controle_mes)

        else:
            controle_mes = self.mes_atual

            if not dados:
                self.tabela_frame.renderizar(controle_mes=controle_mes, escolha=escolha)
            else:
                self.controle_dados(dados=dados, controle_mes=controle_mes)

