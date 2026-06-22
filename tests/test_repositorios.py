

import MySQLdb
import unittest
from tests.test_database import Test_database
from models.repositorios import Rep_Usuario, Rep_Receita, Rep_Despesa, Rep_Cartao_credito, Rep_Assinatura
from models.entidades import *


def limpar_tabelas(conn: MySQLdb.Connection):
        """
        Limpa os dados das tabelas para garantir um ambiente isolado em cada teste.
    
        Trava de Segurança: Só executa o DELETE se o nome do banco de dados
        terminar com '_teste' ou '_test', evitando apagar dados reais acidentalmente.
        """

        cursor = conn.cursor()
    
        # Busca o nome do banco de dados atual para a trava de segurança
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()[0]

        if "test" not in db_name.lower():
            raise Exception(
                f"TRAVA DE SEGURANÇA: O banco conectado '{db_name}' não parece ser um banco de testes. "
                "Operação de limpeza abortada para evitar perda de dados reais."
            )

        try:
            # Desativa temporariamente a checagem de chave estrangeira para limpar sem erros
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            cursor.execute("DELETE FROM tarefas")
            cursor.execute("DELETE FROM usuario")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            conn.commit() 
        except MySQLdb.Error as e:
            print(f"Erro ao limpar tabelas de teste: {e}")
            conn.rollback()
            raise



class Test_Rep_Usuario(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Prepara a infraestrutura e a conexão uma única vez para esta classe."""
        cls.db_infra = Test_database()
        cls.conn = cls.db_infra.conectar_bd_teste()
        
        # Garante que o banco de testes comece sem sujeira antiga
        # limpar_tabelas(cls.conn) 
        
        print("\n==================================================")
        print("   INICIANDO SUÍTE DE TESTES: REPOSITÓRIO USUÁRIO")
        print("==================================================")

    @classmethod
    def tearDownClass(cls):
        """Desconecta do banco após rodar todos os testes desta entidade."""
        if hasattr(cls, 'conn') and cls.conn:
            cls.db_infra.desconectar(cls.conn)

        print("\n==================================================")
        print("   SUÍTE FINALIZADA: REPOSITÓRIO USUÁRIO")
        print("==================================================")


    def setUp(self):
        """Roda ANTES de cada método de teste individual."""
        self.rep = Rep_Usuario()

        limpar_tabelas(conn=self.conn)
        print(f"\n-> Rodando: {self._testMethodName}")


    def tearDown(self):
        """Roda DEPOIS de cada método de teste individual."""
        print(f"-> Finalizado: {self._testMethodName}")


    # --------- INICIANDO TESTES ---------
    def test_inserir_usuario_pega_id(self):
        """Garante que a entidade Usuário insere e retorna id do usuário."""

        # Arrange (Prepara o objeto)
        user = Usuario('Bruno Rodrigues', 'bruno', '1234', 'bruno@gmail.com', 2000, '11964824753', None)

        # Act & Assert (Executa as ações repassando o cls.conn que criamos no setUpClass)
        self.assertTrue(self.rep.inserir_usuario(usuario=user, conn=self.conn))
        
        user_id = self.rep.pega_id('bruno', conn=self.conn)

        # Assert Final
        self.assertIsNotNone(user_id)
        self.assertGreater(user_id, 0)






    
class Test_Rep_Receita(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Prepara a infraestrutura e a conexão uma única vez para esta classe."""
        cls.db_infra = Test_database()
        cls.conn = cls.db_infra.conectar_bd_teste()

        limpar_tabelas(cls.conn)
        print(f"\n--- Configurando teste Usuários: {cls._testMethodName} ---")

    @classmethod
    def tearDownClass(cls):
        """Desconecta do banco após rodar todos os testes desta entidade."""
        if hasattr(cls, 'conn') and cls.conn:
            cls.db_infra.desconectar(cls.conn)

    def test_fluxo(self):
        """Garante que a entidade Usuário consegue persistir dados."""

        # Injeta a conexão ativa do repositório real
        repo = Rep_Receita(conn=self.conn)
    


class Test_Rep_Despesa(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Prepara a infraestrutura e a conexão uma única vez para esta classe."""
        cls.db_infra = Test_database()
        cls.conn = cls.db_infra.conectar_bd_teste()

    @classmethod
    def tearDownClass(cls):
        """Desconecta do banco após rodar todos os testes desta entidade."""
        if hasattr(cls, 'conn') and cls.conn:
            cls.db_infra.desconectar(cls.conn)

    def test_fluxo(self):
        """Garante que a entidade Usuário consegue persistir dados."""

        # Injeta a conexão ativa do repositório real
        repo = Rep_Despesa(conn=self.conn)
    


class Test_Rep_Cartao_credito(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Prepara a infraestrutura e a conexão uma única vez para esta classe."""
        cls.db_infra = Test_database()
        cls.conn = cls.db_infra.conectar_bd_teste()

    @classmethod
    def tearDownClass(cls):
        """Desconecta do banco após rodar todos os testes desta entidade."""
        if hasattr(cls, 'conn') and cls.conn:
            cls.db_infra.desconectar(cls.conn)

    def test_fluxo(self):
        """Garante que a entidade Usuário consegue persistir dados."""

        # Injeta a conexão ativa do repositório real
        repo = Rep_Cartao_credito(conn=self.conn)
    


class Test_Rep_Assinatura(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Prepara a infraestrutura e a conexão uma única vez para esta classe."""
        cls.db_infra = Test_database()
        cls.conn = cls.db_infra.conectar_bd_teste()

    @classmethod
    def tearDownClass(cls):
        """Desconecta do banco após rodar todos os testes desta entidade."""
        if hasattr(cls, 'conn') and cls.conn:
            cls.db_infra.desconectar(cls.conn)

    def test_fluxo(self):
        """Garante que a entidade Usuário consegue persistir dados."""

        # Injeta a conexão ativa do repositório real
        repo = Rep_Assinatura(conn=self.conn)
    



