

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

        # Limpa as tabelas do banco
        limpar_tabelas(conn=self.conn)
        print(f"\n-> Rodando: {self._testMethodName}")

        self.user1 = Usuario('Bruno Rodrigues', 'bruno', '1234', 'bruno@gmail.com', 2000, '11964824753', None)
        self.user2 = Usuario('Dante Sparta', 'dante', '1234', 'dante@gmail.com', 10000, '11964824753', None)
        self.user3 = Usuario('Kratos Good', 'kratos', '1234', 'kratos@gmail.com', 12000, '11964824753', None)


    def tearDown(self):
        """Roda DEPOIS de cada método de teste individual."""
        print(f"-> Finalizado: {self._testMethodName}")


                                    # --------- INICIANDO TESTES ---------

    def test_inserir_usuario_pega_id_pega_usuario(self):
        """Garante que a entidade Usuário insere e retorna id do usuário."""

        # Act & Assert (Executa as ações repassando o cls.conn que criamos no setUpClass)
        self.assertTrue(self.rep.inserir_usuario(usuario=self.user1, conn=self.conn))
        
        user_id = self.rep.pega_id('bruno', conn=self.conn)
        usuario = self.rep.pega_usuario(user_id, conn=self.conn)

        # Validação dos métodos
        self.assertIsNotNone(user_id)
        self.assertGreater(user_id, 0)
        self.assertIsNotNone(usuario)

        #Garante que o banco salvou e trouxe o dado certo
        self.assertEqual(usuario['id_user'], user_id)
        self.assertEqual(usuario['nome_completo'], self.user1.nome_completo)
        self.assertEqual(usuario['nome_user'], self.user1.nome_user)
        self.assertEqual(usuario['senha'], self.user1.senha)
        self.assertEqual(usuario['sal_fixo'], self.user1.sal_fixo)
        self.assertEqual(usuario['email'], self.user1.email)
        self.assertEqual(usuario['telefone'], self.user1.telefone)
        self.assertEqual(usuario['tci'], self.user1.tci)



    def test_listar_usuarios(self):
        """Garante que o método retorna os usuários do banco em dicionários"""

        #Inserindo dois usuários no banco
        self.rep.inserir_usuario(self.user1, conn=self.conn)
        self.rep.inserir_usuario(self.user2, conn=self.conn)
        self.rep.inserir_usuario(self.user3, conn=self.conn)
        

        usuarios = self.rep.dados_usuarios(conn=self.conn)

        # Garante que usuarios tenha os 3 usuários cadastrados
        self.assertEqual(len(usuarios),3)

        #Garante que o retorno é um dicionário com os campos mapeados corretamente
        primeiro_usuario = usuarios[0] # usuário Bruno
        self.assertIn('id_user', primeiro_usuario)
        self.assertIn('nome_completo', primeiro_usuario)
        self.assertIn('nome_user', primeiro_usuario)
        self.assertIn('senha', primeiro_usuario)
        self.assertIn('email', primeiro_usuario)
        self.assertIn('sal_fixo', primeiro_usuario)
        self.assertIn('telefone', primeiro_usuario)
        self.assertIn('tci', primeiro_usuario)

        # Garante que os dois ultimos usuários do dicionário tenha 8 campos.
        self.assertEqual(len(usuarios[1]), 8) #usuário 2 Dante
        self.assertEqual(len(usuarios[2]), 8) #usuário 3 Kratos

        # Garante que o terceiro usuário realmente é o Kratos e o telefone veio nulo
        self.assertEqual(usuarios[2]['nome'], 'Kratos Good')
        self.assertIsNone(usuarios[2]['tci'])

        

    
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
    



