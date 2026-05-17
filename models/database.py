import MySQLdb

import configparser

class Database:
    def __init__(self):
        self.config = self._ler_configuracao()

    def _ler_configuracao(self):
        """Lê as credenciais do banco de dados do arquivo config.ini."""
        config = configparser.ConfigParser()
        
        # Tenta ler o arquivo de configuração
        try:
            config.read('config.ini')
            if 'mysql' not in config:
                raise ValueError("Seção [mysql] não encontrada em config.ini")
            
            db_config = config['mysql']
            return {
                'host': db_config.get('host', 'localhost'),
                'user': db_config.get('user'),
                'passwd': db_config.get('passwd'),
                'db': db_config.get('db')
            }
        except FileNotFoundError:
            print("Erro: Arquivo 'config.ini' não encontrado.")
            return None
        except ValueError as e:
            print(f"Erro de configuração: {e}")
            return None
        except Exception as e:
            print(f"Erro inesperado ao ler o arquivo de configuração: {e}")
            return None 
        

    def conectar_bd_original(self):
        """Função para conectar ao servidor"""

        if not self.config:
            # Se as credenciais não puderam ser lidas, não tente conectar
            print("Não foi possível conectar ao banco de dados devido a um erro de configuração.")
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
            print(f'Erro na conexão ao MySql Server: {e}')


    def desconectar(self, conn):
        if conn:
            conn.close()