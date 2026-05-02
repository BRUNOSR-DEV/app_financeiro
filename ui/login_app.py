
from models.conecte_bd import (dados_usuarios)

from utils.typedDict import(Dados_usuarios_db)

from utils.audio_helper import tocar_notificacao 
from utils.helper import(centralizar_janela)
import time

from typing import List

import customtkinter as ctk
ctk.set_appearance_mode('dark')


from ui.forms import(Registro_usuario)

#Módulo Login
class Login(ctk.CTk):

    tocar_notificacao("open", True)


    def __init__(self):
        super().__init__()

        # --------------- Configuração da janela/'labels' -----------------------
        self.title('Sistema de Login')
        centralizar_janela(self, 350, 400)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=0)

        self.label = ctk.CTkLabel(self, text="Faça seu Login", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.grid(row=0, column=0, pady=20)

        self.usuario_entry = ctk.CTkEntry(self, placeholder_text="Usuário")
        self.usuario_entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.senha_entry = ctk.CTkEntry(self, placeholder_text="Senha", show="*")
        self.senha_entry.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.botao_enter = ctk.CTkButton(self, text="Entrar", command=self.validar_login, 
                                         fg_color="#000200", hover_color="#FC0404")
        self.botao_enter.grid(row=3, column=0, padx=20, pady=10)
        self.bind("<Return>", lambda event: self.botao_enter.invoke())

        self.registrar = ctk.CTkButton(self, text="Registrar", command=self.abrir_tela_registro,
                                       fg_color="#000200", hover_color="#FC0404")
        self.registrar.grid(row=4, column=0, padx=20, pady=10)

        self.status_label = ctk.CTkLabel(self, text="", text_color="red")
        self.status_label.grid(row=5, column=0, pady=5)

        # ---------------- Gerencimento ---------------------

        self.usuarios: List[Dados_usuarios_db] = dados_usuarios()
        self.usuario_logado = None


    def quit_and_destroy(self):
        self.quit()    # Para o mainloop com elegância
        self.destroy()

    def validar_login(self):
        """ Valida o login que o usuário inseriu na entry"""

        usuario_entry = self.usuario_entry.get()
        senha_entry = self.senha_entry.get()
        login_sucesso = False
        usuario_logado = usuario_entry

        for _, user in enumerate(self.usuarios):
            if usuario_entry == user["nome_user"] and senha_entry == user["senha"]:
                login_sucesso = True
                break
         
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
        """ Direciona o usuário para fazer cadastro, chamando a classe Registro_usuario"""

        tocar_notificacao("open_w", True)
        
        register_window = Registro_usuario(self)
        
        self.wait_window(register_window) 