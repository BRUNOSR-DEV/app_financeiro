import MySQLdb
from models.database import Database

class Rep_Usuarios:

    def __init__(self, db: Database):
        self.db = db
#fazendo alterações na branch

class Rep_Receitas:

    def __init__(self, db: Database):
        self.db = db
    
    def dados_receitas(self, id_user, conn=None):
        """
        Função que retorna os dados do  usuario
        """
        gerenciar_conn = False

        if conn is None:
            conn= self.db.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()

        try:
            query = "SELECT id, valor, descricao, data FROM receitas WHERE id_usuario= %s"
            cursor.execute(query, (id_user, ))
            receitas = cursor.fetchall()

            colunas = [
                'id_receita', 'valor_recebido', 'descricao', 'data'
            ]

            if receitas:
                return [dict(zip(colunas, valor)) for valor in receitas]
            else:
                return []
        
        except MySQLdb.Error as e: # Captura erro específico do MySQL
            print(f'Erro no MySQL ao buscar dados de receitas: {e}')
            raise # Re-levanta a exceção para que o chamador saiba que algo deu errado

        except Exception as e:
            print(f'Erro inesperado ao buscar dados de receitas: {e}')

        finally:
            if gerenciar_conn:
                self.db.desconectar(conn)


class Rep_Despesas:

    def __init__(self, db: Database):
        self.db = db


class Rep_Card_credito:

    def __init__(self, db: Database):
        self.db = db


class Rep_Assinaturas:

    def __init__(self, db: Database):
        self.db = db