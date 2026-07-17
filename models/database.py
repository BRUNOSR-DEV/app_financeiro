"""
Módulo de Conexão com Banco de Dados (Database Infrastructure)

Gerencia o ciclo de vida de conexões brutas com o servidor MySQL/MariaDB
utilizando o driver MySQLdb, aplicando isolamento de credenciais via config.ini.
"""
import os
import sys
import MySQLdb
import configparser
from typing import Optional, Dict, Any

class Database:
    def __init__(self) -> None:
        self.config: Optional[Dict[str, Any]] = self._ler_configuracao()

    
    def _obter_caminho_ini(self) -> str:
        """Determina o caminho do config.ini dinamicamente para dev e .exe"""
        if getattr(sys, 'frozen', False):
            # Se estiver rodando como executável (.exe), pega a pasta do .exe
            diretorio_base = os.path.dirname(sys.executable)
        else:
            # Se estiver rodando em desenvolvimento no VS Code
            diretorio_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
 
            
        return os.path.join(diretorio_base, 'config.ini')

    def _ler_configuracao(self) -> Optional[Dict[str, Any]]:
        """Lê as credenciais de infraestrutura a partir de arquivo de configuração INI externo."""

        config = configparser.ConfigParser()
        
        try:
            caminho_ini = self._obter_caminho_ini()
            arquivos_lidos = config.read(caminho_ini, encoding='utf-8')
            
            if not arquivos_lidos:
                raise FileNotFoundError(f"Arquivo de infraestrutura 'config.ini' não localizado em: {caminho_ini}")

            if 'mysql' not in config:
                raise ValueError("Seção obrigatória [mysql] não encontrada em config.ini")
            
            db_config = config['mysql']
            return {
                'host': db_config.get('host', 'localhost'),
                'user': db_config.get('user'),
                'passwd': db_config.get('passwd'),
                'db': db_config.get('db')
            }
        except FileNotFoundError as e:
            print(f"Erro Crítico: {e}")
            return None
        except ValueError as e:
            print(f"Erro de Parse de Configuração: {e}")
            return None
        except Exception as e:
            print(f"Erro de E/S inesperado ao mapear config.ini: {e}")
            return None


    def conectar_bd_original(self) -> Optional[MySQLdb.Connection]:
        """Inicializa e retorna uma instância estável de conexão ativa com o servidor MySQL."""

        if not self.config:
            print("Handshake abortado devido a falhas na leitura do config.ini.")
            return None
    
        try:
            conn = MySQLdb.connect(
                db=self.config['db'],
                host=self.config['host'],
                user=self.config['user'],
                passwd=self.config['passwd']
            )
            return conn
        except MySQLdb.Error as e:
            print(f'Falha na tabela de conexões ao MySQL Server: {e}')
            return None

    def desconectar(self, conn: Optional[MySQLdb.Connection]) -> None:
        """Garante a desalocação dos sockets e encerramento da conexão ativa."""
        if conn:
            conn.close()