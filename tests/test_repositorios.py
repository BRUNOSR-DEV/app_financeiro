

import MySQLdb
import unittest
from tests.config.database_teste import Database_teste
from models.repositorios import Rep_Usuario, Rep_Receita, Rep_Despesa, Rep_Cartao_credito, Rep_Assinatura
from models.entidades import *
from utils.segurança import SegurancaService


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
            cursor.execute("DELETE FROM usuarios")
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
        cls.db_infra = Database_teste()
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

        self.user1 = Usuario('Bruno Rodrigues', 'bruno', '1234', 'bruno@gmail.com', 2000, '11985652500', None)
        self.user2 = Usuario('Dante Sparta', 'dante', '1234', 'dante@gmail.com', 10000, '11985652500', None)
        self.user3 = Usuario('Kratos Good', 'kratos', '1234', 'kratos@gmail.com', 12000, '11985652500', None)


    def tearDown(self):
        """Roda DEPOIS de cada método de teste individual."""
        print(f"-> Finalizado: {self._testMethodName}")


                                    # --------- INICIANDO TESTES ---------

    def test_validar_credenciais_usuario_inexistente(self):
        """Garante que retorna None se o usuário não existir"""
        resultado = self.rep.validar_credenciais(username='usuario_fantasma', senha_digitada='4321', conn=self.conn)
        self.assertIsNone(resultado)


    def test_validar_credenciais_bcrypt_sucesso(self):
        """Garante login com sucesso para usuário que já usa Bcrypt"""
        # Cria uma senha já criptografada usando o seu serviço
        senha_hash = SegurancaService.criptografar_senha("kratos123")
    
        # Prepara a entidade com o hash e insere no banco
        user_cripto = Usuario('Kratos Good', 'kratos', senha_hash, 'kratos@gmail.com', 12000, '11985652500', None ) 
        self.rep.inserir_usuario(usuario=user_cripto, conn=self.conn)

        # Executa o login com a senha EM TEXTO PURO
        resultado = self.rep.validar_credenciais('kratos', 'kratos123', conn=self.conn)

        # Verifica se o retorno não é None e o usuário conseguiu fazer login
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado[0]['nome_user'], 'kratos')



    def test_validar_credenciais_bcrypt_senha_errada(self):
        """Garante que retorna None se a senha digitada estiver incorreta"""

        senha_hash = SegurancaService.criptografar_senha("senha_certa")
        user = Usuario('Dante', 'dante', senha_hash, 'dante@gmail.com', 10000, '11985652500', None)

        self.rep.inserir_usuario(user, conn=self.conn)

        # Tenta logar com "senha_errada"
        resultado = self.rep.validar_credenciais('dante_devil', 'senha_errada', conn=self.conn)
        self.assertIsNone(resultado)
    


    def test_validar_credenciais_migracao_automatica(self):
        """Garante que senhas legadas (texto puro) são migradas para Bcrypt no primeiro login"""

        # Arrange: Insere com senha em TEXTO PURO de propósito
        user_legado = Usuario('Bruno Old', 'bruno_old', 'senha_pura_123', 'bruno@gmail.com', 2000, '11985652500', None)

        self.rep.inserir_usuario(user_legado, conn=self.conn)
    
        # Act: Faz o login (Isso deve disparar a migração interna)
        resultado_login = self.rep.validar_credenciais('bruno_old', 'senha_pura_123', conn=self.conn)
    
        # Assert: O login funcionou?
        self.assertIsNotNone(resultado_login)
    
        # Assert de Integração: Vai no banco buscar a senha atualizada para ver se virou Bcrypt
        user_id = self.rep.pega_id('bruno_old', conn=self.conn)
        usuario_atualizado = self.rep.pega_usuario(user_id, conn=self.conn)
        senha_no_banco_agora = usuario_atualizado[0]['senha']
    
        # Verifica se o método alterou a senha no banco para um padrão Bcrypt ($2b$ ou $2a$)
        self.assertTrue(
            senha_no_banco_agora.startswith('$2b$') or senha_no_banco_agora.startswith('$2a$'),
            f"A senha no banco deveria ter sido migrada para Bcrypt, mas continuou: {senha_no_banco_agora}"
        )


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
        self.assertEqual(usuario[0]['id_user'], user_id)
        self.assertEqual(usuario[0]['nome_completo'], self.user1.nome_completo)
        self.assertEqual(usuario[0]['nome_user'], self.user1.nome_user)
        self.assertEqual(usuario[0]['senha'], self.user1.senha)
        self.assertEqual(usuario[0]['sal_fixo'], self.user1.sal_fixo)
        self.assertEqual(usuario[0]['email'], self.user1.email)
        self.assertEqual(usuario[0]['telefone'], self.user1.telefone)
        self.assertEqual(usuario[0]['tci'], self.user1.tci)



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
        self.assertEqual(usuarios[2]['nome_completo'], 'Kratos Good')
        self.assertIsNone(usuarios[2]['tci'])


    def test_atualizar_renda(self):
        """ Garante que o método de atualização retorne True e valide o dado atualizado no banco"""

        #Inserindo o usuário e pegando o id no mesmo
        user_id = self.rep.inserir_usuario(usuario=self.user1, conn=self.conn)

        #Verifica se o retorno da atualização é True
        self.assertTrue(self.rep.atualizar_renda(id_user=user_id, nova_renda=4500, conn=self.conn))
        
        #Buscamos a lista de dados do usuário inserido
        user1 = self.rep.pega_usuario(id_user=user_id, conn=self.conn)

        self.assertEqual(user1[0]['sal_fixo'], 4500) #4500 sendo a nova renda do usuário


    def test_atualizar_senha_usuario(self):
        """Garante que o método de atualização se senha retorne True e valide o dado atualizado no banco"""

        user_id = self.rep.inserir_usuario(self.user1, self.conn)

        user1 = self.rep.pega_usuario(user_id, conn=self.conn)

        # Verifica se a senha foi alterada no banco
        self.assertTrue(
            self.rep.atualizar_senha_usuario(user_id=user_id, nova_senha='1111', conn=self.conn), 
            f'A senha do usuário deveria ter sido alterada, mas continua {user1[0]['senha']}'
            )
        
        user1_atualizado = self.rep.pega_usuario(user_id, conn=self.conn)
        
        self.assertEqual(user1_atualizado[0]['senha'], '1111') # '1111' sendo a nova senha do usuário


    


