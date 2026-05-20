
from models.conecte_bd import (
    deletar_receita, deletar_assinatura, deletar_cartao, deletar_despesa
     )

from utils.helper import(
    gerar_opcoes_meses, mysql_para_obj, formatar_moeda, data_para_exibicao, controle_data_parc_cc, centralizar_janela, controle_data_parc,
)

from utils.typedDict import(
    Dados_usuarios_db, Dados_receitas_db, Dados_despesas_db, Dados_cartoes_db, Dados_assinaturas_db, Pega_despesas_avulsas_bd, Pega_assinaturas_avulças_db, Pega_div_cartao_db, Pega_assinatuas_cartao_db, Pega_despesas_cartao_db, Despesa_simulacao
    )

from typing import List

from utils.audio_helper import tocar_notificacao 

from dateutil.relativedelta import relativedelta
from datetime import datetime

import customtkinter as ctk
ctk.set_appearance_mode('dark')

from CTkToolTip import *

#gráficos
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from decimal import Decimal
from collections import defaultdict 


#Filho de Módulo Receitas (crud_app.py)
class Listar_receitas(ctk.CTkFrame):

    def __init__(self,  parent=None, user_id=None, dados_receitas=None, controle_dados= None, callback_comandante_crud=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.dados_receitas: List[Dados_receitas_db] = dados_receitas
        self.controle_dados = controle_dados
        self.cdt_crud = callback_comandante_crud

         # --------------- Configuração da Frames/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.lista_frame = ctk.CTkScrollableFrame(self, label_text="Receitas Cadastradas")
        self.lista_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.lista_frame.grid_columnconfigure((0, 1, 3), weight=0) # Index, Valor e Data fixos
        self.lista_frame.grid_columnconfigure(2, weight=1) #Descriçao estica

        #ctk.CTkLabel(self.lista_frame, text="Receitas Cadastradas", font=("Arial", 18, "bold")).grid(row=0, column=0, padx=10, pady=10)

        #cabeçalho
        ctk.CTkLabel(self.lista_frame, text='#', font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Valor", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Descrição", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Data Recebimento", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5, sticky="w")

        self.listar()

       
    def listar(self, dados_receitas=None):

        for widget in self.lista_frame.winfo_children():
            widget.destroy()
        
        if dados_receitas is None:
            dados_receitas = self.dados_receitas


        if dados_receitas:

            for i, dado in enumerate(dados_receitas, start=1):
                #dado é o dict de uma receita
                valor = dado.get('valor_recebido')
                descricao = dado.get('descricao')
                data = dado.get('data')

                ctk.CTkLabel(self.lista_frame, text=str(i), font=('Ariel', 14)).grid(row=i, column=0, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=formatar_moeda(valor), text_color="#27ae60", font=('Ariel', 14)).grid(row=i, column=1, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=descricao, font=('Ariel', 14)).grid(row=i, column=2, padx=3, pady=1, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=data_para_exibicao(data), font=('Ariel', 14)).grid(row=i, column=3, padx=5, pady=2, sticky="e")

                btn_edit = ctk.CTkButton(self.lista_frame, text="📝", width=30, fg_color="transparent", hover_color="#34495e",
                                     command=lambda d=dado: self.confirmar_update(d))
                btn_edit.grid(row=i, column=4, padx=2)
                CTkToolTip(btn_edit, message="Editar Registro")

                btn_del = ctk.CTkButton(self.lista_frame, text="X", width=30, fg_color="#c0392b", hover_color="#e74c3c",
                                    command=lambda dados=dado: self.confirmar_delete(dados))
                btn_del.grid(row=i, column=5, padx=5)
                CTkToolTip(btn_del, 
                            message="Excluir Registro", 
                            delay=0.5,      # Tempo em segundos para aparecer
                            alpha=0.9,      # Transparência
                            bg_color="red" 
                            )


        self.lista_frame.grid_columnconfigure((4, 5), weight=0)


    def confirmar_update(self, dict_dados):

        print("Estou no'confirmar_update' mandando dados dict para crud_app")

        if dict_dados:
            self.controle_dados(dict_dados)
        else:
            self.controle_dados(None)



    def confirmar_delete(self, dados):
        
        popup = ctk.CTkToplevel(self)
        popup.title("Confirmação")
        centralizar_janela(popup, 300, 150)

        popup.grab_set()

        popup.grid_columnconfigure((0, 1), weight=1)

        label = ctk.CTkLabel(popup, text="Tem certeza que deseja\nexcluir esta receita?", font=("Arial", 14))
        label.grid(row=0, column=0, columnspan=2, pady=20)

        btn_cancelar = ctk.CTkButton(popup, text="Cancelar", fg_color="gray", hover_color="#555555",
                                 command=popup.destroy)
        btn_cancelar.grid(row=1, column=0, padx=10, pady=10)

        btn_confirmar = ctk.CTkButton(popup, text="Sim, excluir", fg_color="#c0392b", hover_color="#e74c3c",
                                  command=lambda: self.executar_delete(dados, popup))
        btn_confirmar.grid(row=1, column=1, padx=10, pady=10)


    def executar_delete(self, dados, popup):
        
        id_rec = dados.get('id_receita')
        descricao = dados.get('descricao')

        dado = {'id_rec': id_rec}

        sucesso = self.cdt_crud(deletar=dado)

        if sucesso:
            print(f"ID {id_rec} receita: '{descricao}'. Mandado pro espaço 🌌​")
            popup.destroy()

        else:
            print("Erro ao deletar")

            
#Filho de Módulo Despesas (crud_app.py)
class Listar_despesas(ctk.CTkFrame):

    def __init__(self,  parent=None, user_id=None, dados_cartoes =None, cb_comandante_crud=None, dados_despesas=None, controle_dados=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.dados_cartoes = dados_cartoes
        self.cdt_crud = cb_comandante_crud
        self.controle_dados = controle_dados
        self.dados_despesas: List[Dados_despesas_db] = dados_despesas

        # --------------- Configuração da Frames/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.lista_frame = ctk.CTkScrollableFrame(self, label_text="Despesas Cadastradas")
        self.lista_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.lista_frame.grid_columnconfigure((0, 1, 2, 3, 5, 6, 7, 8), weight=0) # valores/colunas fixas
        self.lista_frame.grid_columnconfigure(4, weight=1) #Descriçao estica

        #cabeçalho
        ctk.CTkLabel(self.lista_frame, text='#', font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text='Local', font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Valor Total", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Parcelas", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Descrição", font=ctk.CTkFont(weight="bold")).grid(row=0, column=4, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Categoria", font=ctk.CTkFont(weight="bold")).grid(row=0, column=5, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Data Compra", font=ctk.CTkFont(weight="bold")).grid(row=0, column=6, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Data P/Pagamento", font=ctk.CTkFont(weight="bold")).grid(row=0, column=7, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Método de Pagamento", font=ctk.CTkFont(weight="bold")).grid(row=0, column=8, padx=5, pady=5, sticky="w")

        self.listar()


    def listar(self, dados_despesas=None):
        
        for widget in self.lista_frame.winfo_children():
            if int(widget.grid_info().get("row", 0)) > 0:
                widget.destroy()

        if dados_despesas is None:
            dados_despesas = self.dados_despesas

        if dados_despesas:

            for i, dado in enumerate(dados_despesas, start=1):

                nome_card = None

                local = dado.get('local')
                valor_total = dado.get('valor_total')
                parcelas = dado.get('parcelas')
                descricao = dado.get('descricao')
                categoria = dado.get('categoria')
                data_compra = dado.get('data_compra')
                data_pp = dado.get('data_pp')
                
                if self.dados_cartoes:
                    for cartao in self.dados_cartoes:
                        if cartao.get('id_cartao') == dado.get('id_cc'):
                            nome_card = cartao.get('nome_cartao')
                            
                if nome_card is None:
                    nome_card = "Boleto/Avulça"

                #cabeçalho
                ctk.CTkLabel(self.lista_frame, text=str(i), font=('Ariel', 14)).grid(row=i, column=0, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=local, font=('Ariel', 14)).grid(row=i, column=1, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=formatar_moeda(valor_total), text_color="#27ae60", font=('Ariel', 14)).grid(row=i, column=2, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=parcelas, font=('Ariel', 14)).grid(row=i, column=3, padx=3, pady=1, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=descricao, font=('Ariel', 14)).grid(row=i, column=4, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=categoria, font=('Ariel', 14)).grid(row=i, column=5, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=data_compra, font=('Ariel', 14)).grid(row=i, column=6, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=data_pp, font=('Ariel', 14)).grid(row=i, column=7, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=nome_card, font=('Ariel', 14)).grid(row=i, column=8, padx=5, pady=2, sticky="w")

                btn_edit = ctk.CTkButton(self.lista_frame, text="📝", width=30, fg_color="transparent", hover_color="#34495e",
                                     command=lambda dados=dado: self.confirmar_update(dados))
                btn_edit.grid(row=i, column=9, padx=2)
                CTkToolTip(btn_edit, message="Editar Registro")

                btn_del = ctk.CTkButton(self.lista_frame, text="X", width=30, fg_color="#c0392b", hover_color="#e74c3c",
                                    command=lambda dados=dado: self.confirmar_delete(dados))
                btn_del.grid(row=i, column=10, padx=5)
                CTkToolTip(btn_del, 
                            message="Excluir Registro", 
                            delay=0.5,      # Tempo em segundos para aparecer
                            alpha=0.9,      # Transparência
                            bg_color="red" 
                            )
                

    def confirmar_update(self, dados):
        
        print("Estou no'confirmar_update' mandando dados (dict) para crud_app")

        if dados:
            self.controle_dados(dados)
        else:
            self.controle_dados(None)


    def confirmar_delete(self, dados):

        popup = ctk.CTkToplevel(self)
        popup.title("Confirmação")
        centralizar_janela(popup, 300, 150)

        popup.grab_set()

        popup.grid_columnconfigure((0, 1), weight=1)

        label = ctk.CTkLabel(popup, text="Tem certeza que deseja\nexcluir está despesa?", font=("Arial", 14))
        label.grid(row=0, column=0, columnspan=2, pady=20)

        btn_cancelar = ctk.CTkButton(popup, text="Cancelar", fg_color="gray", hover_color="#555555",
                                 command=popup.destroy)
        btn_cancelar.grid(row=1, column=0, padx=10, pady=10)

        btn_confirmar = ctk.CTkButton(popup, text="Sim, excluir!", fg_color="#c0392b", hover_color="#e74c3c",
                                  command=lambda: self.executar_delete(dados, popup))
        btn_confirmar.grid(row=1, column=1, padx=10, pady=10)


    def executar_delete(self, dados, popup):
        
        id_desp = dados.get('id_desp')
        local = dados.get('local')

        dados_detalhar = {
            'id_desp': id_desp
        }

        sucesso = self.cdt_crud(deletar= dados_detalhar)

        if sucesso:
            print(f"ID: {id_desp} Local: '{local}'. Mandado pro espaço 🌌​")

            popup.destroy()

        else:
            print("Erro ao deletar")


#Filho de Módulo Cartões de Crédito (crud_app.py)
class Listar_car_cred(ctk.CTkFrame):

    def __init__(self,  parent=None, user_id=None, dados_cartoes=None, nomes_cards =None, cb_comandante_crud=None, controle_dados = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.nomes_cards = nomes_cards
        self.controle_dados = controle_dados
        self.dados_cartoes: List[Dados_cartoes_db] = dados_cartoes
        self.cdt_crud = cb_comandante_crud

        # --------------- Configuração da Frames/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.lista_frame = ctk.CTkScrollableFrame(self, label_text="Cartões de Crédito Cadastrados")
        self.lista_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.lista_frame.grid_columnconfigure((0, 1, 2, 4), weight=0) 


        #cabeçalho
        ctk.CTkLabel(self.lista_frame, text='#', font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text='Nome', font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Limite", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Fechamento Fatura", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Vencimento Fatura", font=ctk.CTkFont(weight="bold")).grid(row=0, column=4, padx=5, pady=5, sticky="w")


        self.listar()


    def listar(self, dados_cartoes=None):

        for widget in self.lista_frame.winfo_children():
            if int(widget.grid_info().get("row", 0)) > 0:
                widget.destroy()

        if dados_cartoes is None:
            dados_cartoes = self.dados_cartoes

        if dados_cartoes:
            for i, dado in enumerate(dados_cartoes, start=1):

                nome = dado.get('nome_cartao')
                limite = dado.get('limite_cartao')
                dia_fec = dado.get('dia_fechamento')
                dia_venc = dado.get('dia_vencimento')

                #cabeçalho
                ctk.CTkLabel(self.lista_frame, text=str(i), font=('Ariel', 14)).grid(row=i, column=0, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=nome, font=('Ariel', 14)).grid(row=i, column=1, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=formatar_moeda(limite), text_color="#27ae60", font=('Ariel', 14)).grid(row=i, column=2, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=dia_fec, font=('Ariel', 14)).grid(row=i, column=3, padx=3, pady=1, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=dia_venc, font=('Ariel', 14)).grid(row=i, column=4, padx=5, pady=2, sticky="w")

                btn_edit = ctk.CTkButton(self.lista_frame, text="📝", width=30, fg_color="transparent", hover_color="#34495e",
                                     command=lambda dados=dado: self.confirmar_update(dados))
                btn_edit.grid(row=i, column=8, padx=2)
                CTkToolTip(btn_edit, message="Editar Registro")

                btn_del = ctk.CTkButton(self.lista_frame, text="X", width=30, fg_color="#c0392b", hover_color="#e74c3c",
                                    command=lambda dados=dado: self.confirmar_delete(dados))
                btn_del.grid(row=i, column=9, padx=5)
                CTkToolTip(btn_del, 
                            message="Excluir Registro", 
                            delay=0.5,      # Tempo em segundos para aparecer
                            alpha=0.9,      # Transparência
                            bg_color="red" 
                            )



    def confirmar_update(self, dados):
        print("Estou no'confirmar_update' mandando dados (dict) para crud_app")

        if dados:
            self.controle_dados(dados)
        else:
            self.controle_dados(None)


    def confirmar_delete(self, dados):

        popup = ctk.CTkToplevel(self)
        popup.title("Confirmação")
        centralizar_janela(popup, 300, 150)

        popup.grab_set()

        popup.grid_columnconfigure((0, 1), weight=1)

        label = ctk.CTkLabel(popup, text="Tem certeza que deseja\nexcluir este Cartão?", font=("Arial", 14))
        label.grid(row=0, column=0, columnspan=2, pady=20)

        btn_cancelar = ctk.CTkButton(popup, text="Cancelar", fg_color="gray", hover_color="#555555",
                                 command=popup.destroy)
        btn_cancelar.grid(row=1, column=0, padx=10, pady=10)

        btn_confirmar = ctk.CTkButton(popup, text="Sim, excluir!", fg_color="#c0392b", hover_color="#e74c3c",
                                  command=lambda: self.executar_delete(dados, popup))
        btn_confirmar.grid(row=1, column=1, padx=10, pady=10)


    def executar_delete(self, dados, popup):
        
        id_card = dados.get('id_cartao')
        nome = dados.get('nome_cartao')

        dados_delete = {
            'id_card': id_card
        }
        sucesso = self.cdt_crud(deletar=dados_delete)

        if sucesso:

            print(f"ID: {id_card} None: '{nome}'. Mandado pro espaço 🌌​")

            popup.destroy()

        else:
            print("Erro ao deletar")


#Filho de Módulo Assinaturas (crud_app.py)      
class Listar_assinaturas(ctk.CTkFrame):

    def __init__(self, parent=None, user_id=None, dados_cartoes=None, dados_assinaturas=None, controle_dados=None, cb_comandante_crud=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.dados_cartoes: List[Dados_cartoes_db] = dados_cartoes 
        self.dados_assinaturas: List[Dados_assinaturas_db] = dados_assinaturas  
        self.controle_dados = controle_dados
        self.cdt_crud = cb_comandante_crud

        # --------------- Configuração da Frames/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.lista_frame = ctk.CTkScrollableFrame(self, label_text="Assinaturas Cadastradas")
        self.lista_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.lista_frame.grid_columnconfigure((0, 1, 2, 4, 5, 6, 7), weight=0) # valores/colunas fixas
        self.lista_frame.grid_columnconfigure(3, weight=1) #Descriçao estica

        #cabeçalho
        ctk.CTkLabel(self.lista_frame, text='#', font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text='Nome', font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Valor", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Descrição", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Data Aquisisão", font=ctk.CTkFont(weight="bold")).grid(row=0, column=4, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Data P/Pagamento", font=ctk.CTkFont(weight="bold")).grid(row=0, column=5, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Categoria", font=ctk.CTkFont(weight="bold")).grid(row=0, column=6, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Método de Pagamento", font=ctk.CTkFont(weight="bold")).grid(row=0, column=7, padx=5, pady=5, sticky="w")

        self.listar()


    def listar(self, dados_ass=None):

        for widget in self.lista_frame.winfo_children():
            if int(widget.grid_info().get("row", 0)) > 0:
                widget.destroy()

        if dados_ass is None:
            dados_ass = self.dados_assinaturas

        if dados_ass:
            
            for i, dado in enumerate(dados_ass, start=1):

                nome_card = None

                nome = dado.get('nome')
                valor = dado.get('valor')
                desc = dado.get('descricao')
                data_aq = dado.get('data_aquisicao')
                data_pp = dado.get('data_prim_pag')
                cat = dado.get('categoria')

                if self.dados_cartoes:
                    for cartao in self.dados_cartoes:
                        if cartao.get('id_cartao') == dado.get('id_cc'):
                            nome_card = cartao.get('nome_cartao')
                            
                if nome_card is None:
                    nome_card = "Boleto/Avulça"

                ctk.CTkLabel(self.lista_frame, text=str(i), font=('Ariel', 14)).grid(row=i, column=0, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=nome, font=('Ariel', 14)).grid(row=i, column=1, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=formatar_moeda(valor), text_color="#27ae60", font=('Ariel', 14)).grid(row=i, column=2, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=desc, font=('Ariel', 14)).grid(row=i, column=3, padx=3, pady=1, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=data_aq, font=('Ariel', 14)).grid(row=i, column=4, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=data_pp, font=('Ariel', 14)).grid(row=i, column=5, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=cat, font=('Ariel', 14)).grid(row=i, column=6, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=nome_card, font=('Ariel', 14)).grid(row=i, column=7, padx=5, pady=2, sticky="w")

                btn_edit = ctk.CTkButton(self.lista_frame, text="📝", width=30, fg_color="transparent", hover_color="#34495e",
                                     command=lambda dados=dado: self.confirmar_update(dados))
                btn_edit.grid(row=i, column=8, padx=2)
                CTkToolTip(btn_edit, message="Editar Registro")

                btn_del = ctk.CTkButton(self.lista_frame, text="X", width=30, fg_color="#c0392b", hover_color="#e74c3c",
                                    command=lambda dados=dado: self.confirmar_delete(dados))
                btn_del.grid(row=i, column=9, padx=5)
                CTkToolTip(btn_del, 
                            message="Excluir Registro", 
                            delay=0.5,      # Tempo em segundos para aparecer
                            alpha=0.9,      # Transparência
                            bg_color="red" 
                            )


    def confirmar_update(self, dados):
        print("Estou no'confirmar_update' mandando dados (dict) para crud_app")

        if dados:
            self.controle_dados(dados)
        else:
            self.controle_dados(None)


    def confirmar_delete(self, dados):

        popup = ctk.CTkToplevel(self)
        popup.title("Confirmação")
        centralizar_janela(popup, 300, 150)

        popup.grab_set()

        popup.grid_columnconfigure((0, 1), weight=1)

        label = ctk.CTkLabel(popup, text="Tem certeza que deseja\nexcluir esta assinatura?", font=("Arial", 14))
        label.grid(row=0, column=0, columnspan=2, pady=20)

        btn_cancelar = ctk.CTkButton(popup, text="Cancelar", fg_color="gray", hover_color="#555555",
                                 command=popup.destroy)
        btn_cancelar.grid(row=1, column=0, padx=10, pady=10)

        btn_confirmar = ctk.CTkButton(popup, text="Sim, excluir!", fg_color="#c0392b", hover_color="#e74c3c",
                                  command=lambda: self.executar_delete(dados, popup))
        btn_confirmar.grid(row=1, column=1, padx=10, pady=10)



    def executar_delete(self, dados, popup):
        
        id_ass = dados.get('id_ass')
        nome = dados.get('nome')

        dados_delete = {
            'id_ass': id_ass
        }

        sucesso = self.cdt_crud(deletar=dados_delete)

        if sucesso:
            print(f"ID: {id_ass} Assinatura: '{nome}'. Mandado pro espaço 🌌​")
            tocar_notificacao('dv_delete', True)

            popup.destroy()

        else:
            print("Erro ao deletar")



# ------------------- Detalhamento Tabela e Gráfico - DASHBOARD -------------------------------

#Filho de módulo Main_app e Simulação
class Listar_desp_tabela(ctk.CTkFrame):

    def __init__(self, parent=None, id_user=None, despesas_avulsas=None, dados_cartoes=None, assinaturas_avulsas=None, dados_prontos=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
    
        self.id_user = id_user
        self.despesas_avulsas = despesas_avulsas #------ return: dict de despesas avulsas=(sem cartão)
        self.dados_cartoes = dados_cartoes # -------- return: dict de dados cartoes
        self.assinaturas_avulsas = assinaturas_avulsas # -----------return: dict de assinaturas avulsas
        self.dados_prontos= dados_prontos

        #???????????/???????
        #self.desp_cartoes = desp_cartoes # ---------- return: dict de despesas no cartão
        #self.assin_cartoes = assin_cartoes # ---------- return: dict de assinaturas no cartão 

        self.data_atual = datetime.now()
        self.mes_atual = self.data_atual.month
        self.prox_mes =  (self.data_atual + relativedelta(months=1)).month
        self.seg_prox_mes =  (self.data_atual + relativedelta(months=2)).month

        opcoes = gerar_opcoes_meses()
        self.mes_atual_str = opcoes.get(self.mes_atual)
        self.prox_mes_str = opcoes.get(self.prox_mes)
        self.seg_prox_mes_str = opcoes.get(self.seg_prox_mes)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # FRAME TABELA
        self.tabela_frame = ctk.CTkScrollableFrame(self, label_text=f"Despesas Detalhadas: {self.mes_atual_str} / {self.data_atual.year}")
        self.tabela_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew") 

        self.tabela_frame.grid_columnconfigure(0, weight=1)
        self.tabela_frame.grid_rowconfigure(0, weight=1)

        #self.tabela_frame.grid_columnconfigure((0, 1, 2, 3), weight=0) # valores/colunas fixas
        #self.tabela_frame.grid_columnconfigure(4, weight=1) #Descriçao estica

    
    
    def renderizar(self, controle_mes=None, escolha=None, dados_simulacao=None):

        for widget in self.tabela_frame.winfo_children():
            widget.destroy()

        if controle_mes is None:
            controle_mes = int(datetime.now().month)


        despesas: List[Pega_despesas_avulsas_bd] = self.despesas_avulsas
        assin: List[Pega_assinaturas_avulças_db] = self.assinaturas_avulsas

        total_avulsas = Decimal('0.0')
        total_cards = Decimal('0.0')
        #Lógica para montar lista com o total de cada cartão

        lista_faturas_resumo = []


        if self.dados_prontos: #se tem cartão! entra no bloco
            
            for pacote in self.dados_prontos:
                pacote: Pega_div_cartao_db = pacote

                info_cartao = pacote.get('info', {})

                nome_cartao = info_cartao.get('nome_cartao')
                id_cartao = info_cartao.get('id_cartao') 
                
                despesas_do_cartao = pacote.get('despesas', {})
                assin_card = pacote.get('assinaturas', {})
            
                total_deste_cartao = Decimal('0.0')
                data_vencimento_fatura = None

                if assin_card or despesas_do_cartao or dados_simulacao:

                    if assin_card:

                        for ass in assin_card:

                            dia_f = ass.get('dia_fechamento_cc')
                            dia_v = ass.get('dia_vencimento_cc')
                            data_aquisicao = ass.get('data_aquisicao')

                            resultado = controle_data_parc_cc(data_aquisicao, dia_f, dia_v, controle_mes= controle_mes)
                            _, entra_na_fatura, _ = resultado

                            if entra_na_fatura:
                                valor = Decimal(str(ass.get('valor')))
                                total_deste_cartao += valor


                    if despesas_do_cartao:

                        for desp in despesas_do_cartao:

                            data_compra = mysql_para_obj(desp.get('data_compra'))
                            dia_venc = desp.get('dia_vencimento')
                            fechamento = desp.get('dia_fechamento')
                            parcelas = desp.get('parcelas')


                            resultado = controle_data_parc_cc(data_compra, fechamento, dia_venc, parcelas, controle_mes= controle_mes)
                            _, entra_na_fatura, controle_data = resultado

                            if entra_na_fatura:
                                valor_mensal = Decimal(str(desp.get('valor_total'))) / parcelas
                                total_deste_cartao += valor_mensal
                                data_vencimento_fatura = controle_data 


                
                    #---------- simulação - Inserindo o valor na fatura do cartão informado ----------------------
                    mensalidade_simulacao_card  = Decimal('0.0')

                    if not data_vencimento_fatura:
                        dia_venc_base = info_cartao.get('vencimento_fatura')
                        if dia_venc_base:
                            # Assumindo que a fatura cai no mês de controle_mes
                            ano_atual = datetime.now().year
                            # Tratamento simples para virada de ano, caso precise
                            data_vencimento_fatura = datetime(ano_atual, controle_mes, int(dia_venc_base)).date()


                    if dados_simulacao:
                    
                        for _, dado in enumerate(dados_simulacao):
                        
                            info_card = dado.get('info_cartao')

                            if info_card and isinstance(info_card, dict):  #if type(met_pag) is dict: 

                                data_compra_simulacao = dado.get('data_compra')
                                parcelas_simulacao = int(dado.get('parcelas'))

                                id_card = info_card.get('id_cartao')
                                venc_card_simulacao = info_card.get('vencimento')
                                fech_card_simulacao = info_card.get('fechamento')
                            
                                if str(id_card) == str(id_cartao): #id_cartao é o cartao do loop principal

                                    resultado = controle_data_parc_cc(data_compra_simulacao, fech_card_simulacao, venc_card_simulacao, parcelas_simulacao, controle_mes= controle_mes)

                                    _, entra_na_fatura, controle_data = resultado

                                    if entra_na_fatura:
                                        data_vencimento_fatura = controle_data 
                                        mensalidade_simulacao_card += Decimal(str(dado.get('valor_total'))) / parcelas_simulacao


                    # Se o cartão tem fatura para pagar, guardamos na lista

                    if (total_deste_cartao > Decimal('0.0')) or (mensalidade_simulacao_card > Decimal('0.0')):
                        lista_faturas_resumo.append({
                            'local': f"Fatura - {nome_cartao}",
                            'valor': (total_deste_cartao + mensalidade_simulacao_card),
                            'vencimento': data_vencimento_fatura
                        })

    
        # Se tiver despesas avulsas, faturas de cartão, assinaturas ou simulação, desenha a tabela.
        if despesas or lista_faturas_resumo or assin or dados_simulacao:
        
            # Cabeçalho
            ctk.CTkLabel(self.tabela_frame, text="Local/Nome", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self.tabela_frame, text="Parcelas", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self.tabela_frame, text="Mensalidade/Valor", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5, sticky="e")
            ctk.CTkLabel(self.tabela_frame, text="Vencimento", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5, sticky="w")

            linha = 1

            total_ass_avulcas = Decimal('0.0')

            if assin: 
                
                for ass in assin:

                        data_pp = mysql_para_obj(ass['data_pp'])
                        dia_venc = ass['dia_vencimento']
                        nome = ass['nome']
                        valor = ass["valor"]

                        resultado = controle_data_parc(data_pp, dia_venc, total_parcelas=None, controle_mes = controle_mes )
                        str_sit, entra_no_mes, data_vencimento = resultado

                        if entra_no_mes:

                            total_ass_avulcas += Decimal(str(valor))

                            ctk.CTkLabel(self.tabela_frame, text=nome).grid(row=linha, column=0, padx=5, pady=2, sticky="w")
                            ctk.CTkLabel(self.tabela_frame, text=str_sit).grid(row=linha, column=1, padx=3, pady=1, sticky="w")
                            ctk.CTkLabel(self.tabela_frame, text=formatar_moeda(valor), justify=ctk.LEFT, text_color="red").grid(row=linha, column=2, padx=5, pady=2, sticky="e")
                            ctk.CTkLabel(self.tabela_frame, text=data_para_exibicao(data_vencimento)).grid(row=linha, column=3, padx=5, pady=2, sticky="w")


                        linha += 1
            else:
                print('lista assinaturas estava vazia')

            if despesas:

                for _, dados in enumerate(despesas):
                    primeira_parc = mysql_para_obj(dados['data_pp'])
                    dia_venc = primeira_parc.day
                
                    resultado_avulso = controle_data_parc(primeira_parc, dia_venc, dados.get('parcelas'), controle_mes= controle_mes)

                    str_parcela, control_parc, data_vencimento = resultado_avulso

                    dia_venc = int(primeira_parc.day)

                    if data_vencimento:
                        data_fatura = data_vencimento
                    else:
                        data_fatura = datetime.now().replace(day=dia_venc)

                    if control_parc:
                        valor_mensal = Decimal(str(dados.get('valor_total'))) / dados.get('parcelas')
                    
                        ctk.CTkLabel(self.tabela_frame, text=dados.get('local')).grid(row=linha, column=0, padx=5, pady=2, sticky="w")
                        ctk.CTkLabel(self.tabela_frame, text=str_parcela).grid(row=linha, column=1, padx=3, pady=1, sticky="w")
                        ctk.CTkLabel(self.tabela_frame, text=formatar_moeda(valor_mensal), justify=ctk.LEFT, text_color="green").grid(row=linha, column=2, padx=5, pady=2, sticky="e")
                        ctk.CTkLabel(self.tabela_frame, text=data_para_exibicao(data_fatura)).grid(row=linha, column=3, padx=5, pady=2, sticky="w")

                        total_avulsas += valor_mensal
                    
                        linha += 1
            else:
                print('lista despesas estava vazia')
          
            # Desenha o Resumo das Faturas dos Cartões
            if lista_faturas_resumo:

                for fatura in lista_faturas_resumo:

                    ctk.CTkLabel(self.tabela_frame, text=fatura['local']).grid(row=linha, column=0, padx=5, pady=2, sticky="w")
                    ctk.CTkLabel(self.tabela_frame, text="-").grid(row=linha, column=1, padx=3, pady=1, sticky="w") 
                    ctk.CTkLabel(self.tabela_frame, text=formatar_moeda(fatura['valor']), justify=ctk.LEFT, text_color="orange").grid(row=linha, column=2, padx=5, pady=2, sticky="e")
            
                    # Formata a data se ela não vier vazia
                    venc_str = data_para_exibicao(fatura['vencimento']) if fatura['vencimento'] else "N/A"
                    ctk.CTkLabel(self.tabela_frame, text=venc_str).grid(row=linha, column=3, padx=5, pady=2, sticky="w")

                    total_cards += fatura['valor']

                    linha += 1
            else:
                print('lista faturas estava vazia')



            # -------------- SIMULAÇÃO - DESENHANDO LINHA AVULSA COM OS DADOS INFORMADOS NO FORMS -----------
            if dados_simulacao:
                
                for dado in dados_simulacao:

                    info_card = dado['info_cartao']

                    if info_card is None:

                        local_simulacao = dado.get('local')
                        data_compra_simulacao = dado.get('data_compra')
                        data_pp_simulacao = dado.get('prim_data_pag')
                        parcelas_simulacao = int(dado.get('parcelas'))

                        dia_venc_simulacao = data_pp_simulacao.day

                        if data_pp_simulacao:

                            resultado_avulso_sim = controle_data_parc(data_pp_simulacao, dia_venc_simulacao, parcelas_simulacao, controle_mes= controle_mes)
                            str_parcela, control_parc, data_vencimento = resultado_avulso_sim

                            if data_vencimento:
                                data_fatura = data_vencimento
                            else:
                                data_fatura = datetime.now().replace(day=dia_venc)

                            if control_parc:
                                mensalidade_simulacao_avulsa = Decimal(str(dado['valor_total'])) / parcelas_simulacao

                                ctk.CTkLabel(self.tabela_frame, text=local_simulacao).grid(row=linha, column=0, padx=5, pady=2, sticky="w")
                                ctk.CTkLabel(self.tabela_frame, text=str_parcela).grid(row=linha, column=1, padx=3, pady=1, sticky="w")
                                ctk.CTkLabel(self.tabela_frame, text=formatar_moeda(mensalidade_simulacao_avulsa), justify=ctk.LEFT, text_color="green").grid(row=linha, column=2, padx=5, pady=2, sticky="e")
                                ctk.CTkLabel(self.tabela_frame, text=data_para_exibicao(data_fatura)).grid(row=linha, column=3, padx=5, pady=2, sticky="w")

                                total_avulsas += mensalidade_simulacao_avulsa

                                linha += 1
                        else:
                            print('ERRO: Data do primeiro pagamento nula...')



            ctk.CTkLabel(
                self.tabela_frame, 
                text="TOTAL DESPESAS:", 
                font=ctk.CTkFont(weight="bold", size=14)
            ).grid(row=linha, column=0, columnspan=2, padx=5, pady=(20, 5), sticky="e")

            ctk.CTkLabel(
                self.tabela_frame, 
                text=formatar_moeda((total_avulsas + total_cards + total_ass_avulcas)), 
                font=ctk.CTkFont(weight="bold", size=14), 
                text_color="red" 
            ).grid(row=linha, column=2, padx=5, pady=(20, 5), sticky="e")

            self.tabela_frame.grid_columnconfigure(2, weight=1)
            
            tt_dividas = (total_avulsas + total_cards + total_ass_avulcas)

            
            if escolha:
                self.tabela_frame.configure(label_text=f"Detalhes do Despesas: {escolha}")


            return tt_dividas

        else:
            ctk.CTkLabel(self.tabela_frame, text="Nenhum pagamento previsto.").grid(row=0, column=0, padx=10, pady=10)
            self.tabela_frame.grid_columnconfigure(2, weight=1)


#Filho de módulo Main_app
class Listar_cat_grafico(ctk.CTkFrame):

    def __init__(self, parent=None, id_user=None, despesas_avulsas=None, dados_cartoes=None, assinaturas_avulsas=None, dados_prontos=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.id_user = id_user
        self.despesas_avulsas = despesas_avulsas
        self.dados_cartoes = dados_cartoes
        self.assinaturas_avulsas = assinaturas_avulsas
        self.dados_prontos: Pega_div_cartao_db = dados_prontos

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        #FRAME GRÁFICO
        self.grafico_frame = ctk.CTkFrame(self)
        self.grafico_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.grafico_frame.grid_columnconfigure(0, weight=1)
        self.grafico_frame.grid_rowconfigure(0, weight=1)

        
    
    def renderizar(self, controle_mes=None):
        

        print(f"Renderizando gráfico")

        for widget in self.grafico_frame.winfo_children():
            widget.destroy()

        if controle_mes is None:
            controle_mes = datetime.now().month

        assin_avulsas: List[Pega_assinaturas_avulças_db] = self.assinaturas_avulsas
        desp_avulsas: List[Pega_despesas_avulsas_bd]= self.despesas_avulsas

        gastos_por_categoria = defaultdict(Decimal)
        total_previsto = Decimal('0.0')
    
        

        if self.dados_prontos:

            for pacote in self.dados_prontos:
                pacote: Pega_div_cartao_db = pacote

                desp_cc = pacote.get('despesas', {})
                assin_card = pacote.get('assinaturas', {})

            
                if assin_card:
                    for ass in assin_card:

                        dia_f = ass.get('dia_fechamento_cc')
                        dia_v = ass.get('dia_vencimento_cc')
                        data_aquisicao = ass.get('data_aquisicao')

                        # Verifica se entra na fatura atual - Método chamado de utils/helper
                        resultado = controle_data_parc_cc(data_aquisicao, dia_f, dia_v, controle_mes= controle_mes)
                        _, entra_na_fatura, _ = resultado

                        if entra_na_fatura:

                            valor = Decimal(str(ass.get('valor')))
                            categoria = ass.get('categoria', 'Outros') # SOMA NO DICIONÁRIO USANDO A CATEGORIA
                            gastos_por_categoria[categoria] += valor
                            total_previsto += valor

                if desp_cc:
                    for desp in desp_cc:

                        data_compra = mysql_para_obj(desp.get('data_compra'))
                        dia_venc = desp.get('dia_vencimento')
                        fechamento = desp.get('dia_fechamento')
                        parcelas = desp.get('parcelas')

                        resultado = controle_data_parc_cc(data_compra, fechamento, dia_venc, parcelas, controle_mes= controle_mes)
                        _, entra_na_fatura, _ = resultado

                        if entra_na_fatura:

                            valor_mensal = Decimal(str(desp.get('valor_total'))) / parcelas
                            categoria = desp.get('categoria', 'Outros') 
                            gastos_por_categoria[categoria] += valor_mensal
                            total_previsto += valor_mensal



        if desp_avulsas or assin_avulsas:

            if desp_avulsas:
                for desp in desp_avulsas:

                    primeira_parc = mysql_para_obj(desp["data_pp"])
                    parcelas = desp['parcelas']
                    dia_venc = desp['dia_vencimento']
        
                    resultado = controle_data_parc(primeira_parc, dia_venc , parcelas, controle_mes = controle_mes)
                    _, entra_no_mes, _ = resultado

                    if entra_no_mes:

                        valor_mensal = Decimal(str(desp.get('valor_total'))) / parcelas
                        categoria = desp.get('categoria', 'Outros')
                        gastos_por_categoria[categoria] += valor_mensal
                        total_previsto += valor_mensal

            if assin_avulsas:

                for ass in assin_avulsas:

                    data_pp = mysql_para_obj(ass.get('data_pp'))
                    dia_venc = ass.get('dia_vencimento')
                    valor = ass.get('valor')

                    resultado = controle_data_parc(data_pp, dia_venc, controle_mes = controle_mes)
                    _, entra_no_mes, _ = resultado

                    if entra_no_mes:

                        total_previsto += valor
                        categoria = ass.get('categoria', 'Outros')
                        gastos_por_categoria[categoria] += valor
            
        #Verifica se tem algo para mostrar
        if total_previsto == Decimal('0.0'):
            ctk.CTkLabel(self.grafico_frame, text="Nenhum gasto para este mês.").grid(row=0, column=0, padx=20, pady=20)
            return

        # Prepara os dados para o Matplotlib
        categorias = list(gastos_por_categoria.keys())
        totais = list(gastos_por_categoria.values())

        # 5. Criação do Gráfico
        fig, ax = plt.subplots(figsize=(5, 5), facecolor='#2b2b2b') # Cor de fundo igual ao CTk
        ax.pie(
            totais, 
            labels=categorias, 
            autopct='%1.1f%%', 
            startangle=90,
            textprops={'fontsize': 8, 'color': 'white'}
        )
        ax.axis('equal')
    
        # Título (Ajuste o gerar_opcoes_meses conforme sua estrutura)
        ax.set_title(f"Distribuição de Gastos\nTotal: {formatar_moeda(total_previsto)}", color='white', fontsize=12)

        # 6. Renderização no CustomTkinter
        canvas = FigureCanvasTkAgg(fig, master=self.grafico_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, sticky="nsew")
        canvas.draw()


#-----------------  Detalhes da fatura dos cartões -----------------------------------------

#Filho de Módulo Faturas (crud_app.py)
class Listar_faturas_cartao(ctk.CTkFrame):
    
    def __init__(self, parent=None, id_user=None, id_card=None, nome_card=None, dados_prontos=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.id_user = id_user
        self.id_card = id_card
        self.nome_card = nome_card
        self.dados_prontos = dados_prontos

        # ---------------- Gerencimento de self ---------------------

        self.data_atual = datetime.now().date()
        self.mes_atual = self.data_atual.month
        self.prox_mes =  (self.data_atual + relativedelta(months=1)).month
        self.seg_prox_mes =  (self.data_atual + relativedelta(months=2)).month

        opcoes = gerar_opcoes_meses()
        self.nomes_datas = [
            opcoes.get(self.mes_atual, 'Mês inválido'),
            opcoes.get(self.prox_mes, 'Mês inválido'),
            opcoes.get(self.seg_prox_mes, 'Mês inválido'),
            
        ]
        self.mes_atual_str = opcoes.get(self.mes_atual)
        self.prox_mes_str = opcoes.get(self.prox_mes)
        self.seg_prox_mes_str = opcoes.get(self.seg_prox_mes)
        

        # --------------- Configuração da Frames/'labels' -----------------------

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # mês vigente
        self.tabela_frame = ctk.CTkScrollableFrame(self, label_text=f"Pagamentos Detalhados: [ ] - Mês: {self.mes_atual_str} / {self.data_atual.year}"
        )
        self.tabela_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.container_dados = ctk.CTkFrame(self.tabela_frame, fg_color="transparent")
        self.container_dados.pack(fill="both", expand=True)



    
    def tabela_cartao(self, id_user, id_card, escolha=None, controle_mes=None, dados_simulacao=None): #Dados_prontos TRUE

        for widget in self.container_dados.winfo_children():
            widget.destroy()
        
        if controle_mes is None:
            controle_mes = datetime.now().month

        dados_desp_card = []
        assin = []
        total_fatura = Decimal('0.0')
        total_assin = Decimal('0.0')

        if self.dados_prontos:
            for pacote in self.dados_prontos:
                
                # Auto-complete
                pacote: Pega_div_cartao_db = pacote

                #opção se não der certo - cala a boca py
                    #pacote = cast(Pega_div_cartao_db, pacote)

                info_cartao = pacote.get('info', {})
                
                # Se achou o cartão exato, pega os dados e QUEBRA o loop!
                if str(info_cartao.get('id_cartao')) == str(id_card):
                    dados_desp_card = pacote.get('despesas', [])
                    assin = pacote.get('assinaturas', [])
                    break


        if dados_desp_card or assin or dados_simulacao:

                        # Cabeçalho
            ctk.CTkLabel(self.container_dados, text="Local.", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self.container_dados, text="Parcelas", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5, sticky="e")
            ctk.CTkLabel(self.container_dados, text="Valor", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self.container_dados, text="Vencimento", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5, sticky="w")

            linha = 1

            if assin:
                for ass in assin:

                    data_aquisicao = ass.get('data_aquisicao')
                    nome = ass.get('nome')
                    valor = ass.get('valor')
                    dia_f = ass.get('dia_fechamento_cc')
                    dia_v = ass.get('dia_vencimento_cc')

                    resultado = controle_data_parc_cc(data_aquisicao, dia_f, dia_v, controle_mes = controle_mes )
                    str_sit, entra_no_mes, data_vencimento = resultado

                    if entra_no_mes:

                        total_assin += Decimal(str(valor))

                        ctk.CTkLabel(self.container_dados, text=nome).grid(row=linha, column=0, padx=5, pady=2, sticky="w")
                        ctk.CTkLabel(self.container_dados, text=str_sit).grid(row=linha, column=1, padx=3, pady=1, sticky="w")
                        ctk.CTkLabel(self.container_dados, text=formatar_moeda(valor), justify=ctk.LEFT, text_color="red").grid(row=linha, column=2, padx=5, pady=2, sticky="e")
                        ctk.CTkLabel(self.container_dados, text=data_para_exibicao(data_vencimento)).grid(row=linha, column=3, padx=5, pady=2, sticky="w")


                        linha += 1

            if dados_desp_card:

                for _, item_desp  in enumerate(dados_desp_card):
                
                    data_compra = mysql_para_obj(item_desp.get('data_compra'))
                    fecha_fatura = item_desp.get('dia_fechamento')
                    dia_venc = item_desp.get('dia_vencimento')
                    parcelas = item_desp.get('parcelas')


                    resultado = controle_data_parc_cc(data_compra, fecha_fatura ,dia_venc, parcelas, controle_mes=controle_mes)

                    str_parc, control_parc, controle_data = resultado


                    if control_parc:
                    
                        valor_mensal = Decimal(str(item_desp.get('valor_total'))) / item_desp.get('parcelas')
                        total_fatura += valor_mensal

                        ctk.CTkLabel(self.container_dados, text=item_desp.get('local')).grid(row=linha, column=0, padx=5, pady=2, sticky="w")

                        ctk.CTkLabel(self.container_dados, text=str_parc).grid(row=linha, column=1, padx=3, pady=1, sticky="w")

                        ctk.CTkLabel(self.container_dados, text=formatar_moeda(valor_mensal),justify=ctk.LEFT, text_color="green").grid(row=linha, column=2, padx=5, pady=2, sticky="e")

                        ctk.CTkLabel(self.container_dados, text=data_para_exibicao(controle_data)).grid(row=linha, column=3, padx=5, pady=2, sticky="w")

                        linha += 1 


            if dados_simulacao:
                
                for dado in dados_simulacao:

                    dado: Despesa_simulacao
                    
                    info_card = dado.get('info_cartao')

                    if info_card and isinstance(info_card, dict):

                        if str(info_card['id_cartao']) == str(id_card):

                            local_simulacao = dado['local']
                            data_compra_simulacao = dado.get('data_compra')
                            parcelas_simulacao = int(dado.get('parcelas'))

                            venc_card_simulacao = info_card['vencimento']
                            fech_card_simulacao = info_card['fechamento']

                            if venc_card_simulacao:

                                resultado = controle_data_parc_cc(data_compra_simulacao, fech_card_simulacao, venc_card_simulacao, parcelas_simulacao, controle_mes= controle_mes)

                                str_parcela, control_parc, data_vencimento = resultado

                                if control_parc:
                                    mensalidade_simulacao_avulsa = Decimal(str(dado['valor_total'])) / parcelas_simulacao

                                    ctk.CTkLabel(self.container_dados, text=local_simulacao, fg_color="#000000").grid(row=linha, column=0, padx=5, pady=2, sticky="w")

                                    ctk.CTkLabel(self.container_dados, text=str_parcela, fg_color="#000000").grid(row=linha, column=1, padx=3, pady=1, sticky="w")

                                    ctk.CTkLabel(self.container_dados, text=formatar_moeda(mensalidade_simulacao_avulsa), justify=ctk.LEFT, text_color="green", fg_color="#000000").grid(row=linha, column=2, padx=5, pady=2, sticky="e")

                                    ctk.CTkLabel(self.container_dados, text=data_para_exibicao(data_vencimento), fg_color="#000000").grid(row=linha, column=3, padx=5, pady=2, sticky="w")

                                    total_fatura += mensalidade_simulacao_avulsa

                                    linha += 1
                            else:
                                print('ERRO: Data do primeiro pagamento nula...')


            
            ctk.CTkLabel(
                self.container_dados, 
                text="TOTAL DA FATURA:", 
                font=ctk.CTkFont(weight="bold", size=14)
            ).grid(row=linha, column=0, columnspan=2, padx=5, pady=(20, 5), sticky="e")

            ctk.CTkLabel(
                self.container_dados, 
                text=formatar_moeda(total_fatura + total_assin), 
                font=ctk.CTkFont(weight="bold", size=14), 
                text_color="red" 
            ).grid(row=linha, column=2, padx=5, pady=(20, 5), sticky="e")
            
        if escolha:
            self.tabela_frame.configure(label_text=f"Detalhes do Cartão: {escolha} / {self.data_atual.year}")


        self.container_dados.grid_columnconfigure(0, weight=2)
        self.container_dados.grid_columnconfigure((1, 2, 3), weight=1)



