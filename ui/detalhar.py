"""
Módulo Detalhar (UI Listagens e Dashboards)

Este módulo é responsável por renderizar as tabelas dinâmicas (Grids) de listagem 
de dados (Receitas, Despesas, Cartões e Assinaturas). Ele também contém os componentes 
de Dashboard (Listar_desp_tabela e Listar_cat_grafico) que processam a lógica pesada de 
vencimentos e simulações para exibir resumos financeiros mensais e gráficos de pizza.
"""

# ---------------------------------- IMPORTAÇÃO - MÓDULOS LOCAIS ------------------------------------

# ----- FUNÇÕES DE AJUDA - (utils) -------
from utils.helper import(
    gerar_opcoes_meses, mysql_para_obj, formatar_moeda, data_para_exibicao, controle_data_parc_cc, controle_data_parc, centralizar_janela_responsiva, formata_cor, distribuir_parcelas_decimal
)
from utils.audio_helper import tocar_notificacao 

#------ IMPORTAÇÃO DE CLASSES TYPEDDICT - (typedDict.py) --------
from utils.typedDict import *


# ------------------------------ IMPORTAÇÃO - MÓDULOS BIBLIOTECAS ---------------------------------
#BILIO PADRÕES
from typing import List, Optional, Callable, Dict, Any
from datetime import datetime
from decimal import Decimal
from collections import defaultdict 

#BIBLIO VIA PIP
from dateutil.relativedelta import relativedelta
import customtkinter as ctk
from CTkToolTip import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ------------------------------------ CONFIGURAÇÃO INICIAL -------------------------------------------
ctk.set_appearance_mode('dark')

# =================================================================================
# --- LISTAGEM DE RECEITAS ---
# =================================================================================

