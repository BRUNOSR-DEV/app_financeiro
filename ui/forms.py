"""
Módulo de Formulários (UI Cadastros)

Este módulo contém as classes de interface gráfica (Frames) responsáveis pela coleta, 
validação prévia e empacotamento dos dados inseridos pelo usuário. Ele se comunica 
com o módulo Controlador (crud_app.py) através de callbacks para efetivar as transações no banco.
"""

# ---------------------------------- IMPORTAÇÃO - MÓDULOS LOCAIS ------------------------------------

# ----- BANCO DE DADOS (models) ------
from models.entidades import Usuario, Receita, Cartao_credito, Despesa, Assinatura

# ----- FUNÇÕES DE AJUDA - (UTILS) -------
from utils.helper import(data_para_mysql, mysql_para_obj, formata_cor)
from utils.segurança import SegurancaService
from utils.audio_helper import tocar_notificacao 

#------ IMPORTAÇÃO DE CLASSES TYPEDDICT - (typedDict.py) --------
from utils.typedDict import(Despesa_simulacao)

# ------------------------------ IMPORTAÇÃO - MÓDULOS BIBLIOTECAS ---------------------------------
#BILIO PADRÕES
from datetime import datetime
from decimal import Decimal
from typing import Any, Callable, Dict, List, Optional

#BIBLIO VIA PIP
from tkcalendar import DateEntry

# --------------------------------- CONFIGURAÇÃO INICIAL ---------------------------------------
import customtkinter as ctk
ctk.set_appearance_mode('dark')

# =================================================================================
# --- CADASTRO DE USUÁRIOS ---
# =================================================================================

