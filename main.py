"""
Módulo Orquestrador Supremo (Super Main)

Este script atua como o ponto de entrada absoluto (Root Entry Point) de todo o software.
Ele implementa um loop de controle de estado em nível de thread principal para alternar
visualmente as janelas de Autenticação (Login) e a Nave-mãe Operacional (Main_app),
garantindo a desalocação de memória e tratamento limpo de fluxos de Logout.
"""

# ---------------------------------- IMPORTAÇÃO - MÓDULOS LOCAIS ------------------------------------
from ui.main_app import Main_app
from ui.login_app import Login


def rodar_sistema() -> None:
    """
    Executa a engine de loop infinito para controle sequencial de janelas do app.
    
    O fluxo obedece a máquina de estados abaixo:
    [Login] --(Sucesso)--> [Main_app] --(Logout)--> [Login]
    [Login] --(Fechar)---> [Encerrar]
    [Main_app] --(X)-----> [Encerrar]
    """
    while True:
        # 1. Instancia e renderiza a janela de Autenticação
        app_login = Login()
        
        # Silencia pop-ups intrusivos do interpretador Tcl/Tk em threads de background
        app_login.tk.eval('proc bgerror {args} {}')
        app_login.mainloop()

        # 2. Avalia interceptores de segurança pós-fechamento do Login
        if hasattr(app_login, 'usuario_logado'):
            user = app_login.usuario_logado
            
            # 3. Transiciona e eleva os privilégios abrindo o Dashboard Principal
            app_principal = Main_app(logged_in_username=user)
            app_principal.mainloop()

            print("...")

            # 4. Checa gatilho situacional de Logout injetado no botão "Sair"
            if getattr(app_principal, 'quer_voltar_login', False):
                print("Reiniciando para tela de login... 🔄")
                continue
            else:
                print('Encerrando sistema de forma controlada... 👋')
                break
        else:
            # Se o usuário fechar a tela de login no "X" sem se autenticar, encerra a pilha
            print('Acesso não autenticado. Finalizando execução.')
            break

if __name__ == "__main__":
    # Gatilho de execução raiz do projeto
    rodar_sistema()