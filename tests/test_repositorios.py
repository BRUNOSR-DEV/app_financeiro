
# ---------------------------------- IMPORTAÇÃO - MÓDULOS LOCAIS ------------------------------------

# ----- BANCO DE DADOS (models) ------

from tests.config.database_teste import Database_teste
from models.repositorios import Rep_Usuario, Rep_Receita, Rep_Despesa, Rep_Cartao_credito, Rep_Assinatura
from models.entidades import *
from tests.config.db_tabelas_teste import inicializar_banco_completo

# ----- FUNÇÕES DE AJUDA - (UTILS) -------
from utils.segurança import SegurancaService

# ------------------------------ IMPORTAÇÃO - MÓDULOS BIBLIOTECAS ---------------------------------
# BIBLIO PADRÕES
from datetime import date

#BIBLIO VIA PIP
import MySQLdb
import unittest


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
            cursor.execute("DELETE FROM receitas")
            cursor.execute("DELETE FROM despesas")
            cursor.execute("DELETE FROM cartoes_credito")
            cursor.execute("DELETE FROM assinaturas")
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
        
        
        print("\n==================================================")
        print("   INICIANDO SUÍTE DE TESTES: REPOSITÓRIO USUÁRIO")
        print("==================================================")

        inicializar_banco_completo(cls.conn)


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
#       @@Classe Testada
    

