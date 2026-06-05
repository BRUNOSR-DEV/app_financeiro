
# ---------------------------------- IMPORTAÇÃO - MÓDULOS LOCAIS ------------------------------------
# ----- BANCO DE DADOS ------
from models.database import Database
from models.repositorios import Rep_Usuario

#------ IMPORTAÇÃO DE CLASSE GERENCIADORA DE JANELAS - (crud_app.py) --------
from ui.crud_app import(CrudManage)

#------ IMPORTAÇÃO DE CLASSES TYPEDDICT - (typedDict.py) --------
from utils.typedDict import(Dados_usuarios_db)

# ----- FUNÇÕES DE AJUDA - (helper.py/audio_helper.py) -------
from utils.audio_helper import tocar_notificacao 
from utils.helper import(centralizar_janela_responsiva, check_entry_num)

# ------------------------------ IMPORTAÇÃO - MÓDULOS BIBLIOTECAS ---------------------------------
#BILIO PADRÕES
import time
from typing import List

#BIBLIO VIA PIP
import customtkinter as ctk

# ------------- CONFIGURAÇÃO INICIAL ---------------
ctk.set_appearance_mode('dark')


#Módulo Login
class Login(ctk.CTk):

    tocar_notificacao("open", True)

    def __init__(self):
        super().__init__()
        self.db_conn = Database()
        self.db = Rep_Usuario(self.db_conn)

        self.vcmd_num = (self.register(check_entry_num), '%P')
        self.crudManager = CrudManage(self, cb_atualiza_bd=self.atualiza_bd, cb_vcmd_num=self.vcmd_num)
        
        # --------------- Configuração da janela/'labels' -----------------------
        self.title('Sistema de Login')
        centralizar_janela_responsiva(janela=self, tipo_janela='login')
        self.grid_columnconfigure(0, weight=1)

        # ---- LABEL DE LOCALIZAÇÃO ----
        self.label = ctk.CTkLabel(self, text="Faça seu Login", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.grid(row=0, column=0, pady=20)

        # ----- NOME DE USUÁRIO -----
        ctk.CTkLabel(self, text="Nome de Usuário", font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, padx=20, sticky="w")
        self.usuario_entry = ctk.CTkEntry(self, placeholder_text="Dante123")
        self.usuario_entry.grid(row=2, column=0, padx=20, pady=(2,10), sticky="ew")
        
        # ----- SENHA DE ACESSO -----
        ctk.CTkLabel(self, text="Senha de Acesso", font=ctk.CTkFont(size=12, weight="bold")).grid(row=3, column=0, padx=20, sticky="w")
        self.senha_entry = ctk.CTkEntry(self, placeholder_text="*admin", show="*")
        self.senha_entry.grid(row=4, column=0, padx=20, pady=(2,10), sticky="ew")

        # ------ BOTÃO ENTRAR -------
        self.botao_enter = ctk.CTkButton(self, text="Entrar", command=self.validar_login, 
                                         fg_color="#000200", hover_color="#FC0404")
        self.botao_enter.grid(row=5, column=0, padx=20, pady=10)
        self.bind("<Return>", lambda event: self.botao_enter.invoke())

        # ------ BOTÃO REGISTRO -------
        self.registrar = ctk.CTkButton(self, text="Registrar", command=self.abrir_tela_registro,
                                       fg_color="#000200", hover_color="#FC0404")
        self.registrar.grid(row=6, column=0, padx=20, pady=10)

        # ------- STATUS ----------
        self.status_label = ctk.CTkLabel(self, text="", text_color="red")
        self.status_label.grid(row=7, column=0, pady=5)

        # ---------------- Gerencimento ---------------------

        self.usuario_logado = None

        self.atualiza_bd()

    def atualiza_bd(self):
        self.usuarios: List[Dados_usuarios_db] = self.db.dados_usuarios()


    def quit_and_destroy(self):
        self.quit()    # Para o mainloop com elegância
        self.destroy()


    def validar_login(self):
        """ Valida o login que o usuário inseriu na entry"""

        usuario_entry = self.usuario_entry.get().strip()
        senha_entry = self.senha_entry.get().strip()

        login_sucesso = False
        usuario_logado = usuario_entry

        login_sucesso = self.db.validar_credenciais(username=usuario_entry, senha_digitada=senha_entry)

        if login_sucesso:
            self.status_label.configure(text='Login feito com sucesso', text_color='green')
            self.update_idletasks()
            time.sleep(0.8)

            tocar_notificacao('autenticacao', True)

            self.usuario_logado = usuario_logado

            self.after(500, self.quit_and_destroy)


        else:
            self.status_label.configure(text='Login Incorreto!', text_color='red')
            tocar_notificacao('erro')
            
            self.update_idletasks()
            self.after(2000, lambda: self.status_label.configure(text=''))
            
    

    def abrir_tela_registro(self):
        self.crudManager.tela_usuarios()
