

import MySQLdb
import configparser
from typing import Optional, Dict, Any

class Test_database:
    def __init__(self) -> None:
        self.test_config: Optional[Dict[str, Any]] = self._ler_configuracao()

    def _ler_configuracao(self) -> Optional[Dict[str, Any]]:
        """Lê as credenciais de infraestrutura a partir de arquivo de configuração INI externo."""

        config = configparser.ConfigParser()
        
        try:
            arquivos_lidos = config.read('tests/test_config.ini')
            if not arquivos_lidos:
                raise FileNotFoundError("Arquivo 'test_config.ini' não foi localizado na pasta tests/")

            if 'mysql' not in config:
                raise ValueError("Seção obrigatória [mysql] não encontrada em config.ini")
            
            db_config = config['mysql']
            return {
                'host': db_config.get('host', 'localhost'),
                'user': db_config.get('user'),
                'passwd': db_config.get('passwd'),
                'db': db_config.get('db')
            }
        except FileNotFoundError:
            print(f"Erro Crítico: {e}")
            return None
        except ValueError as e:
            print(f"Erro de Parse de Configuração: {e}")
            return None
        except Exception as e:
            print(f"Erro de E/S inesperado ao mapear test_config.ini: {e}")
            return None 


    def conectar_bd_teste(self) -> Optional[MySQLdb.Connection]:
        """Inicializa e retorna uma instância estável de conexão ativa com o servidor MySQL de teste."""

        if not self.test_config:
            print("Handshake abortado devido a falhas na leitura do test_config.ini.")
            return None
    
        try:
            conn = MySQLdb.connect(
                db=self.test_config['db'],
                host=self.test_config['host'],
                user=self.test_config['user'],
                passwd=self.test_config['passwd']
            )
            return conn
        
        except MySQLdb.Error as e:
            print(f'Falha na tabela de conexões ao MySQL Server: {e}')
            return None

    def desconectar(self, conn: Optional[MySQLdb.Connection]) -> None:
        """Garante a desalocação dos sockets e encerramento da conexão ativa."""
        if conn:
            conn.close()