class Test_Rep_Receita(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Prepara a infraestrutura e a conexão uma única vez para esta classe."""

        cls.db_infra = Database_teste()
        cls.conn = cls.db_infra.conectar_bd_teste()

        print("\n==================================================")
        print("   INICIANDO SUÍTE DE TESTES: REPOSITÓRIO RECEITA")
        print("==================================================")

        inicializar_banco_completo(cls.conn)

    @classmethod
    def tearDownClass(cls):
        """Desconecta do banco após rodar todos os testes desta entidade."""
        if hasattr(cls, 'conn') and cls.conn:
            cls.db_infra.desconectar(cls.conn)
        
        print("\n==================================================")
        print("   SUÍTE FINALIZADA: REPOSITÓRIO RECEITA")
        print("==================================================")

    def setUp(self):
        """Roda ANTES de cada método de teste individual."""

        self.rep = Rep_Receita()

        # Limpa as tabelas do banco
        limpar_tabelas(conn=self.conn)
        print(f"\n-> Rodando: {self._testMethodName}")

        self.user1 = Usuario('Bruno Rodrigues', 'bruno', '1234', 'bruno@gmail.com', 2000, '11985652500', None)
        self.user2 = Usuario('Dante Sparta', 'dante', '1234', 'dante@gmail.com', 10000, '11985652500', None)
        self.user3 = Usuario('Kratos Good', 'kratos', '1234', 'kratos@gmail.com', 12000, '11985652500', None)

        self.receita1 = Receita('Tigrinho', 250, 'Ganhos em bet', date(2026, 6, 25))
        self.receita2 = Receita('Presente', 150, 'presente de aniversário', date(2026, 6, 27))

    def tearDown(self):
        """Roda DEPOIS de cada método de teste individual."""

        print(f"-> Finalizado: {self._testMethodName}")
    

                                 # --------- INICIANDO TESTES ---------
                                 
    def test_inserir_receita_dados_receitas(self):
        """Garante que o usuário consiga inserir uma nova receita no banco, já verifica se o método de listagem retorna a receita inserida"""

        user_id = Rep_Usuario().inserir_usuario(usuario=self.user2, conn=self.conn)

        self.assertTrue(self.rep.inserir_receita(id_user=user_id, receita=self.receita1, conn=self.conn)) # inseri receita1 já testando

        id_rec2 = self.rep.inserir_receita(id_user=user_id, receita=self.receita2, conn=self.conn) # inseri receita2

        receitas = self.rep.dados_receitas(user_id, conn=self.conn)

        self.assertEqual(receitas[1]['fonte'], 'Presente')
        self.assertEqual(receitas[1]['valor'], Decimal(150))
        self.assertEqual(receitas[1]['descricao'], 'presente de aniversário')
        self.assertEqual(receitas[1]['data'], date(2026, 6, 27))
        self.assertEqual(receitas[1]['id_receita'], id_rec2)
    

    def test_atualizar_receita(self):
        """Garante que o método atualizar_receita faça a atualização dos valores"""

        user_id = Rep_Usuario().inserir_usuario(usuario=self.user2, conn=self.conn)
        
        id_rec2 = self.rep.inserir_receita(id_user=user_id, receita=self.receita2, conn=self.conn)

        receitas = self.rep.dados_receitas(user_id, conn=self.conn) # Returns: List[Dict[str, any]]

        # Alteração dos valores no dionário
        receitas[0]['fonte'] = 'Presente brabo'
        receitas[0]['valor'] = Decimal(200)

        #Montando a entidade com o dicionário alterado
        ent_receita = Receita(receitas[0]['fonte'], receitas[0]['valor'], receitas[0]['descricao'], receitas[0]['data'], id_rec2)

        #Verificação: O teste precisa retorna True, caso atualize com sucesso
        self.assertTrue(self.rep.atualizar_receita(receita=ent_receita, conn=self.conn))

        receitas_att = self.rep.dados_receitas(user_id, conn=self.conn)

        #Verifica se os valores alterados estão no banco
        self.assertEqual(receitas_att[0]['fonte'], 'Presente brabo', 'Atualização não foi feita')
        self.assertEqual(receitas_att[0]['valor'], Decimal(200), 'Atualização não foi feita')

    
    def test_deletar_receita(self):
        '''Garante que o método deletar_receita faça o delete da receita com o id passado'''

        user_id = Rep_Usuario().inserir_usuario(usuario=self.user2, conn=self.conn)
        
        id_rec2 = self.rep.inserir_receita(id_user=user_id, receita=self.receita2, conn=self.conn)

        # Verifica se o valor está lá antes de deletar
        self.assertEqual(len(self.rep.dados_receitas(user_id, conn=self.conn)), 1)

        # Faz o delete, aguardando True caso ele seja realizado
        self.assertTrue(self.rep.deletar_receita(id_rec2, conn=self.conn), 'O delete não foi realizado')

        # verifica se a listagem voltou vazia após o delete
        self.assertEqual(len(self.rep.dados_receitas(user_id, conn=self.conn)), 0)
#       @@Classe Testada


class Test_Rep_Despesa(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Prepara a infraestrutura e a conexão uma única vez para esta classe."""

        cls.db_infra = Database_teste()
        cls.conn = cls.db_infra.conectar_bd_teste()

        print("\n==================================================")
        print("   INICIANDO SUÍTE DE TESTES: REPOSITÓRIO DESPESA")
        print("==================================================")

        inicializar_banco_completo(cls.conn)

    @classmethod
    def tearDownClass(cls):
        """Desconecta do banco após rodar todos os testes desta entidade."""

        if hasattr(cls, 'conn') and cls.conn:
            cls.db_infra.desconectar(cls.conn)
        
        print("\n==================================================")
        print("   SUÍTE FINALIZADA: REPOSITÓRIO DESPESA")
        print("==================================================")

    def setUp(self):
        """Roda ANTES de cada método de teste individual."""

        self.rep = Rep_Despesa()

        # Limpa as tabelas do banco
        limpar_tabelas(conn=self.conn)
        print(f"\n-> Rodando: {self._testMethodName}")

        self.user1 = Usuario('Bruno Rodrigues', 'bruno', '1234', 'bruno@gmail.com', 2000, '11985652500', None)
        self.user2 = Usuario('Dante Sparta', 'dante', '1234', 'dante@gmail.com', 10000, '11985652500', None)
        self.user3 = Usuario('Kratos Good', 'kratos', '1234', 'kratos@gmail.com', 12000, '11985652500', None)

        #Objeto cartão
        card_click = Cartao_credito('Click', 8000, 18, 24, 'MasterCard', 'Laranja')

        self.user_id = Rep_Usuario().inserir_usuario(usuario=self.user1, conn=self.conn)
        self.cc_id = Rep_Cartao_credito().inserir_cc(self.user_id, cartao=card_click, conn=self.conn)

        # com cartão
        self.materia = Despesa('Fazenda', 385, 2, 'Matérias da boa', 'Lazer', date(2026, 6, 25), None, None, self.cc_id)

        #alvulsa
        self.emprestimo = Despesa('Banco', 3000, 10, 'Emprestimo no banco', 'Contas', date(2026, 6, 28), date(2026,7,15), 15, None)


    def tearDown(self):
        """Roda DEPOIS de cada método de teste individual."""

        print(f"-> Finalizado: {self._testMethodName}")


    def test_inserir_despesas(self):
        """Garante que o método faça a inserção dos dados recebidos"""

        id_desp = self.rep.inserir_despesa(self.user_id, self.materia, conn=self.conn)

        self.assertNotEqual(id_desp, 0)


    def test_dados_despesas_avulsas_cartao(self):
        """Garante que os métodos de listagem traga os dados inseridos corretamente"""

        id_desp = self.rep.inserir_despesa(self.user_id, self.materia, conn=self.conn)
        id_desp2 = self.rep.inserir_despesa(self.user_id, self.emprestimo, conn=self.conn)

        self.assertIsNotNone(id_desp, 'Método do banco retornou None')
        self.assertIsNotNone(id_desp2, 'Método do banco retornou None')

        despesas = self.rep.dados_despesas(self.user_id, conn=self.conn)
        
        # Verifica a primeira despesa inserida
        self.assertEqual(despesas[0]['local'], 'Fazenda', 'O valor do local não corresponde!')

        # Verifica a segunda despesa inserida
        self.assertEqual(despesas[1]['descricao'], 'Emprestimo no banco', "O valor em 'descricao' não corresponde")

        #Verifica se os métodos joins retorna os valores corretos
        avulsas = self.rep.pega_despesas_avulsas(self.user_id, conn=self.conn)
        cartao = self.rep.pega_despesas_cartao(self.user_id, self.cc_id, conn=self.conn)

        
        self.assertEqual(avulsas[0]['data_pp'], date(2026,7,15), 'Datas comparadas não correspondem') 

        self.assertEqual(cartao[0]['local'], 'Fazenda')
        self.assertEqual(cartao[0]['nome_cartao'], 'Click') # Cartão inserido no setUp


    def test_atualizar_despesa_deletar_despesa(self):

        """Garante que o método de updade faça a atualização corretamente"""

        id_desp = self.rep.inserir_despesa(self.user_id, self.materia, conn=self.conn)

        #passa o id da despesa inserida para o objeto
        self.materia.id_desp = id_desp

        #altera os valores
        self.materia.local = 'Fazenda Tegridade'
        self.materia.categoria = 'Hobby'

        #Verifiva se o método retorna True
        self.assertTrue(self.rep.atualizar_despesa(self.materia, self.conn))

        #Verifica se os dados foram atualizados com sucesso
        despesas = self.rep.dados_despesas(self.user_id, conn=self.conn)

        self.assertEqual(despesas[0]['local'], 'Fazenda Tegridade')

        self.assertEqual(despesas[0]['categoria'], 'Hobby')

        #Verifica se o método de delete retorna True e se dados_despesas retorna 0
        self.assertTrue(self.rep.deletar_despesa(id_desp, conn=self.conn))

        self.assertEqual(len(self.rep.dados_despesas(self.user_id, conn=self.conn)), 0)

        #devolve os valores do objeto
        self.materia.local = 'Fazenda'
        self.materia.categoria = 'Lazer'
#       @@Classe Testada


class Test_Rep_Cartao_credito(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Prepara a infraestrutura e a conexão uma única vez para esta classe."""

        cls.db_infra = Database_teste()
        cls.conn = cls.db_infra.conectar_bd_teste()

        print("\n==================================================")
        print("   INICIANDO SUÍTE DE TESTES: REPOSITÓRIO CARTAO_CREDITO")
        print("==================================================")

        inicializar_banco_completo(cls.conn)

    @classmethod
    def tearDownClass(cls):
        """Desconecta do banco após rodar todos os testes desta entidade."""
        
        if hasattr(cls, 'conn') and cls.conn:
            cls.db_infra.desconectar(cls.conn)
        
        print("\n==================================================")
        print("   SUÍTE FINALIZADA: REPOSITÓRIO CARTAO_CREDITO ")
        print("==================================================")

    def setUp(self):
        """Roda ANTES de cada método de teste individual."""

        self.rep = Rep_Cartao_credito()

        # Limpa as tabelas do banco
        limpar_tabelas(conn=self.conn)
        print(f"\n-> Rodando: {self._testMethodName}")

        self.user1 = Usuario('Bruno Rodrigues', 'bruno', '1234', 'bruno@gmail.com', 2000, '11985652500', None)
        self.user2 = Usuario('Dante Sparta', 'dante', '1234', 'dante@gmail.com', 10000, '11985652500', None)
        self.user3 = Usuario('Kratos Good', 'kratos', '1234', 'kratos@gmail.com', 12000, '11985652500', None)

        #Objetos cartões
        self.card_click = Cartao_credito('Click', 8000, 18, 24, 'MasterCard', 'Preto')
        self.card_inter = Cartao_credito('Inter', 10000, 6, 12, 'Visa', 'Laranja')

        #inserindo um usuário
        self.user_id = Rep_Usuario().inserir_usuario(usuario=self.user1, conn=self.conn)
        


    def tearDown(self):
        """Roda DEPOIS de cada método de teste individual."""

        print(f"-> Finalizado: {self._testMethodName}")
    

    def test_inserir_cartao_dados_cartoes(self):
        """Garante que o método de inserção de cartão esteja funcionando"""

        # Verifica se tem o retorno do id 
        self.assertIsNotNone(self.rep.inserir_cc(self.user_id, self.card_inter, conn=self.conn))
        self.rep.inserir_cc(self.user_id, self.card_click, conn=self.conn) # inserindo o segundo cartão

        #monta a variável que terá a lista de dicts
        cards = self.rep.dados_cartoes(self.user_id, conn=self.conn)

        #Verifica se o retorno de dados_cartaoes é 2
        self.assertEqual(len(cards), 2)

        #Verifica se o nome do objeto inserido retorna corretamente
        self.assertEqual(cards[0]['nome_cartao'], "Inter")
        self.assertEqual(cards[1]['bandeira'], "MasterCard")


    def test_atualizar_deletar_cartao(self):
        """Garante que os métodos de atuaçização e delete estejam funcionando"""

        id_click = self.rep.inserir_cc(self.user_id, self.card_click, conn=self.conn)
        id_inter = self.rep.inserir_cc(self.user_id, self.card_inter, conn=self.conn)

        self.card_inter.id_cartao = id_inter

        self.card_inter.bandeira = "MasterCard"
        self.card_inter.cor = "Verde"

        #Verifica se o método retorna verdadeiro
        self.assertTrue(self.rep.atualizar_cartao(self.card_inter, conn=self.conn))

        #verifica se tem dois cartões no banco
        cards = self.rep.dados_cartoes(self.user_id, conn=self.conn)
        self.assertEqual(len(cards), 2)

        #Verifica se os dados foram alterados
        self.assertEqual(cards[1]['bandeira'], "MasterCard")
        self.assertEqual(cards[1]['cor'], "Verde")

        #Verifica se o retono é verdadeiro
        self.assertTrue(self.rep.deletar_cartao(id_card=id_click, conn=self.conn))

        #Verifica se o cartão foi apagado
        cards = self.rep.dados_cartoes(self.user_id, conn=self.conn)
        self.assertEqual(len(cards), 1)
#       @@Classe Testada



class Test_Rep_Assinatura(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Prepara a infraestrutura e a conexão uma única vez para esta classe."""

        cls.db_infra = Database_teste()
        cls.conn = cls.db_infra.conectar_bd_teste()

        print("\n==================================================")
        print("   INICIANDO SUÍTE DE TESTES: REPOSITÓRIO ASSINATURA")
        print("==================================================")

        inicializar_banco_completo(cls.conn)

    @classmethod
    def tearDownClass(cls):
        """Desconecta do banco após rodar todos os testes desta entidade."""
        
        if hasattr(cls, 'conn') and cls.conn:
            cls.db_infra.desconectar(cls.conn)
        
        print("\n==================================================")
        print("   SUÍTE FINALIZADA: REPOSITÓRIO ASSINATURA ")
        print("==================================================")


    def setUp(self):
        """Roda ANTES de cada método de teste individual."""

        self.rep = Rep_Assinatura()

        # Limpa as tabelas do banco
        limpar_tabelas(conn=self.conn)
        print(f"\n-> Rodando: {self._testMethodName}")

        self.user1 = Usuario('Bruno Rodrigues', 'bruno', '1234', 'bruno@gmail.com', 2000, '11985652500', None)
        self.user2 = Usuario('Dante Sparta', 'dante', '1234', 'dante@gmail.com', 10000, '11985652500', None)
        self.user3 = Usuario('Kratos Good', 'kratos', '1234', 'kratos@gmail.com', 12000, '11985652500', None)

        #Objeto cartão
        card_click = Cartao_credito('Click', 8000, 18, 24, 'MasterCard', 'Laranja')

        self.user_id = Rep_Usuario().inserir_usuario(usuario=self.user1, conn=self.conn)
        self.cc_id = Rep_Cartao_credito().inserir_cc(self.user_id, cartao=card_click, conn=self.conn)

        self.netflix = Assinatura('Netflix', 42.50, 'Streaming para casa', 'Streaming', date(2026,7,1), None, None, self.cc_id)


    def tearDown(self):
        """Roda DEPOIS de cada método de teste individual."""

        print(f"-> Finalizado: {self._testMethodName}")
    


    def test_inserir_assinaturas_dados_assinaturas(self):
        """Garante que o método retorne o id do objeto inserido no banco"""

        #Verifica se o método inseri o objeto
        self.assertIsNotNone(self.rep.inserir_assinatura(self.user_id, self.netflix, conn=self.conn))

        #Chama o método de listagem e passa o retono para a variável 'ass'
        ass = self.rep.dados_assinaturas(self.user_id, self.conn)

        #Verifica se o tamanho da lista é de 1
        self.assertEqual(len(ass), 1, 'O método não retono uma lista com dicionários')

        #Verifica se o dicionário dentro da lista tem o valor insiro
        self.assertEqual(ass[0]['nome'], 'Netflix')
        self.assertEqual(ass[0]['data_aquisicao'], date(2026,7,1))


    def test_pega_assinatura_cartao_avulsa(self):
        """Garante que os métodos de listagem especializada retorne os valores corretos que foram inseridos"""

        #objeto avulso
        jornal = Assinatura('Jornal da Vila', 12.50, 'Jornal entregue por moradores', 'Informação', date(2026,6,20), date(2026,7,5), 5, None)

        #Inseri objetos no banco
        self.rep.inserir_assinatura(self.user_id, self.netflix, self.conn) # objeto inserido   COM cartão
        self.rep.inserir_assinatura(self.user_id, jornal, self.conn) # objeto inserido SEM cartão

        ass_cartao = self.rep.pega_assinaturas_cartao(self.user_id, self.cc_id, self.conn)
        ass_avulsas = self.rep.pega_assinaturas_avulsas(self.user_id, self.conn)

        # Verifica se os métodos retona o valor esperado (List[Dict[str, any]])
        self.assertIsNotNone(ass_avulsas, 'O método não retornou a lista com o dicionário esperado')
        self.assertIsNotNone(ass_cartao, 'O método não retornou a lista com o dicionário esperado')


        #Verifica se os valores inseridos estão no banco
        self.assertEqual(ass_cartao[0]['categoria'], 'Streaming')

        self.assertEqual(ass_avulsas[0]['nome'], 'Jornal da Vila')
        self.assertEqual(ass_avulsas[0]['id_cc'], None)


    def test_atualiza_assinatura_deleta_assinatura(self):
        '''Garante que o método atualize e delete assinaturas passando o id da mesma'''

        #objeto avulso
        jornal = Assinatura('Jornal da Vila', 12.50, 'Jornal entregue por moradores', 'Informação', date(2026,6,20), date(2026,7,5), 5, None)

        #Inseri objetos no banco
        id_net = self.rep.inserir_assinatura(self.user_id, self.netflix, self.conn) # objeto inserido   COM cartão
        id_jornal = self.rep.inserir_assinatura(self.user_id, jornal, self.conn) # objeto inserido SEM cartão

        #Verifica se os valores estão no banco
        self.assertEqual(len(self.rep.dados_assinaturas(self.user_id, self.conn)), 2)

        #Passa o id da assinatura para o objeto
        jornal.id_ass = id_jornal

        #Atualização de valores
        jornal.categoria = 'Estudo'
        jornal.data_pp = date(2026,7,10)

        #Verifica se o método de update retorna True
        self.assertTrue(self.rep.atualizar_assinatura(assinatura=jornal, conn=self.conn))

        #Verifica se o método delete retorna True
        self.assertTrue(self.rep.deletar_assinatura(id_ass=id_net, conn=self.conn))

        #Verifica se os valores foram mudados e o um objeto apagado
        ass = self.rep.dados_assinaturas(self.user_id, self.conn)

        self.assertEqual(len(ass), 1)

        self.assertEqual(ass[0]['categoria'], 'Estudo')
        self.assertEqual(ass[0]['data_pp'], date(2026,7,10))