class Listar_receitas(ctk.CTkFrame):
    """Componente de tabela (Grid) para exibir as Receitas e fornecer ações de Editar/Deletar."""

    def __init__(self,  parent: Any = None, user_id: Optional[int] = None, dados_receitas: Optional[List[Any]] = None, controle_dados: Optional[Callable] = None, callback_comandante_crud: Optional[Callable] = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.dados_receitas = dados_receitas
        self.controle_dados = controle_dados
        self.cdt_crud = callback_comandante_crud

         # --------------- Configuração da Frames/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.lista_frame = ctk.CTkScrollableFrame(self, label_text="Receitas Cadastradas")
        self.lista_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.lista_frame.grid_columnconfigure((0, 1, 3), weight=0) # Index, Valor e Data fixos
        self.lista_frame.grid_columnconfigure(2, weight=1) #Descriçao estica

        # Cabeçalho
        ctk.CTkLabel(self.lista_frame, text='#', font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text='Fonte', font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Valor", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Descrição", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Data Recebimento", font=ctk.CTkFont(weight="bold")).grid(row=0, column=4, padx=5, pady=5, sticky="w")

        self.listar()

    def listar(self, dados_receitas: Optional[List[Dict[str, Any]]] = None) -> None:
        """Renderiza as linhas da tabela limpando os dados anteriores."""
        for widget in self.lista_frame.winfo_children():
            if int(widget.grid_info().get("row", 0)) > 0:
                widget.destroy()
        
        if dados_receitas is None:
            dados_receitas = self.dados_receitas

        if dados_receitas:
            for i, dado in enumerate(dados_receitas, start=1):
                fonte = dado["fonte"]
                valor = dado.get('valor')
                descricao = dado.get('descricao')
                data = dado.get('data')

                ctk.CTkLabel(self.lista_frame, text=str(i), font=('Ariel', 14)).grid(row=i, column=0, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=str(fonte), font=('Ariel', 14)).grid(row=i, column=1, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=formatar_moeda(valor), text_color="#27ae60", font=('Ariel', 14)).grid(row=i, column=2, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=str(descricao), font=('Ariel', 14)).grid(row=i, column=3, padx=3, pady=1, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=data_para_exibicao(data), font=('Ariel', 14)).grid(row=i, column=4, padx=5, pady=2, sticky="e")

                btn_edit = ctk.CTkButton(self.lista_frame, text="📝", width=30, fg_color="transparent", hover_color="#34495e",
                                     command=lambda d=dado: self.confirmar_update(d, valor))
                btn_edit.grid(row=i, column=5, padx=2)
                CTkToolTip(btn_edit, message="Editar Registro")

                btn_del = ctk.CTkButton(self.lista_frame, text="X", width=30, fg_color="#c0392b", hover_color="#e74c3c",
                                    command=lambda dados=dado: self.confirmar_delete(dados))
                btn_del.grid(row=i, column=6, padx=5)
                CTkToolTip(btn_del, message="Excluir Registro", delay=0.5, alpha=0.9, bg_color="red")

        self.lista_frame.grid_columnconfigure((4, 5), weight=0)

    def confirmar_update(self, dict_dados: Dict[str, Any], valor: Any) -> None:
        """Injeta a receita selecionada no formulário lateral (via callback)."""
        if dict_dados:
            dict_dados['valor'] = valor
            if self.controle_dados:
                self.controle_dados(dict_dados)
        else:
            if self.controle_dados:
                self.controle_dados(None)

    def confirmar_delete(self, dados: Dict[str, Any]) -> None:
        """Abre a Toplevel Modal de confirmação antes de apagar do Banco."""
        popup = ctk.CTkToplevel(self)
        popup.title("Confirmação")
        centralizar_janela_responsiva(popup, tipo_janela='pequeno')
        popup.grab_set()
        popup.grid_columnconfigure((0, 1), weight=1)

        label = ctk.CTkLabel(popup, text="Tem certeza que deseja\nexcluir esta receita?", font=("Arial", 14))
        label.grid(row=0, column=0, columnspan=2, pady=20)

        btn_cancelar = ctk.CTkButton(popup, text="Cancelar", fg_color="gray", hover_color="#555555", command=popup.destroy)
        btn_cancelar.grid(row=1, column=0, padx=10, pady=10)

        btn_confirmar = ctk.CTkButton(popup, text="Sim, excluir", fg_color="#c0392b", hover_color="#e74c3c",
                                  command=lambda: self.executar_delete(dados, popup))
        btn_confirmar.grid(row=1, column=1, padx=10, pady=10)

    def executar_delete(self, dados: Dict[str, Any], popup: ctk.CTkToplevel) -> None:
        """Realiza o delete através do controlador (crud_app)."""
        id_rec = dados.get('id_receita')
        descricao = dados.get('descricao')

        if self.cdt_crud:
            sucesso = self.cdt_crud(deletar=id_rec)
            if sucesso:
                print(f"ID {id_rec} receita: '{descricao}'. Mandado pro espaço 🌌​")
                popup.destroy()
            else:
                print("Erro ao deletar")

# =================================================================================
# --- LISTAGEM DE DESPESAS ---
# =================================================================================

class Listar_despesas(ctk.CTkFrame):
    """Componente de tabela (Grid) global contendo todas as despesas avulsas e parceladas."""

    def __init__(self,  parent: Any = None, user_id: Optional[int] = None, dados_cartoes: Optional[List] = None, cb_comandante_crud: Optional[Callable] = None, dados_despesas: Optional[List] = None, controle_dados: Optional[Callable] = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.dados_cartoes = dados_cartoes
        self.cdt_crud = cb_comandante_crud
        self.controle_dados = controle_dados
        self.dados_despesas = dados_despesas

        # --------------- Configuração da Frames/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.lista_frame = ctk.CTkScrollableFrame(self, label_text="Despesas Cadastradas")
        self.lista_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.lista_frame.grid_columnconfigure((0, 1, 2, 3, 5, 6, 7, 8), weight=0) 
        self.lista_frame.grid_columnconfigure(4, weight=1) 

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

    def listar(self, dados_despesas: Optional[List[Dict[str, Any]]] = None) -> None:
        """Monta o grid iterando sobre os dados de despesas (cruzando os nomes dos cartões)."""
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

                ctk.CTkLabel(self.lista_frame, text=str(i), font=('Ariel', 14)).grid(row=i, column=0, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=str(local), font=('Ariel', 14)).grid(row=i, column=1, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=formatar_moeda(valor_total), text_color="#27ae60", font=('Ariel', 14)).grid(row=i, column=2, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=str(parcelas), font=('Ariel', 14)).grid(row=i, column=3, padx=3, pady=1, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=str(descricao), font=('Ariel', 14)).grid(row=i, column=4, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=str(categoria), font=('Ariel', 14)).grid(row=i, column=5, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=str(data_compra), font=('Ariel', 14)).grid(row=i, column=6, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=str(data_pp), font=('Ariel', 14)).grid(row=i, column=7, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=str(nome_card), font=('Ariel', 14)).grid(row=i, column=8, padx=5, pady=2, sticky="w")

                btn_edit = ctk.CTkButton(self.lista_frame, text="📝", width=30, fg_color="transparent", hover_color="#34495e",
                                     command=lambda dados=dado: self.confirmar_update(dados))
                btn_edit.grid(row=i, column=9, padx=2)
                CTkToolTip(btn_edit, message="Editar Registro")

                btn_del = ctk.CTkButton(self.lista_frame, text="X", width=30, fg_color="#c0392b", hover_color="#e74c3c",
                                    command=lambda dados=dado: self.confirmar_delete(dados))
                btn_del.grid(row=i, column=10, padx=5)
                CTkToolTip(btn_del, message="Excluir Registro", delay=0.5, alpha=0.9, bg_color="red")
                
    def confirmar_update(self, dados: Dict[str, Any]) -> None:
        if dados:
            if self.controle_dados: self.controle_dados(dados)
        else:
            if self.controle_dados: self.controle_dados(None)

    def confirmar_delete(self, dados: Dict[str, Any]) -> None:
        popup = ctk.CTkToplevel(self)
        popup.title("Confirmação")
        centralizar_janela_responsiva(popup, tipo_janela='pequeno')
        popup.grab_set()
        popup.grid_columnconfigure((0, 1), weight=1)

        label = ctk.CTkLabel(popup, text="Tem certeza que deseja\nexcluir está despesa?", font=("Arial", 14))
        label.grid(row=0, column=0, columnspan=2, pady=20)

        btn_cancelar = ctk.CTkButton(popup, text="Cancelar", fg_color="gray", hover_color="#555555", command=popup.destroy)
        btn_cancelar.grid(row=1, column=0, padx=10, pady=10)

        btn_confirmar = ctk.CTkButton(popup, text="Sim, excluir!", fg_color="#c0392b", hover_color="#e74c3c",
                                  command=lambda: self.executar_delete(dados, popup))
        btn_confirmar.grid(row=1, column=1, padx=10, pady=10)

    def executar_delete(self, dados: Dict[str, Any], popup: ctk.CTkToplevel) -> None:
        id_desp = dados.get('id_desp')
        local = dados.get('local')

        if self.cdt_crud:
            sucesso = self.cdt_crud(deletar=id_desp)
            if sucesso:
                print(f"ID: {id_desp} Local: '{local}'. Mandado pro espaço 🌌​")
                popup.destroy()
            else:
                print("Erro ao deletar")

# =================================================================================
# --- LISTAGEM DE CARTÕES DE CRÉDITO ---
# =================================================================================

class Listar_car_cred(ctk.CTkFrame):
    """Grid para visualizar e gerenciar os Cartões de Crédito cadastrados."""

    def __init__(self,  parent: Any = None, user_id: Optional[int] = None, dados_cartoes: Optional[List] = None, nomes_cards: Optional[List] = None, cb_comandante_crud: Optional[Callable] = None, controle_dados: Optional[Callable] = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.nomes_cards = nomes_cards
        self.controle_dados = controle_dados
        self.dados_cartoes = dados_cartoes
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
        ctk.CTkLabel(self.lista_frame, text="Dia Fechamento", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Dia Vencimento", font=ctk.CTkFont(weight="bold")).grid(row=0, column=4, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text='Bandeira', font=ctk.CTkFont(weight="bold")).grid(row=0, column=5, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text='Cor', font=ctk.CTkFont(weight="bold")).grid(row=0, column=6, padx=6, pady=5, sticky="w")

        self.listar()

    def listar(self, dados_cartoes: Optional[List[Dict[str, Any]]] = None) -> None:
        """Renderiza a listagem de propriedades dos cartões (Fechamento/Corte/Bandeira)."""
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
                bandeira = dado.get('bandeira')
                cor = formata_cor(cor=str(dado.get('cor')))

                ctk.CTkLabel(self.lista_frame, text=str(i), font=('Ariel', 14)).grid(row=i, column=0, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=str(nome), font=('Ariel', 14)).grid(row=i, column=1, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=formatar_moeda(limite), text_color="#27ae60", font=('Ariel', 14)).grid(row=i, column=2, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=str(dia_fec), font=('Ariel', 14)).grid(row=i, column=3, padx=3, pady=1, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=str(dia_venc), font=('Ariel', 14)).grid(row=i, column=4, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=str(bandeira), font=('Ariel', 14)).grid(row=i, column=5, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=str(cor), font=('Ariel', 14)).grid(row=i, column=6, padx=5, pady=2, sticky="w")

                btn_edit = ctk.CTkButton(self.lista_frame, text="📝", width=30, fg_color="transparent", hover_color="#34495e",
                                     command=lambda dados=dado: self.confirmar_update(dados))
                btn_edit.grid(row=i, column=7, padx=2)
                CTkToolTip(btn_edit, message="Editar Registro")

                btn_del = ctk.CTkButton(self.lista_frame, text="X", width=30, fg_color="#c0392b", hover_color="#e74c3c",
                                    command=lambda dados=dado: self.confirmar_delete(dados))
                btn_del.grid(row=i, column=8, padx=5)
                CTkToolTip(btn_del, message="Excluir Registro", delay=0.5, alpha=0.9, bg_color="red")

    def confirmar_update(self, dados: Dict[str, Any]) -> None:
        if dados:
            if self.controle_dados: self.controle_dados(dados)
        else:
            if self.controle_dados: self.controle_dados(None)

    def confirmar_delete(self, dados: Dict[str, Any]) -> None:
        popup = ctk.CTkToplevel(self)
        popup.title("Confirmação")
        centralizar_janela_responsiva(janela=popup, tipo_janela='pequeno')
        popup.grab_set()
        popup.grid_columnconfigure((0, 1), weight=1)

        label = ctk.CTkLabel(popup, text="Tem certeza que deseja\nexcluir este Cartão?", font=("Arial", 14))
        label.grid(row=0, column=0, columnspan=2, pady=20)

        btn_cancelar = ctk.CTkButton(popup, text="Cancelar", fg_color="gray", hover_color="#555555", command=popup.destroy)
        btn_cancelar.grid(row=1, column=0, padx=10, pady=10)

        btn_confirmar = ctk.CTkButton(popup, text="Sim, excluir!", fg_color="#c0392b", hover_color="#e74c3c",
                                  command=lambda: self.executar_delete(dados, popup))
        btn_confirmar.grid(row=1, column=1, padx=10, pady=10)

    def executar_delete(self, dados: Dict[str, Any], popup: ctk.CTkToplevel) -> None:
        id_card = dados.get('id_cartao')
        nome = dados.get('nome_cartao')

        if self.cdt_crud:
            sucesso = self.cdt_crud(deletar=id_card)
            if sucesso:
                print(f"ID: {id_card} None: '{nome}'. Mandado pro espaço 🌌​")
                popup.destroy()
            else:
                print("Erro ao deletar")

# =================================================================================
# --- LISTAGEM DE ASSINATURAS ---
# =================================================================================

class Listar_assinaturas(ctk.CTkFrame):
    """Grid para gestão de serviços recorrentes ininterruptos."""

    def __init__(self, parent: Any = None, user_id: Optional[int] = None, dados_cartoes: Optional[List] = None, dados_assinaturas: Optional[List] = None, controle_dados: Optional[Callable] = None, cb_comandante_crud: Optional[Callable] = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.dados_cartoes = dados_cartoes 
        self.dados_assinaturas = dados_assinaturas  
        self.controle_dados = controle_dados
        self.cdt_crud = cb_comandante_crud

        # --------------- Configuração da Frames/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.lista_frame = ctk.CTkScrollableFrame(self, label_text="Assinaturas Cadastradas")
        self.lista_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.lista_frame.grid_columnconfigure((0, 1, 2, 4, 5, 6, 7), weight=0) 
        self.lista_frame.grid_columnconfigure(3, weight=1) 

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

    def listar(self, dados_ass: Optional[List[Dict[str, Any]]] = None) -> None:
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
                data_pp = dado.get('data_pp')
                cat = dado.get('categoria')

                if self.dados_cartoes:
                    for cartao in self.dados_cartoes:
                        if cartao.get('id_cartao') == dado.get('id_cc'):
                            nome_card = cartao.get('nome_cartao')
                            
                if nome_card is None:
                    nome_card = "Boleto/Avulça"

                ctk.CTkLabel(self.lista_frame, text=str(i), font=('Ariel', 14)).grid(row=i, column=0, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=str(nome), font=('Ariel', 14)).grid(row=i, column=1, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=formatar_moeda(valor), text_color="#27ae60", font=('Ariel', 14)).grid(row=i, column=2, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=str(desc), font=('Ariel', 14)).grid(row=i, column=3, padx=3, pady=1, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=str(data_aq), font=('Ariel', 14)).grid(row=i, column=4, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=str(data_pp), font=('Ariel', 14)).grid(row=i, column=5, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=str(cat), font=('Ariel', 14)).grid(row=i, column=6, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=str(nome_card), font=('Ariel', 14)).grid(row=i, column=7, padx=5, pady=2, sticky="w")

                btn_edit = ctk.CTkButton(self.lista_frame, text="📝", width=30, fg_color="transparent", hover_color="#34495e",
                                     command=lambda dados=dado: self.confirmar_update(dados))
                btn_edit.grid(row=i, column=8, padx=2)
                CTkToolTip(btn_edit, message="Editar Registro")

                btn_del = ctk.CTkButton(self.lista_frame, text="X", width=30, fg_color="#c0392b", hover_color="#e74c3c",
                                    command=lambda dados=dado: self.confirmar_delete(dados))
                btn_del.grid(row=i, column=9, padx=5)
                CTkToolTip(btn_del, message="Excluir Registro", delay=0.5, alpha=0.9, bg_color="red")

    def confirmar_update(self, dados: Dict[str, Any]) -> None:
        if dados:
            if self.controle_dados: self.controle_dados(dados)
        else:
            if self.controle_dados: self.controle_dados(None)

    def confirmar_delete(self, dados: Dict[str, Any]) -> None:
        popup = ctk.CTkToplevel(self)
        popup.title("Confirmação")
        centralizar_janela_responsiva(popup, tipo_janela='pequeno')
        popup.grab_set()
        popup.grid_columnconfigure((0, 1), weight=1)

        label = ctk.CTkLabel(popup, text="Tem certeza que deseja\nexcluir esta assinatura?", font=("Arial", 14))
        label.grid(row=0, column=0, columnspan=2, pady=20)

        btn_cancelar = ctk.CTkButton(popup, text="Cancelar", fg_color="gray", hover_color="#555555", command=popup.destroy)
        btn_cancelar.grid(row=1, column=0, padx=10, pady=10)

        btn_confirmar = ctk.CTkButton(popup, text="Sim, excluir!", fg_color="#c0392b", hover_color="#e74c3c",
                                  command=lambda: self.executar_delete(dados, popup))
        btn_confirmar.grid(row=1, column=1, padx=10, pady=10)

    def executar_delete(self, dados: Dict[str, Any], popup: ctk.CTkToplevel) -> None:
        id_ass = dados.get('id_ass')
        nome = dados.get('nome')

        if self.cdt_crud:
            sucesso = self.cdt_crud(deletar=id_ass)
            if sucesso:
                print(f"ID: {id_ass} Assinatura: '{nome}'. Mandado pro espaço 🌌​")
                tocar_notificacao('dv_delete', True)
                popup.destroy()
            else:
                print("Erro ao deletar")


# =================================================================================
# --- DASHBOARD: TABELA DINÂMICA DE DESPESAS DO MÊS ---
# =================================================================================

class Listar_desp_tabela(ctk.CTkFrame):
    """
    Motor do Dashboard e da Simulação.
    Este componente avalia todas as despesas avulsas, assinaturas e parcelamentos 
    de cartão para determinar quais parcelas vão "cair" no mês atual (ou no mês 
    simulado). Ele renderiza apenas as faturas e boletos ativos para o período.
    """

    def __init__(self, parent: Any = None, id_user: Optional[int] = None, despesas_avulsas: Optional[List] = None, dados_cartoes: Optional[List] = None, assinaturas_avulsas: Optional[List] = None, dados_prontos: Optional[List] = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
    
        self.id_user = id_user
        self.despesas_avulsas = despesas_avulsas 
        self.dados_cartoes = dados_cartoes 
        self.assinaturas_avulsas = assinaturas_avulsas 
        self.dados_prontos = dados_prontos

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


    def renderizar(self, controle_mes: Optional[int] = None, escolha: Optional[str] = None, dados_simulacao: Optional[List[Dict[str, Any]]] = None) -> Decimal:
        """
        Processa as regras de datas do helper (controle_data_parc_cc) para desenhar 
        o extrato financeiro. Se dados_simulacao for passado (Modo Mock), os insere na 
        soma matemática sem afetar a integridade dos dados reais.
        """
        for widget in self.tabela_frame.winfo_children():
            widget.destroy()

        if controle_mes is None:
            controle_mes = int(datetime.now().month)

        despesas = self.despesas_avulsas or []
        assin = self.assinaturas_avulsas or []

        total_avulsas = Decimal('0.0')
        total_cards = Decimal('0.0')
        lista_faturas_resumo = []

        if self.dados_prontos: 
            for pacote in self.dados_prontos:
                info_cartao = pacote.get('info', {})
                nome_cartao = info_cartao.get('nome_cartao')
                id_cartao = info_cartao.get('id_cartao') 
                
                despesas_do_cartao = pacote.get('despesas', [])
                assin_card = pacote.get('assinaturas', [])
            
                total_deste_cartao = Decimal('0.0')
                data_vencimento_fatura = None

                if assin_card or despesas_do_cartao or dados_simulacao:
                    if assin_card:
                        for ass in assin_card:
                            dia_f = ass.get('dia_fechamento_cc')
                            dia_v = ass.get('dia_vencimento_cc')
                            data_aquisicao = ass.get('data_aquisicao')

                            resultado = controle_data_parc_cc(data_aquisicao, dia_f, dia_v, controle_mes=controle_mes)
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

                            resultado = controle_data_parc_cc(data_compra, fechamento, dia_venc, parcelas, controle_mes=controle_mes)
                            _, entra_na_fatura, controle_data = resultado

                            if entra_na_fatura:
                                valor_mensal = Decimal(str(desp.get('valor_total'))) / parcelas
                                total_deste_cartao += valor_mensal
                                data_vencimento_fatura = controle_data 

                    # ---------- Simulação Mock - Injetando despesa virtual na fatura ----------------------
                    mensalidade_simulacao_card  = Decimal('0.0')

                    if not data_vencimento_fatura:
                        dia_venc_base = info_cartao.get('vencimento_fatura')
                        if dia_venc_base:
                            ano_atual = datetime.now().year
                            data_vencimento_fatura = datetime(ano_atual, controle_mes, int(dia_venc_base)).date()

                    if dados_simulacao:
                        for _, dado in enumerate(dados_simulacao):
                            info_card = dado.get('info_cartao')
                            if info_card and isinstance(info_card, dict): 
                                data_compra_simulacao = dado.get('data_compra')
                                parcelas_simulacao = int(dado.get('parcelas', 1))

                                id_card = info_card.get('id_cartao')
                                venc_card_simulacao = info_card.get('vencimento')
                                fech_card_simulacao = info_card.get('fechamento')
                            
                                if str(id_card) == str(id_cartao): 
                                    resultado = controle_data_parc_cc(data_compra_simulacao, fech_card_simulacao, venc_card_simulacao, parcelas_simulacao, controle_mes=controle_mes)
                                    _, entra_na_fatura, controle_data = resultado

                                    if entra_na_fatura:
                                        data_vencimento_fatura = controle_data 
                                        mensalidade_simulacao_card += Decimal(str(dado.get('valor_total'))) / parcelas_simulacao

                    if (total_deste_cartao > Decimal('0.0')) or (mensalidade_simulacao_card > Decimal('0.0')):
                        lista_faturas_resumo.append({
                            'local': f"Fatura - {nome_cartao}",
                            'valor': (total_deste_cartao + mensalidade_simulacao_card),
                            'vencimento': data_vencimento_fatura
                        })

    
        # Desenha a tabela
        if despesas or lista_faturas_resumo or assin or dados_simulacao:
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

                        resultado = controle_data_parc(data_pp, dia_venc, total_parcelas=None, controle_mes=controle_mes )
                        str_sit, entra_no_mes, data_vencimento = resultado

                        if entra_no_mes:
                            total_ass_avulcas += Decimal(str(valor))
                            ctk.CTkLabel(self.tabela_frame, text=nome).grid(row=linha, column=0, padx=5, pady=2, sticky="w")
                            ctk.CTkLabel(self.tabela_frame, text=str_sit).grid(row=linha, column=1, padx=3, pady=1, sticky="w")
                            ctk.CTkLabel(self.tabela_frame, text=formatar_moeda(valor), justify=ctk.LEFT, text_color="red").grid(row=linha, column=2, padx=5, pady=2, sticky="e")
                            ctk.CTkLabel(self.tabela_frame, text=data_para_exibicao(data_vencimento)).grid(row=linha, column=3, padx=5, pady=2, sticky="w")
                            linha += 1

            if despesas:
                for _, dados in enumerate(despesas):
                    dados: Dados_despesas_db = dados

                    primeira_parc = mysql_para_obj(dados['data_pp'])
                    dia_venc = dados['dia_vencimento']
                
                    resultado_avulso = controle_data_parc(primeira_parc, dia_venc, dados.get('parcelas'), controle_mes=controle_mes)
                    str_parcela, control_parc, data_vencimento = resultado_avulso
                    dia_venc = int(primeira_parc.day) if primeira_parc else dia_venc

                    if data_vencimento:
                        data_fatura = data_vencimento
                    else:
                        data_fatura = datetime.now().replace(day=dia_venc)

                    if control_parc:
                        parcela_atual = int(str_parcela.split('/')[0])
                        valor_mensal = distribuir_parcelas_decimal(valor_total=dados['valor_total'], total_parcelas=dados["parcelas"])[parcela_atual - 1]
                    
                        ctk.CTkLabel(self.tabela_frame, text=dados.get('local')).grid(row=linha, column=0, padx=5, pady=2, sticky="w")
                        ctk.CTkLabel(self.tabela_frame, text=str_parcela).grid(row=linha, column=1, padx=3, pady=1, sticky="w")
                        ctk.CTkLabel(self.tabela_frame, text=formatar_moeda(valor_mensal), justify=ctk.LEFT, text_color="green").grid(row=linha, column=2, padx=5, pady=2, sticky="e")
                        ctk.CTkLabel(self.tabela_frame, text=data_para_exibicao(data_fatura)).grid(row=linha, column=3, padx=5, pady=2, sticky="w")

                        total_avulsas += valor_mensal
                        linha += 1
          
            if lista_faturas_resumo:
                for fatura in lista_faturas_resumo:
                    ctk.CTkLabel(self.tabela_frame, text=fatura['local']).grid(row=linha, column=0, padx=5, pady=2, sticky="w")
                    ctk.CTkLabel(self.tabela_frame, text="-").grid(row=linha, column=1, padx=3, pady=1, sticky="w") 
                    ctk.CTkLabel(self.tabela_frame, text=formatar_moeda(fatura['valor']), justify=ctk.LEFT, text_color="orange").grid(row=linha, column=2, padx=5, pady=2, sticky="e")
            
                    venc_str = data_para_exibicao(fatura['vencimento']) if fatura['vencimento'] else "N/A"
                    ctk.CTkLabel(self.tabela_frame, text=venc_str).grid(row=linha, column=3, padx=5, pady=2, sticky="w")

                    total_cards += fatura['valor']
                    linha += 1

            # -------------- SIMULAÇÃO MOCK - AVULSO -----------
            if dados_simulacao:
                for dado in dados_simulacao:
                    info_card = dado.get('info_cartao')

                    if info_card is None:
                        local_simulacao = dado.get('local')
                        data_compra_simulacao = dado.get('data_compra')
                        data_pp_simulacao = dado.get('prim_data_pag')
                        parcelas_simulacao = int(dado.get('parcelas', 1))

                        if data_pp_simulacao:
                            dia_venc_simulacao = data_pp_simulacao.day
                            resultado_avulso_sim = controle_data_parc(data_pp_simulacao, dia_venc_simulacao, parcelas_simulacao, controle_mes=controle_mes)
                            str_parcela, control_parc, data_vencimento = resultado_avulso_sim

                            data_fatura = data_vencimento if data_vencimento else datetime.now().replace(day=dia_venc_simulacao)

                            if control_parc:
                                mensalidade_simulacao_avulsa = Decimal(str(dado['valor_total'])) / parcelas_simulacao

                                ctk.CTkLabel(self.tabela_frame, text=str(local_simulacao)).grid(row=linha, column=0, padx=5, pady=2, sticky="w")
                                ctk.CTkLabel(self.tabela_frame, text=str(str_parcela)).grid(row=linha, column=1, padx=3, pady=1, sticky="w")
                                ctk.CTkLabel(self.tabela_frame, text=formatar_moeda(mensalidade_simulacao_avulsa), justify=ctk.LEFT, text_color="green").grid(row=linha, column=2, padx=5, pady=2, sticky="e")
                                ctk.CTkLabel(self.tabela_frame, text=data_para_exibicao(data_fatura)).grid(row=linha, column=3, padx=5, pady=2, sticky="w")

                                total_avulsas += mensalidade_simulacao_avulsa
                                linha += 1

            ctk.CTkLabel(self.tabela_frame, text="TOTAL DESPESAS:", font=ctk.CTkFont(weight="bold", size=14)
            ).grid(row=linha, column=0, columnspan=2, padx=5, pady=(20, 5), sticky="e")

            ctk.CTkLabel(self.tabela_frame, text=formatar_moeda((total_avulsas + total_cards + total_ass_avulcas)), 
                font=ctk.CTkFont(weight="bold", size=14), text_color="red" 
            ).grid(row=linha, column=2, padx=5, pady=(20, 5), sticky="e")

            self.tabela_frame.grid_columnconfigure(2, weight=1)
            
            tt_dividas = (total_avulsas + total_cards + total_ass_avulcas)
            
            if escolha:
                self.tabela_frame.configure(label_text=f"Detalhes do Despesas: {escolha}")

            return tt_dividas

        else:
            ctk.CTkLabel(self.tabela_frame, text="Nenhum pagamento previsto.").grid(row=0, column=0, padx=10, pady=10)
            self.tabela_frame.grid_columnconfigure(2, weight=1)
            return Decimal('0.0')

# =================================================================================
# --- DASHBOARD: GRÁFICO PIZZA (Matplotlib) ---
# =================================================================================

class Listar_cat_grafico(ctk.CTkFrame):
    """
    Motor Gráfico do Dashboard.
    Usa o Matplotlib para agregar o valor das parcelas do mês filtrado pelas 
    Categorias ('Saúde', 'Lazer', 'Essencial') e plota o gráfico interativo no Canvas.
    """

    def __init__(self, parent: Any = None, id_user: Optional[int] = None, despesas_avulsas: Optional[List] = None, dados_cartoes: Optional[List] = None, assinaturas_avulsas: Optional[List] = None, dados_prontos: Optional[List] = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.id_user = id_user
        self.despesas_avulsas = despesas_avulsas
        self.dados_cartoes = dados_cartoes
        self.assinaturas_avulsas = assinaturas_avulsas
        self.dados_prontos = dados_prontos

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        #FRAME GRÁFICO
        self.grafico_frame = ctk.CTkFrame(self)
        self.grafico_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.grafico_frame.grid_columnconfigure(0, weight=1)
        self.grafico_frame.grid_rowconfigure(0, weight=1)


    def renderizar(self, controle_mes: Optional[int] = None) -> None:
        """Executa a engine de agregação de categorias e redesenha o Matplotlib."""
        print(f"Renderizando gráfico")

        for widget in self.grafico_frame.winfo_children():
            widget.destroy()

        if controle_mes is None:
            controle_mes = datetime.now().month

        assin_avulsas = self.assinaturas_avulsas or []
        desp_avulsas = self.despesas_avulsas or []

        gastos_por_categoria = defaultdict(Decimal)
        total_previsto = Decimal('0.0')
    
        if self.dados_prontos:
            for pacote in self.dados_prontos:
                desp_cc = pacote.get('despesas', [])
                assin_card = pacote.get('assinaturas', [])
            
                if assin_card:
                    for ass in assin_card:
                        dia_f = ass.get('dia_fechamento_cc')
                        dia_v = ass.get('dia_vencimento_cc')
                        data_aquisicao = ass.get('data_aquisicao')

                        resultado = controle_data_parc_cc(data_aquisicao, dia_f, dia_v, controle_mes=controle_mes)
                        _, entra_na_fatura, _ = resultado

                        if entra_na_fatura:
                            valor = Decimal(str(ass.get('valor')))
                            categoria = ass.get('categoria', 'Outros') 
                            gastos_por_categoria[categoria] += valor
                            total_previsto += valor

                if desp_cc:
                    for desp in desp_cc:
                        data_compra = mysql_para_obj(desp.get('data_compra'))
                        dia_venc = desp.get('dia_vencimento')
                        fechamento = desp.get('dia_fechamento')
                        parcelas = desp.get('parcelas')

                        resultado = controle_data_parc_cc(data_compra, fechamento, dia_venc, parcelas, controle_mes=controle_mes)
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
        
                    resultado = controle_data_parc(primeira_parc, dia_venc , parcelas, controle_mes=controle_mes)
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
                    valor = Decimal(str(ass.get('valor')))

                    resultado = controle_data_parc(data_pp, dia_venc, controle_mes=controle_mes)
                    _, entra_no_mes, _ = resultado

                    if entra_no_mes:
                        total_previsto += valor
                        categoria = ass.get('categoria', 'Outros')
                        gastos_por_categoria[categoria] += valor
            
        if total_previsto == Decimal('0.0'):
            ctk.CTkLabel(self.grafico_frame, text="Nenhum gasto para este mês.").grid(row=0, column=0, padx=20, pady=(20,0))
            return

        # Prepara os dados para o Matplotlib
        categorias = list(gastos_por_categoria.keys())
        totais = list(gastos_por_categoria.values())

        # Criação do Gráfico
        fig, ax = plt.subplots(figsize=(5, 5), facecolor='#2b2b2b') # Cor de fundo igual ao CTk
        ax.pie(
            totais, 
            labels=categorias, 
            autopct='%1.1f%%', 
            startangle=90,
            textprops={'fontsize': 8, 'color': 'white'}
        )
        ax.axis('equal')
    
        ax.set_title(f"Distribuição de Gastos\nTotal: {formatar_moeda(total_previsto)}", color='white', fontsize=12, pad=25)
        fig.tight_layout()

        # Renderização no CustomTkinter
        canvas = FigureCanvasTkAgg(fig, master=self.grafico_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, sticky="nsew", pady=(15, 5), padx=10)
        canvas.draw()


# =================================================================================
# --- FATURA DETALHADA DO CARTÃO DE CRÉDITO ---
# =================================================================================

class Listar_faturas_cartao(ctk.CTkFrame):
    """
    Visão Microscópica de um Cartão.
    Filtra do Dicionário "dados_prontos" apenas os itens daquele ID específico
    e calcula as parcelas em aberto, renderizando o detalhamento da fatura.
    Suporta o Mock Engine para a tela de Simulação.
    """

    def __init__(self, parent: Any = None, id_user: Optional[int] = None, id_card: Optional[int] = None, nome_card: Optional[str] = None, dados_prontos: Optional[List[Dict[str, Any]]] = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.id_user = id_user
        self.id_card = id_card
        self.nome_card = nome_card
        self.dados_prontos = dados_prontos #LISTA DE DICIONÁRIOS

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

        self.tabela_frame = ctk.CTkScrollableFrame(self, label_text=f"Pagamentos Detalhados: [ ] - Mês: {self.mes_atual_str} / {self.data_atual.year}")
        self.tabela_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.container_dados = ctk.CTkFrame(self.tabela_frame, fg_color="transparent")
        self.container_dados.pack(fill="both", expand=True)


    def tabela_cartao(self, id_user: int, id_card: int, escolha: Optional[str] = None, controle_mes: Optional[int] = None, dados_simulacao: Optional[List[Dict[str, Any]]] = None) -> None: 
        """Recalcula e renderiza a listagem de despesas que compõem a fatura do cartão focado."""
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
                info_cartao = pacote.get('info', {})
                
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

                    resultado = controle_data_parc_cc(data_aquisicao, dia_f, dia_v, controle_mes=controle_mes )
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
                    item_desp: Pega_despesas_cartao_db = item_desp

                    data_compra = mysql_para_obj(item_desp.get('data_compra'))
                    fecha_fatura = item_desp.get('dia_fechamento')
                    dia_venc = item_desp.get('dia_vencimento')
                    parcelas = item_desp.get('parcelas')

                    resultado = controle_data_parc_cc(data_compra, fecha_fatura ,dia_venc, parcelas, controle_mes=controle_mes)
                    str_parc, control_parc, controle_data = resultado

                    if control_parc:
                        parcela_atual = int(str_parc.split('/')[0])
                        valor_mensal = distribuir_parcelas_decimal(valor_total=item_desp['valor_total'], total_parcelas=item_desp['parcelas'])[parcela_atual - 1]
                        total_fatura += valor_mensal

                        ctk.CTkLabel(self.container_dados, text=item_desp.get('local')).grid(row=linha, column=0, padx=5, pady=2, sticky="w")
                        ctk.CTkLabel(self.container_dados, text=str_parc).grid(row=linha, column=1, padx=3, pady=1, sticky="w")
                        ctk.CTkLabel(self.container_dados, text=formatar_moeda(valor_mensal),justify=ctk.LEFT, text_color="green").grid(row=linha, column=2, padx=5, pady=2, sticky="e")
                        ctk.CTkLabel(self.container_dados, text=data_para_exibicao(controle_data)).grid(row=linha, column=3, padx=5, pady=2, sticky="w")
                        linha += 1


            if dados_simulacao:
                for dado in dados_simulacao:
                    info_card = dado.get('info_cartao')

                    if info_card and isinstance(info_card, dict):
                        if str(info_card['id_cartao']) == str(id_card):
                            local_simulacao = dado['local']
                            data_compra_simulacao = dado.get('data_compra')
                            parcelas_simulacao = int(dado.get('parcelas', 1))

                            venc_card_simulacao = info_card['vencimento']
                            fech_card_simulacao = info_card['fechamento']

                            if venc_card_simulacao:
                                resultado = controle_data_parc_cc(data_compra_simulacao, fech_card_simulacao, venc_card_simulacao, parcelas_simulacao, controle_mes=controle_mes)
                                str_parcela, control_parc, data_vencimento = resultado

                                if control_parc:
                                    mensalidade_simulacao_avulsa = Decimal(str(dado['valor_total'])) / parcelas_simulacao

                                    ctk.CTkLabel(self.container_dados, text=local_simulacao, fg_color="#000000").grid(row=linha, column=0, padx=5, pady=2, sticky="w")
                                    ctk.CTkLabel(self.container_dados, text=str_parcela, fg_color="#000000").grid(row=linha, column=1, padx=3, pady=1, sticky="w")
                                    ctk.CTkLabel(self.container_dados, text=formatar_moeda(mensalidade_simulacao_avulsa), justify=ctk.LEFT, text_color="green", fg_color="#000000").grid(row=linha, column=2, padx=5, pady=2, sticky="e")
                                    ctk.CTkLabel(self.container_dados, text=data_para_exibicao(data_vencimento), fg_color="#000000").grid(row=linha, column=3, padx=5, pady=2, sticky="w")

                                    total_fatura += mensalidade_simulacao_avulsa
                                    linha += 1
            
            ctk.CTkLabel(self.container_dados, text="TOTAL DA FATURA:", font=ctk.CTkFont(weight="bold", size=14)
            ).grid(row=linha, column=0, columnspan=2, padx=5, pady=(20, 5), sticky="e")

            ctk.CTkLabel(self.container_dados, text=formatar_moeda(total_fatura + total_assin), font=ctk.CTkFont(weight="bold", size=14), text_color="red" 
            ).grid(row=linha, column=2, padx=5, pady=(20, 5), sticky="e")
            
        if escolha:
            self.tabela_frame.configure(label_text=f"Detalhes do Cartão: {escolha} / {self.data_atual.year}")

        self.container_dados.grid_columnconfigure(0, weight=2)
        self.container_dados.grid_columnconfigure((1, 2, 3), weight=1)