class Cadastrar_usuario(ctk.CTkFrame):
    """
    Interface de registro para novos usuários. Coleta credenciais, verifica senhas 
    e envia os dados para inserção no banco de dados.
    """

    def __init__(self, parent: Any = None, cb_comandante_crud: Optional[Callable] = None, nome_users: Optional[List[str]] = None, cb_fechar: Optional[Callable] = None, cb_vcmd_num: Optional[Callable] = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.cdt_crud = cb_comandante_crud
        self.fechar = cb_fechar
        self.nome_users = nome_users or []
        self.vcmd_num = cb_vcmd_num

        # --------------- Configuração da janela/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1)
        
        # --- TÍTULO DO FORMULÁRIO ---
        ctk.CTkLabel(self, text="Crie sua nova conta", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=(20, 10))

        # --- NOME COMPLETO ---
        ctk.CTkLabel(self, text="Nome e Sobrenome*", font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, padx=20, sticky="w")
        self.nome_completo = ctk.CTkEntry(self, placeholder_text="Maria Silva")
        self.nome_completo.grid(row=2, column=0, padx=20, pady=(2, 10), sticky="ew")

        # --- USUÁRIO ---
        ctk.CTkLabel(self, text="Nome de Usuário*", font=ctk.CTkFont(size=12, weight="bold")).grid(row=3, column=0, padx=20, sticky="w")
        self.novo_usuario = ctk.CTkEntry(self, placeholder_text="maria_silva123")
        self.novo_usuario.grid(row=4, column=0, padx=20, pady=(2, 10), sticky="ew")

        # --- SENHA ---
        ctk.CTkLabel(self, text="Senha de Acesso*", font=ctk.CTkFont(size=12, weight="bold")).grid(row=5, column=0, padx=20, sticky="w")
        self.nova_senha = ctk.CTkEntry(self, placeholder_text="Mínimo 6 caracteres", show="*")
        self.nova_senha.grid(row=6, column=0, padx=20, pady=(2, 10), sticky="ew")

        # --- REPETIR SENHA ---
        ctk.CTkLabel(self, text="Confirmar Senha*", font=ctk.CTkFont(size=12, weight="bold")).grid(row=7, column=0, padx=20, sticky="w")
        self.rep_nova_senha = ctk.CTkEntry(self, placeholder_text="Repita a Senha", show="*")
        self.rep_nova_senha.grid(row=8, column=0, padx=20, pady=(2, 10), sticky="ew")

        # --- EMAIL ---
        ctk.CTkLabel(self, text="Melhor E-mail*", font=ctk.CTkFont(size=12, weight="bold")).grid(row=9, column=0, padx=20, sticky="w")
        self.email = ctk.CTkEntry(self, placeholder_text="maria@silva123")
        self.email.grid(row=10, column=0, padx=20, pady=(2, 10), sticky="ew")

        # --- TELEFONE ---
        ctk.CTkLabel(self, text="Telefone/WhatsApp", font=ctk.CTkFont(size=12, weight="bold")).grid(row=11, column=0, padx=20, sticky="w")
        self.telefone = ctk.CTkEntry(self, placeholder_text="11 93858:2525")
        self.telefone.grid(row=12, column=0, padx=20, pady=(2, 10), sticky="ew")

        # --- SALÁRIO ---
        ctk.CTkLabel(self, text="Salário Mensal Fixo*", font=ctk.CTkFont(size=12, weight="bold")).grid(row=13, column=0, padx=20, sticky="w")
        self.sal_fixo = ctk.CTkEntry(self, placeholder_text="2500.00", validate='key', validatecommand= self.vcmd_num)
        self.sal_fixo.grid(row=14, column=0, padx=20, pady=(2, 15), sticky="ew")

        # --- BOTÃO ---
        self.botao_registrar = ctk.CTkButton(self, text="Confirmar Registro", font=ctk.CTkFont(weight="bold"), command=self.processar_registro)
        self.botao_registrar.grid(row=15, column=0, padx=20, pady=10, sticky="ew")

        # --- STATUS ---
        self.status_label = ctk.CTkLabel(self, text="", text_color="red")
        self.status_label.grid(row=16, column=0, pady=5)


    def processar_registro(self) -> None:
        """Coleta, valida os campos e envia a entidade Usuario para o Controlador."""

        nome_comp = self.nome_completo.get().strip()
        nome_user = self.novo_usuario.get().strip()
        senha_um = self.nova_senha.get().strip()
        senha_dois = self.rep_nova_senha.get().strip()
        email = self.email.get().strip()
        telefone = self.telefone.get().strip()
        sal_fixo = self.sal_fixo.get().strip()

        if not nome_user or not senha_um or not senha_dois or not sal_fixo or not email:
            self.status_label.configure(text='Por favor, preencha todos os campos com (*).', text_color='red')
            tocar_notificacao("dv_erro", True)
            self.update_idletasks()
            self.after(3000, lambda: self.status_label.configure(text='')) 
            return

        if nome_user in self.nome_users:
            self.status_label.configure(text='Nome de usuário já utilizado, tente outro!', text_color='red')
            self.update_idletasks()
            self.after(3000, lambda: self.status_label.configure(text=''))
            return

        if senha_um == senha_dois:    
            senha_protegida = SegurancaService.criptografar_senha(senha_um)
            new_user= Usuario(nome_completo=nome_comp, nome_user=nome_user, senha=senha_protegida, email=email, telefone=telefone, sal_fixo=float(sal_fixo))

            sucesso = self.cdt_crud(inserir=new_user)

            if sucesso:
                self.status_label.configure(text='Os dados foram inseridos com sucesso!', text_color='green')
                self.update_idletasks()
                self.after(3000, lambda: self.status_label.configure(text='')) 
                self.status_label.configure(text=f'Usuário: {nome_user} Já pode fazer login no sistema! ', text_color='blue')
                self.update_idletasks()
                self.after(3000, lambda: self.status_label.configure(text=''))

                import time
                time.sleep(0.5)
                if self.fechar:
                    self.fechar()
            else:
                self.status_label.configure(text='Não foi possível registrar, contate o adm do sistema...', text_color='red')
                self.update_idletasks()
                self.after(3000, lambda: self.status_label.configure(text='')) 
        else:
            self.status_label.configure(text='As senhas não correspondem!', text_color='red')
            self.update_idletasks()
            self.after(3000, lambda: self.status_label.configure(text='')) 

# =================================================================================
# --- CADASTRO DE RECEITAS ---
# =================================================================================

class Cadastrar_receita(ctk.CTkFrame):
    """Formulário para lançamento de Receitas (rendas variáveis ou extras)."""

    def __init__(self, parent: Any = None, user_id: Optional[int] = None, callback_comandante_crud: Optional[Callable] = None, cb_vcmd_num: Optional[Callable] = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.cdt_crud = callback_comandante_crud
        self.vcmd_num = cb_vcmd_num

        # ---------------- Gerencimento de self ---------------------
        self.data_atual = datetime.now().date()
        self.sentinela = self.data_atual.replace(day=1, month=1, year=2099)

        # --------------- Configuração da janela/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1)

        # ----- TÍTULO DO FORMULÁRIO -------
        ctk.CTkLabel(self, text="Cadastre Seus Ganhos", font=("Arial", 18, "bold")).grid(row=0, column=0, pady=10)

        # -------- FONTE ----------
        ctk.CTkLabel(self, text="Origim do Ganho*", font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, padx=20, sticky="w")
        self.fonte = ctk.CTkEntry(self, placeholder_text="Tigrinho")
        self.fonte.grid(row=2, column=0, padx=20, pady=(2,10), sticky="ew")

        # -------- VALOR GANHO ----------
        ctk.CTkLabel(self, text="Valor Ganho*", font=ctk.CTkFont(size=12, weight="bold")).grid(row=3, column=0, padx=20, sticky="w")
        self.valor = ctk.CTkEntry(self, placeholder_text="300,00", validate='key', validatecommand= self.vcmd_num)
        self.valor.grid(row=4, column=0, padx=20, pady=(2,10), sticky="ew")

        # -------- DESCRIÇÃO ----------- 
        ctk.CTkLabel(self, text="Descrição", font=ctk.CTkFont(size=12, weight="bold")).grid(row=5, column=0, padx=20, sticky="w")
        self.descricao = ctk.CTkEntry(self, placeholder_text="Ganho nas apostas ninja")
        self.descricao.grid(row=6, column=0, padx=20, pady=(2,10), sticky="ew")

        # --------- DATA DO GANHO ----------
        self.label_data_compra = ctk.CTkLabel(self, text="Data do Ganho*", font=ctk.CTkFont(size=12, weight="bold")).grid(row=7, column=0, padx=20, pady=(2,10)) 
        self.data_recebimento = DateEntry(self, width=12, background='darkblue',
                            foreground='white', borderwidth=2, day=1, month=1, year=2099, 
                            locale='pt_BR', date_pattern='dd/mm/yyyy')
        self.data_recebimento.grid(row=8, column=0, padx=10, pady=(2,10))

        # --------- BOTÃO ------------
        self.botao_salvar = ctk.CTkButton(self, text="Salvar Dados", command=self.salvar_dados)
        self.botao_salvar.grid(row=9, column=0, padx=20, pady=10, sticky="ew")

        # ---------- STATUS ------------
        self.status_label = ctk.CTkLabel(self, text="", text_color="red")
        self.status_label.grid(row=10, column=0, pady=5)


    def salvar_dados(self, id_rec: Optional[int] = None, atualizar: bool = False) -> None:
        """Valida e envia a nova receita (ou a atualização) para o controlador CRUD."""

        fonte = self.fonte.get().strip()
        valor = self.valor.get().strip()
        descricao = self.descricao.get().strip()
        data_obj = self.data_recebimento.get_date()

        data_mysql = data_para_mysql(data_obj)
        
        try:
            valor_dec = Decimal(str(valor.replace(',', '.')))
        except ValueError:
            print('Valor precisa ser um número valido, decimal!')
            tocar_notificacao("erro")
            self.after(2000, lambda: self.status_label.configure(text=''))
            return

        if not fonte or not valor or not descricao or not data_obj:
            self.status_label.configure(text='Por favor, preencha todos os campos com (*)', text_color='red')
            tocar_notificacao("erro")
            self.update_idletasks()
            self.after(2000, lambda: self.status_label.configure(text=''))
            return
        
        obj_receita = Receita(fonte=fonte, valor=valor_dec, descricao=descricao, data=data_mysql) # type: ignore
        
        if not atualizar:
            sucesso = self.cdt_crud(inserir=obj_receita)
            msg_ok = "INSERIDOS"
            msg_falha = "Não foi possível SALVAR os dados, contate o adm do sistema...'"
        else: 
            obj_receita.id_receita = id_rec
            sucesso = self.cdt_crud(atualizar=obj_receita)
            msg_ok = "ATUALIZADOS"
            msg_falha = "Não foi possível ATUALIZAR os dados, contate o adm do sistema..."

        if sucesso:
            self.status_label.configure(text=f'Os dados foram {msg_ok} com sucesso!', text_color='green')
            self.update_idletasks()
            self.after(2000, lambda: self.status_label.configure(text=''))

            if atualizar:
                self.controla_campos(None)
        else:
            self.status_label.configure(text=f'{msg_falha}', text_color='red')
            self.update_idletasks()
            self.after(2000, lambda: self.status_label.configure(text=''))


    def controla_campos(self, dados: Optional[Dict[str, Any]] = None) -> None:
        """Preenche o formulário com dados de uma receita selecionada para edição."""

        self.limpa_campos()

        if dados:
            id_rec = dados.get('id_receita')
            data_obj = mysql_para_obj(dados.get('data'))

            self.fonte.insert(0, dados['fonte'])
            self.valor.insert(0, str(dados.get('valor', '')))
            self.descricao.insert(0, dados.get('descricao', ''))
            
            if data_obj:
                self.data_recebimento.set_date(data_obj)

            self.botao_salvar.configure(text='Atualizar', fg_color="orange", command=lambda: self.salvar_dados(id_rec, atualizar=True))
        else:
            self.botao_salvar.configure(
            text="Salvar Dados", 
            fg_color=["#3B8ED0", "#1F6AA5"],
            command=self.salvar_dados 
        )

    def limpa_campos(self) -> None:
        """Reseta todos os inputs do formulário."""

        self.valor.delete(0, ctk.END)
        self.descricao.delete(0, ctk.END)
        self.fonte.delete(0, ctk.END)
        self.data_recebimento.set_date(self.sentinela)

# =================================================================================
# --- CADASTRO DE DESPESAS ---
# =================================================================================

class Cadastrar_despesa(ctk.CTkFrame):
    """
    Formulário para lançamento de despesas. 
    Capaz de diferenciar despesas avulsas (direto da renda) e despesas de cartão.
    Suporta injeção de dados no modo Simulação (Mock DB).
    """

    def __init__(self, parent: Any = None, user_id: Optional[int] = None, dados_cartoes: Optional[List[Dict[str, Any]]] = None, cb_comandante_crud: Optional[Callable] = None, simulacao: bool = False, dados_select: Optional[List[Dict[str, Any]]] = None, controle_dados: Optional[Callable] = None, cb_vcmd_num: Optional[Callable] = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.dados_cartoes = dados_cartoes or []
        self.cdt_crud = cb_comandante_crud
        self.vcmd_num = cb_vcmd_num

        self.dados_select = dados_select
        self.simulacao = simulacao
        self.controle_dados = controle_dados 

        # ---------------- Gerencimento de self ---------------------
        self.nomes_cartoes = [c.get('nome_cartao') for c in self.dados_cartoes] if self.dados_cartoes else []
        self.data_atual = datetime.now().date()
        self.sentinela = (self.data_atual.replace(day=1, month=1, year=2099))

        # --------------- Configuração da janela/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1)

        # ------- TÍTULO DO FORMULÁRIO --------
        ctk.CTkLabel(self, text="Cadastre Suas Despesas", font=("Arial", 18, "bold")).grid(row=0, column=0, pady=10)

        # ----- LOCAL DA COMPRA ------
        ctk.CTkLabel(self, text="Local da Compra*", font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, padx=20, sticky="w")
        self.local = ctk.CTkEntry(self, placeholder_text="Casas Bahia")
        self.local.grid(row=2, column=0, padx=20, pady=(2, 10), sticky="ew")

        # ----- TOTAL DA COMPRA ------
        ctk.CTkLabel(self, text="Total da Compra*", font=ctk.CTkFont(size=12, weight="bold")).grid(row=3, column=0, padx=20, sticky="w")
        self.valor_total = ctk.CTkEntry(self, placeholder_text="1000", validate='key', validatecommand= self.vcmd_num)
        self.valor_total.grid(row=4, column=0, padx=20, pady=(2, 10), sticky="ew")

        # ------ PARCELAS ------
        parcelas_opcoes = [str(i) for i in range(1, 13)]
        ctk.CTkLabel(self, text="N° Parcelas*", font=ctk.CTkFont(size=12, weight="bold")).grid(row=5, column=0, padx=20, sticky="w")
        self.menu_parcelas = ctk.CTkOptionMenu(self, values=parcelas_opcoes)
        self.menu_parcelas.grid(row=6, column=0, padx=20, pady=(2, 10), sticky="ew")

        # ----- DESCRIÇÃO DA COMPRA -------
        ctk.CTkLabel(self, text="Descrição", font=ctk.CTkFont(size=12, weight="bold")).grid(row=7, column=0, padx=20, sticky="w")
        self.descricao = ctk.CTkEntry(self, placeholder_text="Celular Novo")
        self.descricao.grid(row=8, column=0, padx=20, pady=(2, 10), sticky="ew")

        # ------ CATEGORIA ------
        categorias = ['Não Selecionado', 'Essencial', 'Lazer', 'Hobby', 'Vestimenta/Acessórios','Eletrônicos', 'Evolução Pessoal', 'Saúde', 'Empréstimo', 'Reforma e Construção', 'Outros']
        ctk.CTkLabel(self, text="Categoria*", font=ctk.CTkFont(size=12, weight="bold")).grid(row=9, column=0, padx=20, sticky="w")
        self.categoria = ctk.CTkOptionMenu(self, values=categorias)
        self.categoria.grid(row=10, column=0, padx=20, pady=(2, 10), sticky="ew")
  
        # ------- DATA DA COMPRA --------
        self.label_data_compra = ctk.CTkLabel(self, text="Data da Compra*", font=ctk.CTkFont(size=12, weight="bold"))
        self.label_data_compra.grid(row=11, column=0)
        self.campo_data_compra = DateEntry(self, width=12, background='darkblue',
                            foreground='white', borderwidth=2, year=2026, 
                            locale='pt_BR', date_pattern='dd/mm/yyyy')
        self.campo_data_compra.grid(row=12, column=0, padx=(2, 10), pady=10)

        # ---- DATA PRIMEIRO PAGAMENTO - SE NÃO FOR NO CARTÃO -----
        self.label_primeira_dc = ctk.CTkLabel(self, text="Data do Primeiro Pagamento: \n(obs. Não preencher se a compra for no Cartão)", font=ctk.CTkFont(size=12, weight="bold"))
        self.label_primeira_dc.grid(row=13, column=0)
        self.campo_primeira_dc = DateEntry(self, width=12, background='darkblue',
                            foreground='white', borderwidth=2, day=1, month=1, year=2099, 
                            locale='pt_BR', date_pattern='dd/mm/yyyy')
        self.campo_primeira_dc.grid(row=14, column=0, padx=(2, 10), pady=10)
        
        # ---- MENU CARTÕES DE CRÉDITO ----
        if self.nomes_cartoes:
            campo_cartoes = ["Cartão de Cobrança - Sem Cartão"] + self.nomes_cartoes
            self.car_cred = ctk.CTkOptionMenu(self, values=campo_cartoes)
            self.car_cred.grid(row=15, column=0, padx=20, pady=(2, 10), sticky="ew")
            self.car_cred.set("Cartão de Cobrança - Sem Cartão")
        else:
            self.car_cred = ctk.CTkOptionMenu(self, values=[' ', ' ',])
            self.car_cred.grid(row=15, column=0, padx=20, pady=(2, 10), sticky="ew")
            self.car_cred.set("Cadastre Seus Cartões Na Área Destinada")

        # ----- BOTÃO SALVAR E ATUALIZAR -----
        if not self.simulacao:
            self.botao_salvar = ctk.CTkButton(self, text="Salvar Dados", command=self.salvar_dados)
            self.botao_salvar.grid(row=16, column=0, padx=20, pady=(2, 10), sticky="ew")
        else:
            self.botao_salvar = ctk.CTkButton(self, text="Simular despesa", command=lambda: self.salvar_dados(simulacao=True, dados_select=self.dados_select))
            self.botao_salvar.grid(row=16, column=0, padx=20, pady=(2, 10), sticky="ew")

        # ------ STATUS ------
        self.status_label = ctk.CTkLabel(self, text="", text_color="red")
        self.status_label.grid(row=17, column=0, pady=5)


    def salvar_dados(self, id_desp: Optional[int] = None, atualizar: bool = False, simulacao: bool = False, dados_select: Optional[List[Dict[str, Any]]] = None) -> None:
        """Coleta, valida e orquestra a injeção da despesa (real ou mockada)."""

        dia_venc = None
        verifica_pri_dc = False
        id_card = None

        local = self.local.get().strip()
        valor_total_str = self.valor_total.get().strip()
        menu_parcelas_str = self.menu_parcelas.get()
        descricao = self.descricao.get().strip()
        categoria = self.categoria.get()
        self.dc_select = self.campo_data_compra.get_date()
        self.prim_dc_select = self.campo_primeira_dc.get_date()

        prim_dc_select_mysql = None
        self.sentinela = self.data_atual.replace(day=1, month=1, year=2099)

        if self.prim_dc_select != self.sentinela:
            dia_venc = self.prim_dc_select.day
            verifica_pri_dc = True
            prim_dc_select_mysql = data_para_mysql(self.prim_dc_select)

        car_cred = self.car_cred.get()
        dc_select_mysql = data_para_mysql(self.dc_select)
        
        if not local or not valor_total_str or categoria == "Categoria" or menu_parcelas_str == "N° Parcelas":
            self.status_label.configure(text='Preencha Local, Valor Total, Categoria,\n N° Parcelas e Data da compra', text_color='red')
            tocar_notificacao('erro')
            self.after(3000, lambda: self.status_label.configure(text=''))
            return
    
        try:
            parcelas = int(menu_parcelas_str)
            valor_total = float(valor_total_str.replace(",", "."))
        except ValueError:
            self.status_label.configure(text='Valor Total ou Parcelas devem ser \nnúmeros válidos!', text_color='red')
            tocar_notificacao('erro')
            self.after(3000, lambda: self.status_label.configure(text=''))
            return
        
        tem_cartao = car_cred != "Cartão de Cobrança - Sem Cartão" and car_cred != "Cadastre Seus Cartões Na Área Destinada"

        if self.dados_cartoes:
            for card in self.dados_cartoes:
                if card['nome_cartao'] == car_cred:
                    id_card = card['id_cartao']

        if not tem_cartao and not verifica_pri_dc:
            self.status_label.configure(text='Informe um Cartão OU Data do \nprimeiro pagamento', text_color='red')
            tocar_notificacao('erro')
            self.after(3000, lambda: self.status_label.configure(text=''))
            return 

        verifica = tem_cartao is True and verifica_pri_dc is True

        if verifica:
            self.campo_primeira_dc.set_date(self.sentinela)
            import time
            time.sleep(0.8)

            prim_dc_select_mysql = None
            dia_venc = None

            self.status_label.configure(text='Como foi informado um Cartão, a Data \nprimeiro pagamento será desconsiderada', text_color='blue')
            self.update_idletasks()
            self.after(4000, lambda: self.status_label.configure(text=''))

        #----------------- SIMULAÇÃO (MOCK DB) ---------------------------
        if simulacao and dados_select is not None:
            dict_dados: Despesa_simulacao = {
                "local": local,
                "valor_total": valor_total,
                "parcelas": int(menu_parcelas_str),
                "descricao": descricao,
                "categoria": categoria,
                "data_compra": self.dc_select, # type: ignore
                "prim_data_pag": self.prim_dc_select, # type: ignore
                "nome_cartao": car_cred,
                "info_cartao": None,
            }  
            dados_select.append(dict_dados) # type: ignore

            if self.controle_dados:
                self.controle_dados(dados=dados_select)

                self.limpa_campos()
                return
        # -------------- SIMULAÇÃO END ---------------

        obj_despesa = Despesa(local=local, valor_total=valor_total, parcelas=parcelas, descricao=descricao, categoria=categoria, data_compra=dc_select_mysql, data_pp=prim_dc_select_mysql, dia_venc=dia_venc, id_cc=id_card) # type: ignore

        if not atualizar:
            sucesso = self.cdt_crud(inserir=obj_despesa) if self.cdt_crud else False
            msg_ok = 'INSERIDOS'
            msg_erro = "SALVAR"
        else: 
            obj_despesa.id_desp = id_desp
            sucesso = self.cdt_crud(atualizar=obj_despesa) if self.cdt_crud else False
            msg_ok = 'ATUALIZADOS'
            msg_erro = "ATUALIZAR"

        if sucesso:
            self.status_label.configure(text=f'Os dados foram {msg_ok} com sucesso!', text_color='green')
            self.update_idletasks()

            if atualizar:
                self.controla_campos(None)
            
            self.after(3000, lambda: self.status_label.configure(text=''))
        else:
            self.status_label.configure(text=f'Não foi possível {msg_erro} os dados, contate o adm do sistema...', text_color='red')
            self.update_idletasks()
            self.after(3000, lambda: self.status_label.configure(text=''))


    def controla_campos(self, dados: Optional[Dict[str, Any]] = None) -> None:
        """Preenche o form para update com base em registro pré-selecionado na UI."""

        self.limpa_campos()
        
        if dados:
            id_desp = dados.get('id_desp')
            nome_card = "Cartão de Cobrança - Sem Cartão"

            if self.dados_cartoes:
                for cartao in self.dados_cartoes:
                    if cartao.get('id_cartao') == dados.get('id_cc'):
                        nome_card = cartao.get('nome_cartao', nome_card)

            self.local.insert(0, str(dados.get('local', '')))
            self.valor_total.insert(0, str(dados.get('valor_total', '')))
            self.descricao.insert(0, str(dados.get('descricao', '')))

            self.menu_parcelas.set(str(dados.get('parcelas', 'N° Parcelas')))
            self.categoria.set(str(dados.get('categoria', 'Categoria')))
            self.car_cred.set(str(nome_card))

            data_compra_obj = mysql_para_obj(dados.get('data_compra'))
            data_pp = dados.get('data_pp')

            if data_pp is None:
                data_pp_obj = self.sentinela
            else:
                data_pp_obj = mysql_para_obj(data_pp)

            if data_compra_obj:
                self.campo_data_compra.set_date(data_compra_obj)
            if data_pp_obj:
                self.campo_primeira_dc.set_date(data_pp_obj)

            self.botao_salvar.configure(text='Atualizar Assinatura', fg_color="orange", command=lambda: self.salvar_dados(id_desp, atualizar=True))
        else:
            self.botao_salvar.configure(
            text="Confirmar Assinatura" if self.simulacao else "Salvar Dados", 
            fg_color=["#3B8ED0", "#1F6AA5"], 
            command=self.salvar_dados 
        )

    def limpa_campos(self) -> None:
        """Reseta todos os inputs da tela de despesas para o default."""

        self.local.delete(0, ctk.END)
        self.valor_total.delete(0, ctk.END)
        self.descricao.delete(0, ctk.END)

        self.menu_parcelas.set("N° Parcelas")
        self.categoria.set("Categoria")
        self.car_cred.set("Cartão de Cobrança - Sem Cartão")

        self.campo_data_compra.set_date(self.data_atual)
        self.campo_primeira_dc.set_date(self.sentinela)
        
# =================================================================================
# --- CADASTRO DE CARTÕES DE CRÉDITO ---
# =================================================================================

class Cadastrar_car_cred(ctk.CTkFrame):
    """
    Formulário para definição de propriedades de cartões de crédito 
    (Limites, Dias de Fechamento/Vencimento e Cor).
    """

    def __init__(self, parent: Any = None, user_id: Optional[int] = None, nomes_cards: Optional[List[str]] = None, cb_comandante_crud: Optional[Callable] = None, cb_vcmd_num: Optional[Callable] = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.nomes_cards = nomes_cards or []
        self.cdt_crud = cb_comandante_crud
        self.vcmd_num = cb_vcmd_num

        # --------------- Configuração da janela/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1)

        # ------- TÍTULO DO FORMULÁRIO -------
        ctk.CTkLabel(self, text="Cadastre Seus Cartões de Crédito", font=("Arial", 18, "bold")).grid(row=0, column=0, pady=10)

        # ------ NOME DO CARTÃO ---------
        ctk.CTkLabel(self, text="Nome do Cartão*", font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, padx=20, sticky="w")
        self.nome_cc = ctk.CTkEntry(self, placeholder_text="Itaú Uniclass")
        self.nome_cc.grid(row=2, column=0, padx=20, pady=(2,10), sticky="ew")

        # -------- LIMITE DO CARTÃO -------
        ctk.CTkLabel(self, text="Limite do Cartão*", font=ctk.CTkFont(size=12, weight="bold")).grid(row=3, column=0, padx=20, sticky="w")
        self.limite = ctk.CTkEntry(self, placeholder_text="1000,00", validate='key', validatecommand= self.vcmd_num)
        self.limite.grid(row=4, column=0, padx=20, pady=(2,10), sticky="ew")

        # -------- DIA FECHAMENTO -------
        ctk.CTkLabel(self, text="Dia de Fechamento*", font=ctk.CTkFont(size=12, weight="bold")).grid(row=5, column=0, padx=20, sticky="w")
        self.dia_fechamento = ctk.CTkEntry(self, placeholder_text="8", validate='key', validatecommand= self.vcmd_num)
        self.dia_fechamento.grid(row=6, column=0, padx=20, pady=(2,10), sticky="ew")

        # -------- DIA VENCIMENTO -------
        ctk.CTkLabel(self, text="Dia de Vencimento*", font=ctk.CTkFont(size=12, weight="bold")).grid(row=7, column=0, padx=20, sticky="w")
        self.dia_vencimento = ctk.CTkEntry(self, placeholder_text="12", validate='key', validatecommand= self.vcmd_num)
        self.dia_vencimento.grid(row=8, column=0, padx=20, pady=(2,10), sticky="ew")

        # ------ BANDEIRA ---------
        ctk.CTkLabel(self, text="Bandeira do Cartão", font=ctk.CTkFont(size=12, weight="bold")).grid(row=9, column=0, padx=20, sticky="w")
        self.bandeira = ctk.CTkEntry(self, placeholder_text="MasterCard")
        self.bandeira.grid(row=10, column=0, padx=20, pady=(2,10), sticky="ew")

        # ------ COR ---------
        cores = ['Sem Cor','Roxo', 'Laranja', 'Preto', 'Vermelho', 'Cinza', 'Verde']
        ctk.CTkLabel(self, text="Cor do Cartão*", font=ctk.CTkFont(size=12, weight="bold")).grid(row=11, column=0, padx=20, sticky="w")
        self.cor = ctk.CTkOptionMenu(self, values=cores)
        self.cor.grid(row=12, column=0, padx=20, pady=(2, 10), sticky="ew")
        self.cor.set('Sem Cor')

        # -------- BOTÃO SALVAR ---------
        self.botao_salvar = ctk.CTkButton(self, text="Salvar Dados", command=self.salvar_dados)
        self.botao_salvar.grid(row=13, column=0, padx=20, pady=(2,10), sticky="ew")

        # -------- STATUS -----------
        self.status_label = ctk.CTkLabel(self, text="", text_color="red")
        self.status_label.grid(row=14, column=0, pady=5)


    def salvar_dados(self, id_card: Optional[int] = None, atualizar: bool = False) -> None:
        """Processa e valida a criação/edição da entidade Cartao_credito."""

        nome_cc = self.nome_cc.get().strip()
        limite = self.limite.get().strip()
        dia_f = self.dia_fechamento.get().strip()
        dia_v = self.dia_vencimento.get().strip()
        bandeira = self.bandeira.get().strip()
        cor_card = self.cor.get().strip()
        
        # Evita duplicidade de nomes para não confundir o helper/joins
        for nome in self.nomes_cards:
            if nome == nome_cc:
                tocar_notificacao("dv_erro", True)
                if not atualizar:
                    self.status_label.configure(text=f'Por favor, Não repita nome de cartões já cadastrados, tente - *{nome_cc}10', text_color='red')
                    self.update_idletasks()
                    self.after(3000, lambda: self.status_label.configure(text=''))
                    return

        if not nome_cc or not limite or not dia_f or not dia_v:
            self.status_label.configure(text='Por favor, preencha todos os campos obrigarórios (*)', text_color='red')
            tocar_notificacao("dv_erro", True)
            self.update_idletasks()
            self.after(2000, lambda: self.status_label.configure(text=''))
            return
        
        try:
            limite_float = float(limite.replace(',', '.'))
            dia_f_int = int(dia_f)
            dia_v_int = int(dia_v)
        except ValueError:
            self.status_label.configure(text='Limites e dias devem ser numéricos!', text_color='red')
            return

        obj_cartao = Cartao_credito(nome=nome_cc, limite=limite_float, fech=dia_f_int, venc=dia_v_int, bandeira=bandeira, cor=cor_card)

        if not atualizar: 
            sucesso = self.cdt_crud(inserir=obj_cartao) if self.cdt_crud else False
            msg_ok = "INSERIDOS"
            msg_erro = "SALVAR"
        else:
            obj_cartao.id_cartao = id_card
            sucesso = self.cdt_crud(atualizar=obj_cartao) if self.cdt_crud else False
            msg_ok = "ATUALIZADOS"
            msg_erro = "ATUALIZAR"

        if sucesso:
            self.status_label.configure(text=f'Os dados foram {msg_ok} com sucesso!', text_color='green')
            self.update_idletasks()
            self.after(2000, lambda: self.status_label.configure(text=''))
            self.controla_campos(None)
        else:
            self.status_label.configure(text=f'Não foi possível {msg_erro} os dados, contate o adm do sistema...', text_color='red')
            self.update_idletasks()
            self.after(2000, lambda: self.status_label.configure(text=''))
    

    def controla_campos(self, dados: Optional[Dict[str, Any]] = None) -> None:
        """Preenche o form para update com base em registro pré-selecionado na UI."""

        self.limpa_campos()

        if dados:
            id_card = dados.get('id_cartao')

            self.nome_cc.insert(0, str(dados.get('nome_cartao', '')))
            self.limite.insert(0, str(dados.get('limite_cartao', '')))
            self.dia_fechamento.insert(0, str(dados.get('dia_fechamento', '')))
            self.dia_vencimento.insert(0, str(dados.get('dia_vencimento', '')))

            ret_bandeira = dados.get('bandeira') or ""
            self.bandeira.insert(0, str(ret_bandeira))

            ret_cor = dados.get('cor') or 'Sem Cor'
            self.cor.set(formata_cor(cor=str(ret_cor)))

            self.botao_salvar.configure(text='Atualizar Cartão', fg_color="orange", command=lambda: self.salvar_dados(id_card, atualizar=True))
        else:
            self.botao_salvar.configure(
            text="Salvar Dados", 
            fg_color=["#3B8ED0", "#1F6AA5"], 
            command=self.salvar_dados 
        )

    def limpa_campos(self) -> None:
        """Limpa todos os campos de entrada do formulário de cartões.""" 
        self.nome_cc.delete(0, ctk.END)
        self.limite.delete(0, ctk.END)
        self.dia_fechamento.delete(0, ctk.END)
        self.dia_vencimento.delete(0, ctk.END)
        self.bandeira.delete(0, ctk.END)
        self.cor.set('Sem Cor')


# =================================================================================
# --- CADASTRO DE ASSINATURAS ---
# =================================================================================

class Cadastrar_assinatura(ctk.CTkFrame):
    """Formulário focado em pagamentos recorrentes indefinidos (Assinaturas)."""

    def __init__(self, parent: Any = None, user_id: Optional[int] = None, dados_cartoes: Optional[List[Dict[str, Any]]] = None, cb_comandante_crud: Optional[Callable] = None, cb_vcmd_num: Optional[Callable] = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.dados_cartoes = dados_cartoes or []
        self.cdt_crud = cb_comandante_crud
        self.vcmd_num = cb_vcmd_num
        
        # ---------------- Gerencimento de self --------------------
        self.data_atual = datetime.now().date()
        self.sentinela = (self.data_atual.replace(day=1, month=1, year=2099))

        self.nomes_cartoes = [c['nome_cartao'] for c in self.dados_cartoes]
        
        # --------------- Configuração da janela/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1)

        # ------- TÍTULO DO FORMULÁRIO ---------
        ctk.CTkLabel(self, text="Cadastre Suas Assinaturas", font=("Arial", 18, "bold")).grid(row=0, column=0, pady=10)

        # -------- NOME DA ASSINATURA ----------
        ctk.CTkLabel(self, text="Nome da Assinatura*", font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, padx=20, sticky="w")
        self.entry_nome = ctk.CTkEntry(self, placeholder_text="Netflix")
        self.entry_nome.grid(row=2, column=0, padx=20, pady=(2,10), sticky="ew")

        # -------- VALOR DA ASSINATURA ---------
        ctk.CTkLabel(self, text="Valor*", font=ctk.CTkFont(size=12, weight="bold")).grid(row=3, column=0, padx=20, sticky="w")
        self.entry_valor = ctk.CTkEntry(self, placeholder_text="49,90", validate='key', validatecommand= self.vcmd_num )
        self.entry_valor.grid(row=4, column=0, padx=20, pady=(2,10), sticky="ew")
        
        # -------- DESCRIÇÃO ---------
        ctk.CTkLabel(self, text="Descrição", font=ctk.CTkFont(size=12, weight="bold")).grid(row=5, column=0, padx=20, sticky="w")
        self.entry_desc = ctk.CTkEntry(self, placeholder_text="'Serviço de Streaming'", width=300)
        self.entry_desc.grid(row=6, column=0, padx=20, pady=(2,10), sticky="ew")

        # ------- DATA DE AQUISIÇÃO -------
        self.label_prim_dp = ctk.CTkLabel(self, text="Data Aquisição", font=ctk.CTkFont(size=12, weight="bold"))
        self.label_prim_dp.grid(row=7, column=0)

        self.data_aquisicao = DateEntry(self, width=12, background='darkblue',
                            foreground='white', borderwidth=2, year=2026, 
                            locale='pt_BR', date_pattern='dd/mm/yyyy')
        
        self.data_aquisicao.grid(row=8, column=0, padx=(2,10), pady=10)

        # -------- DATA PRIMEIRO PAGAMENTO - COMPRA SEM CARTÃO ------
        self.label_primeira_dc = ctk.CTkLabel(self, text="Data do Primeiro Pagamento: \n(obs. Não preencher se a compra for no C. Crédito)", font=ctk.CTkFont(size=12, weight="bold"))
        self.label_primeira_dc.grid(row=9, column=0)

        self.campo_prim_dp = DateEntry(self, width=12, background='darkblue',
                            foreground='white', borderwidth=2, day=1, month=1, year=2099, 
                            locale='pt_BR', date_pattern='dd/mm/yyyy')
        self.campo_prim_dp.grid(row=10, column=0, padx=(2,10), pady=10)

        # ------- MENU DE CATEGORIAS ---------
        categorias = ['Não Selecionado','Lazer', 'Essencial', 'Estudos', 'Saúde', ' Hobby','Streaming', 'Outros']

        ctk.CTkLabel(self, text="Categorias*", font=ctk.CTkFont(size=12, weight="bold")).grid(row=11, column=0, padx=20, sticky="w")
        self.menu_cat = ctk.CTkOptionMenu(self, values=categorias, width=300)
        self.menu_cat.grid(row=12, column=0, padx=20, pady=(2,10), sticky="ew")

        # ------- MENU DE CARTÕES ---------
        if self.nomes_cartoes:
            campo_cartoes = ["Cartão de Cobrança - Sem Cartão"] + self.nomes_cartoes
            self.menu_cc = ctk.CTkOptionMenu(self, values=campo_cartoes, width=300)
            self.menu_cc.grid(row=13, column=0, padx=20, pady=(2,10), sticky="ew")
            self.menu_cc.set("Cartão de Cobrança - Sem Cartão")
        else:
            self.menu_cc = ctk.CTkOptionMenu(self, values=[' ', ' ',])
            self.menu_cc.grid(row=13, column=0, padx=20, pady=(2,10), sticky="ew")
            self.menu_cc.set("Cadastre Seus Cartões Na Área Destinada")
    
        # ------ BOTÃO SALVAR -------
        self.btn_salvar = ctk.CTkButton(self, text="Confirmar Assinatura", command=self.salvar_dados, fg_color="#2c3e50", hover_color="#34495e")
        self.btn_salvar.grid(row=14, column=0, padx=20, pady=10, sticky="ew")

        # --------- STATUS ----------
        self.status_label = ctk.CTkLabel(self, text="", text_color="red")
        self.status_label.grid(row=15, column=0, pady=5)


    def salvar_dados(self, id_ass: Optional[int] = None, atualizar: bool = False) -> None:
        """Processa e valida a criação/edição da entidade assinatura."""

        dia_venc = None
        verifica_data_pp = False
        id_card = None

        nome = self.entry_nome.get().strip()
        valor_str = self.entry_valor.get().strip()
        descricao = self.entry_desc.get().strip()
        data_aq =  self.data_aquisicao.get_date()
        data_pp = self.campo_prim_dp.get_date()
        categoria = self.menu_cat.get().strip()
        cartao = self.menu_cc.get().strip()

        data_aq_mysql = data_para_mysql(data_aq)
        data_pp_mysql = None

        if data_pp != self.sentinela:
            dia_venc = data_pp.day
            verifica_data_pp = True
            data_pp_mysql = data_para_mysql(data_pp)

            if data_pp.year == self.sentinela.year:
                self.status_label.configure(text='Mude o ano da data de primeiro pagemento', text_color='red')
                tocar_notificacao("dv_erro", True)
                self.after(3000, lambda: self.status_label.configure(text='')) 
                return

        if not nome or not valor_str or categoria == "Selecione a Categoria":
            self.status_label.configure(text='Preencha Nome, Valor, Categoria ,', text_color='red')
            tocar_notificacao("dv_erro", True)
            self.after(3000, lambda: self.status_label.configure(text=''))
            return

        try:
            valor = float(valor_str.replace(",", "."))
        except ValueError:
            self.status_label.configure(text=" 'Valor' deve ser números válidos!", text_color='red')
            tocar_notificacao("dv_erro", True)
            self.after(3000, lambda: self.status_label.configure(text=''))
            return
        
        tem_cartao = cartao != "Cartão de Cobrança - Sem Cartão"
        if tem_cartao:
            for dado in self.dados_cartoes:
                if dado.get('nome_cartao') == cartao:
                    id_card = dado.get('id_cartao')

        if not verifica_data_pp and cartao == "Cartão de Cobrança - Sem Cartão":
            self.status_label.configure(text='Selecione uma data de primeiro pagamento ou um cartão de crédito ', text_color='red')
            tocar_notificacao("dv_erro", True)
            self.after(3000, lambda: self.status_label.configure(text='')) 
            return
        
        obj_assinatura = Assinatura(nome=nome, valor=valor, descricao=descricao, categoria=categoria, data_aq=data_aq_mysql, data_pp=data_pp_mysql, dia_venc=dia_venc, id_cc=id_card) # type: ignore

        if not atualizar: 
            sucesso = self.cdt_crud(inserir=obj_assinatura) if self.cdt_crud else False
            msg_ok = "INSERIDOS"
            msg_falha = "Não foi possível SALVAR os dados, contate o adm do sistema...'"
        else: 
            obj_assinatura.id_ass = id_ass
            sucesso = self.cdt_crud(atualizar=obj_assinatura) if self.cdt_crud else False
            msg_ok = "ATUALIZADOS"
            msg_falha = "Não foi possível ATUALIZAR os dados, contate o adm do sistema...'"

        if sucesso:
            self.status_label.configure(text=f'Os dados foram {msg_ok} com sucesso!', text_color='green')
            self.update_idletasks()
            self.controla_campos(None)
            self.after(2000, lambda: self.status_label.configure(text=''))  
        else:
            self.status_label.configure(text=f'{msg_falha}', text_color='red')
            self.update_idletasks()
            self.after(2000, lambda: self.status_label.configure(text=''))


    def controla_campos(self, dados: Optional[Dict[str, Any]] = None) -> None:
        """Preenche o form para update com base em registro pré-selecionado na UI."""

        self.limpa_campos()

        if dados:
            nome_card = "Cartão de Cobrança - Sem Cartão"

            if self.dados_cartoes:
                for cartao in self.dados_cartoes:
                    if cartao.get('id_cartao') == dados.get('id_cc'):
                        nome_card = str(cartao.get('nome_cartao', ''))

            id_ass = dados.get('id_ass')
            data_aq_obj = mysql_para_obj(dados.get('data_aquisicao'))
            data_pp_obj = mysql_para_obj(dados.get('data_pp'))

            self.entry_nome.insert(0, str(dados.get('nome', '')))
            self.entry_valor.insert(0, str(dados.get('valor', '')))
            self.entry_desc.insert(0, str(dados.get('descricao', '')))
            
            if data_aq_obj: self.data_aquisicao.set_date(data_aq_obj)
            if data_pp_obj: self.campo_prim_dp.set_date(data_pp_obj)
            
            self.menu_cat.set(str(dados.get('categoria', '')))
            self.menu_cc.set(nome_card)

            self.btn_salvar.configure(text='Atualizar Assinatura', fg_color="orange", command=lambda: self.salvar_dados(id_ass, atualizar=True))
        else:
            self.btn_salvar.configure(
            text="Confirmar Assinatura", 
            fg_color=["#3B8ED0", "#1F6AA5"],
            command=self.salvar_dados
        )

    def limpa_campos(self) -> None:
        """Restaura todas as comboboxes e entries do form Assinatura para o padrão."""
        self.entry_nome.delete(0, ctk.END)
        self.entry_valor.delete(0, ctk.END)
        self.entry_desc.delete(0, ctk.END)

        self.menu_cat.set("Selecione a Categoria")
        self.menu_cc.set("Cartão de Cobrança - Sem Cartão")

        self.data_aquisicao.set_date(self.data_atual)
        self.campo_prim_dp.set_date(self.sentinela)