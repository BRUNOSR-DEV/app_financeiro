from ui.main_app import Main_app
from ui.login_app import Login

def rodar_sistema():

    while True:
        # 1. Abre o Login
        app_login = Login()
        app_login.tk.eval('proc bgerror {args} {}')
        app_login.mainloop()

        # 2. Verifica se o login teve sucesso
        if hasattr(app_login, 'usuario_logado'):
            user = app_login.usuario_logado
            
            # 3. Abre a Main
            app_principal = Main_app(logged_in_username=user)
            app_principal.mainloop()

            print("...")

            if getattr(app_principal, 'atualiza_sistema', False):

                print('atualizando sistema!')
                app_principal = Main_app(logged_in_username=user)
                app_principal.mainloop()

            if getattr(app_principal, 'quer_voltar_login', False):
                print("Reiniciando para tela de login...")
                continue
            else:
                print('Encerrando sistema...')
                break
        else:
            # Se fechou o login sem logar, encerra o app
            break

if __name__ == "__main__":
    rodar_sistema()