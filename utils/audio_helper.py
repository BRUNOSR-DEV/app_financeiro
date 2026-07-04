"""
Módulo de Infraestrutura de Áudio (Audio Helper)

Interface gráfica sonora baseada na engine Pygame Mixer. Suporta a execução síncrona
de alertas e triggers de notificações mapeados em assets binários (.mp3 e .mpeg).
"""

import pygame
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    pygame.mixer.init()
except Exception:
    print("Aviso: Dispositivo de áudio não encontrado (Ambiente CI/CD).")


def tocar_notificacao(tipo: str, boll: bool = False) -> None:
    """Toca um feedback sonoro baseado no evento mapeado no sistema."""
    
    try:
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
        if not nome_arq:
            print(f"Tipo de áudio inválido ou não mapeado: {tipo}")
            return
        
        extensao = ".mpeg" if boll else ".mp3"
        caminho = os.path.join(BASE_DIR, "assets", f"{nome_arq}{extensao}")
        
        if os.path.exists(caminho):
            try:
                pygame.mixer.music.load(caminho)
                pygame.mixer.music.play()
            except Exception as e:
                print(f'Erro ao carregar ou reproduzir mídia: {e}')
        else:
            print(f'Arquivo não encontrado no diretório de assets: {caminho}')

    except Exception as e:
        print(f"Erro fatal no subsistema de áudio: {e}")