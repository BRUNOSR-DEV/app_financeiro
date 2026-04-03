import pygame
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

pygame.mixer.init()

def tocar_notificacao(tipo, boll=False):
    """
    Toca um som baseado no evento.
    Tipos: 'sucesso', 'erro', 'clique'
    """
    try:
        # Caminho dos sons (crie uma pasta 'assets/sons' no seu projeto)
        sons = {          
            "sucesso": "sucesso",
            "erro": "erro",
            "click": "click",
            "ligar_desligar": "abertura",
            "autenticacao": "authentication",
            "open": "system_open",
            "dv_sucesso": "dv_sucesso",
            "closed": "system_closed",
            "dv_delete": "dv_delete",
            "open_w": "open_window",
            "dv_erro": "dv_erro",
        }

        nome_arq = sons.get(tipo)
        
        if boll:
            caminho = os.path.join(BASE_DIR, "assets", f"{nome_arq}.mpeg")
        else:
            caminho = os.path.join(BASE_DIR, "assets", f"{nome_arq}.mp3")
        
        if os.path.exists(caminho):
            try:

                pygame.mixer.music.load(caminho)
                pygame.mixer.music.play()
            except Exception as e:
                print(f'erro ao tocar {e}')
        else:
            print(f'Arquivo não encontrado: {caminho}')

    except Exception as e:
        print(f"Erro ao reproduzir áudio: {e}")

    