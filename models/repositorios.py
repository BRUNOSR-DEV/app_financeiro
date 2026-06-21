"""
Módulo de Repositórios (Camada de Persistência)

Este módulo é responsável por abstrair todas as operações de banco de dados (CRUD) 
do sistema financeiro. Cada classe gerencia uma entidade específica, garantindo 
segurança nas transações, tratamento de exceções (Rollbacks) e injeção de dependência 
da conexão com o banco.
"""

# ---------------------------------- IMPORTAÇÃO - MÓDULOS LOCAIS ------------------------------------

# ----- BANCO DE DADOS (models) ------
import MySQLdb
from models.database import Database
from models.entidades import *

# ----- FUNÇÕES DE AJUDA - (UTILS) -------
from utils.segurança import SegurancaService

# ------------------------------ IMPORTAÇÃO - MÓDULOS BIBLIOTECAS ---------------------------------
# BIBLIO PADRÕES
from decimal import Decimal
from typing import Optional, List, Dict, Any, Union


# =================================================================================
# --- REPOSITÓRIO USUÁRIO ---
# =================================================================================

class Rep_Usuario:
    """
    Gerencia as operações de persistência e validação da entidade Usuario.
    
    Attributes:
        db_conn (Database): Instância da classe de gerenciamento do banco de dados.
    """
    
    def __init__(self, db_conn: Database = None) -> None:
        self.db_conn: Database = db_conn
    
    def validar_credenciais(self, username: str, senha_digitada: str) -> Optional[List[Dict[str, Any]]]:
        """
        Valida o login do usuário, realizando a migração automática de senhas antigas 
        (texto puro) para hashes Bcrypt, se necessário.

        Args:
            username (str): O nome de usuário (login).
            senha_digitada (str): A senha em texto puro informada na UI.

        Returns:
            Optional[List[Dict[str, Any]]]: Uma lista contendo o dicionário do usuário se 
            autorizado, ou None se as credenciais forem inválidas.
        """

        user_id = self.pega_id(username)
        usuario = self.pega_usuario(user_id) 
        
        if not user_id:
            return None 
            
        senha_salva = usuario[0]['senha'] 

        if senha_salva.startswith('$2b$') or senha_salva.startswith('$2a$'):
            if SegurancaService.verificar_senha(senha_digitada, senha_salva):
                return usuario
            return None
        
        else:
            # Fluxo de migração de senha legado para Bcrypt
            if senha_digitada == senha_salva:
                nova_senha_cripto = SegurancaService.criptografar_senha(senha_digitada)
                self.atualizar_senha_usuario(user_id, nova_senha_cripto)
                
                print(f"🔒 Usuário {usuario[0]['nome_user']} migrado com sucesso para criptografia avançada!")
                return usuario
            return None


    def dados_usuarios(self, conn: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Retorna uma lista com os dados de todos os usuários do sistema.

        Args:
            conn (Optional[Any]): Conexão injetada (opcional). Se None, cria uma própria.

        Returns:
            List[Dict[str, Any]]: Lista de dicionários mapeados pela Entidade Usuario.

        Raises:
            MySQLdb.Error: Se houver falha na query SQL.
        """
        gerenciar_conn = False

        if conn is None:
            conn= self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()

        try:
            cursor.execute('SELECT nome_completo, nome_usuario, senha, email, salario_fixo, numero_telefone, telegram_chat_id, id FROM usuarios')
            usuarios = cursor.fetchall()

            if usuarios:
                objetos = [Usuario(*user) for user in usuarios]
                return [obj.to_dict() for obj in objetos]
            else:
                return []
        
        except MySQLdb.Error as e: 
            print(f'Erro no MySQL ao pegar dados: {e}')
            raise 

        except Exception as e:
            print(f'Erro inesperado ao pegar usuários: {e}')

        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def pega_usuario(self, id_user: int, conn: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Busca os dados de um usuário específico pelo ID.

        Args:
            id_user (int): ID da chave primária do usuário.
            conn (Optional[Any]): Conexão de banco de dados opcional.

        Returns:
            List[Dict[str, Any]]: Dicionário do usuário mapeado, ou lista vazia.
        """
        gerenciar_conn = False

        if conn is None:
            conn= self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()

        try:
            sql = "SELECT nome_completo, nome_usuario, senha, email, salario_fixo, numero_telefone, telegram_chat_id, id FROM usuarios WHERE id= %s"
            cursor.execute(sql, (id_user, ))
            usuario = cursor.fetchall()

            if usuario:
                objeto = [Usuario(*user) for user in usuario]
                return [obj.to_dict() for obj in objeto]
        
        except MySQLdb.Error as e: 
            print(f'Erro no MySQL ao buscar dados do usuário: {e}')
            raise 

        except Exception as e:
            print(f'Erro inesperado ao buscar dados do usuário: {e}')

        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def pega_id(self, usuario: str, conn: Optional[Any] = None) -> Optional[int]: 
        """
        Busca o ID interno (PK) do usuário utilizando o seu nome de usuário (login).

        Args:
            usuario (str): Nome do usuário no sistema.
            conn (Optional[Any]): Conexão com o banco de dados.

        Returns:
            Optional[int]: O ID do usuário, ou None se não for encontrado.
        """
        gerenciar_conn = False

        if conn is None:
            conn= self.db_conn.conectar_bd_original()
            gerenciar_conn= True

        cursor = conn.cursor() 

        try:
            sql = "SELECT id FROM usuarios WHERE nome_usuario = %s" 
            cursor.execute(sql, (usuario,)) 
            result = cursor.fetchone()
        
            if result:
                return result[0]
        
        except MySQLdb.Error as e:
            print(f"Erro MySQL ao pegar ID: {e}")
            return None 
        except Exception as e:
            print(f"Erro inesperado ao pegar ID: {e}")

        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def inserir_usuario(self, usuario: Usuario, conn: Optional[Any] = None) -> bool:
        """
        Insere um novo registro de usuário no banco de dados.

        Args:
            usuario (Usuario): Objeto Entidade contendo os dados a serem salvos.
            conn (Optional[Any]): Conexão com o banco de dados.

        Returns:
            bool: True se o INSERT foi bem-sucedido, False caso contrário.
        """  
        gerenciar_conn = False

        if conn is None:
            conn= self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
        sucesso = False

        try:
            cursor.execute("INSERT INTO usuarios (nome_completo, nome_usuario, senha, email, salario_fixo, numero_telefone, telegram_chat_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",(usuario.nome_completo, usuario.nome_user, usuario.senha, usuario.email, usuario.sal_fixo, usuario.telefone, usuario.tci))
            conn.commit()

            if cursor.rowcount == 1: 
                print(f'Usuário inserido com sucesso! olá {usuario.nome_completo}')
                sucesso = True
                return sucesso 
            else:
                print('Não foi possível inserir usuário no banco de dados! ')
                sucesso = False
                return sucesso
        
        except MySQLdb.Error as e:
            print(f'Erro MySQL ao inserir usuário: {e}')
            conn.rollback()
            return False     
    
        except Exception as e:
            print(f'Erro em inserir usuário {e}')
            conn.rollback()
            return False
        
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def atualizar_renda(self, id_user: int, nova_renda: Decimal, conn: Optional[Any] = None) -> bool: 
        """
        Atualiza o salário fixo base de um usuário específico.

        Args:
            id_user (int): ID do usuário a ser atualizado.
            nova_renda (Decimal): Novo valor de salário fixo.
            conn (Optional[Any]): Conexão opcional.

        Returns:
            bool: True em caso de sucesso, False em caso de falha.
        """
        gerenciar_conn = False
        if conn is None:
            conn= self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
    
        try:
            sql = "UPDATE usuarios SET salario_fixo = %s WHERE id = %s"
            cursor.execute(sql, (nova_renda, id_user))
            conn.commit()

            print(f"Renda fixa do usuário ID: {id_user} atualizada com sucesso!")
            return True
    
        except MySQLdb.Error as e:
            print(f"Erro MySQL ao fazer atualização: {e}")
            conn.rollback()
            return False
    
        except Exception as e:
            print(f"Erro inesperado ao atualizar renda fixa: {e}")
            conn.rollback()
            return False
        
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def atualizar_senha_usuario(self, user_id: int, nova_senha: str, conn: Optional[Any] = None) -> Optional[bool]:
        """
        Atualiza o hash de senha do usuário no banco de dados.

        Args:
            user_id (int): ID do usuário alvo.
            nova_senha (str): Hash gerado via Bcrypt.
            conn (Optional[Any]): Conexão opcional.

        Returns:
            Optional[bool]: True se sucesso, None em caso de falha de DB.
        """
        gerenciar_conn = False
        if conn is None:
            conn= self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
    
        try:
            sql = "UPDATE usuarios SET senha = %s WHERE id = %s"
            cursor.execute(sql, (nova_senha, user_id))
            conn.commit()

            print(f"Senha do usuário ID: {user_id} atualizada com sucesso!")
            return True
    
        except MySQLdb.Error as e:
            print(f"Erro MySQL ao fazer atualização: {e}")
            conn.rollback()
            return None 
    
        except Exception as e:
            print(f"Erro inesperado ao atualizar senha: {e}")
            conn.rollback()
            return None
        
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)
                                         

# =================================================================================
# --- REPOSITÓRIO RECEITA ---
# =================================================================================

class Rep_Receita:
    """
    Gerencia as operações de persistência relacionadas às Entidades de Receita.
    """

    def __init__(self, db_conn: Database) -> None:
        self.db_conn: Database = db_conn
    
    def dados_receitas(self, id_user: int, conn: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Busca e retorna todas as receitas atreladas a um usuário específico.

        Args:
            id_user (int): ID do usuário dono das receitas.
            conn (Optional[Any]): Conexão com o banco.

        Returns:
            List[Dict[str, Any]]: Lista de dicionários populados pela entidade Receita.
        """
        gerenciar_conn = False

        if conn is None:
            conn= self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()

        try:
            query = "SELECT fonte, valor, descricao, data_recebimento, id FROM receitas WHERE id_usuario= %s"
            cursor.execute(query, (id_user, ))
            receitas = cursor.fetchall()

            if receitas:
                objetos = [Receita(*rec) for rec in receitas]
                return [obj.to_dict() for obj in objetos]
            else:
                return []
        
        except MySQLdb.Error as e: 
            print(f'Erro no MySQL ao buscar dados de receitas: {e}')
            raise 

        except Exception as e:
            print(f'Erro inesperado ao buscar dados de receitas: {e}')
            return []

        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def inserir_receita(self, id_user: int, receita: Receita, conn: Optional[Any] = None) -> Optional[int]:
        """
        Insere uma nova receita no banco de dados e retorna seu identificador único.

        Args:
            id_user (int): ID do usuário associado à receita.
            receita (Receita): Objeto do domínio contendo os dados a serem salvos.
            conn (Optional[Any]): Conexão com o banco.

        Returns:
            Optional[int]: O ID gerado para a nova receita, ou None em caso de falha.
        """
        gerenciar_conn = False

        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
        try:
            sql = "INSERT INTO receitas (fonte, valor, descricao, data_recebimento, id_usuario) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (receita.fonte, receita.valor, receita.descricao, receita.data, id_user))
            conn.commit()
            return cursor.lastrowid 
    
        except MySQLdb.Error as e: 
            print(f"Erro MySQL ao inserir receita: {e}")
            conn.rollback()
            return None 
    
        except Exception as e:
            print(f"Erro inesperado ao inserir receita: {e}")
            conn.rollback()
            return None
        
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def atualizar_receita(self, receita: Receita, conn: Optional[Any] = None) -> Optional[bool]:
        """
        Atualiza uma receita existente utilizando o ID embutido no objeto.

        Args:
            receita (Receita): Objeto Entidade com as alterações e o id_receita preenchido.
            conn (Optional[Any]): Conexão opcional.

        Returns:
            Optional[bool]: True se sucesso, None em caso de erro no SQL.
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
    
        try:
            sql = "UPDATE receitas SET fonte = %s, valor = %s, descricao = %s, data_recebimento = %s WHERE id = %s"
            cursor.execute(sql, (receita.fonte, receita.valor, receita.descricao, receita.data, receita.id_receita))
            conn.commit()

            print(f"Receita com ID {receita.id_receita} atualizada com sucesso!")
            return True
    
        except MySQLdb.Error as e: 
            print(f"Erro MySQL ao fazer atualização: {e}")
            conn.rollback()
            return None 
    
        except Exception as e:
            print(f"Erro inesperado ao atualizar receita: {e}")
            conn.rollback()
            return None
        
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def deletar_receita(self, id_rec: int, conn: Optional[Any] = None) -> bool:
        """
        Remove permanentemente uma receita da base de dados.

        Args:
            id_rec (int): ID da receita a ser deletada.
            conn (Optional[Any]): Conexão opcional.

        Returns:
            bool: True se a deleção for concluída, False em caso de falha.
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
        try:
            sql = "DELETE FROM receitas WHERE id = %s"
            cursor.execute(sql, (id_rec,))
            conn.commit()
            return True
    
        except Exception as e:
            print(f"Erro ao deletar no MySQL: {e}")
            conn.rollback()
            return False
    
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


# =================================================================================
# --- REPOSITÓRIO DESPESA ---
# =================================================================================

class Rep_Despesa:
    """
    Controla as operações de persistência e extração de Despesas, incluindo JOINs 
    complexos com tabelas de cartões de crédito.
    """

    def __init__(self, db_conn: Database) -> None:
        self.db_conn: Database = db_conn

    def dados_despesas(self, id_user: int, conn: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Retorna a relação completa de todas as despesas (avulsas e parceladas) do usuário.

        Args:
            id_user (int): PK do usuário logado.
            conn (Optional[Any]): Conexão injetada (opcional).

        Returns:
            List[Dict[str, Any]]: Dicionários no formato base da Entidade Despesa.
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()

        try:
            query = """
                SELECT 
                    local, 
                    valor_total, 
                    parcelas,
                    descricao,
                    categoria,
                    data_compra,
                    data_primeiro_pagamento,
                    dia_vencimento,
                    id_cartao,
                    id
                FROM despesas 
                WHERE id_usuario = %s
            """
        
            cursor.execute(query, (id_user, ))
            despesas = cursor.fetchall()
        
            if despesas:
                objetos = [Despesa(*desp) for desp in despesas]
                return [obj.to_dict() for obj in objetos]
            else:
                return []

        except Exception as e:
            print(f"Erro ao buscar despesas: {e}")
            return []
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def pega_despesas_cartao(self, id_user: int, id_card: int, conn: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Consulta de DTO: Executa um INNER JOIN para mesclar Despesas com os dados 
        do seu Cartão de Crédito associado.

        Args:
            id_user (int): Identificador do usuário.
            id_card (int): Identificador do cartão de crédito.
            conn (Optional[Any]): Conexão injetada.

        Returns:
            List[Dict[str, Any]]: Lista de dicionários complexos (DespesaDetalhadoDTO).
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()

        try:
            query = """
                SELECT 
                    d.id, 
                    d.local, 
                    d.valor_total, 
                    d.parcelas,
                    d.descricao,
                    d.categoria,
                    d.data_compra,
                    c.nome,
                    c.limite, 
                    c.dia_fechamento, 
                    c.dia_vencimento,
                    c.bandeira,
                    c.cor
                FROM despesas d
                INNER JOIN cartoes_credito c ON d.id_cartao = c.id
                WHERE d.id_usuario = %s AND d.id_cartao = %s
            """
        
            cursor.execute(query, (id_user, id_card))
            resultados = cursor.fetchall()
        
            if resultados:
                objetos = [DespesaDetalhadoDTO(*resul) for resul in resultados]
                return [obj.to_dict()  for obj in objetos]
            else:
                return []

        except Exception as e:
            print(f"Erro ao buscar despesas e cartão (JOIN): {e}")
            return []
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def pega_despesas_avulsas(self, id_user: int, conn: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Isola e retorna apenas despesas vinculadas diretamente à renda fixa 
        (onde a Foreign Key do cartão é Nula).

        Args:
            id_user (int): PK do usuário logado.
            conn (Optional[Any]): Conexão de banco de dados.

        Returns:
            List[Dict[str, Any]]: Dicionários no formato base da Entidade Despesa.
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()

        try:
            query = """
                SELECT 
                    local, 
                    valor_total, 
                    parcelas,
                    descricao,
                    categoria,
                    data_compra,
                    data_primeiro_pagamento,
                    dia_vencimento,
                    id_cartao,
                    id
                FROM despesas 
                WHERE id_usuario = %s AND id_cartao IS NULL
            """
        
            cursor.execute(query, (id_user, ))
            desp_avulsas = cursor.fetchall()

            if desp_avulsas:
                objetos = [Despesa(*desp) for desp in desp_avulsas]
                return [obj.to_dict() for obj in objetos]
            return []

        except Exception as e:
            print(f"Erro ao buscar despesas: {e}")
            return []
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def inserir_despesa(self, id_user: int, despesa: Despesa, conn: Optional[Any] = None) -> Optional[int]:
        """
        Persiste uma nova despesa informada pelo usuário.

        Args:
            id_user (int): FK do usuário dono da despesa.
            despesa (Despesa): Entidade Despesa contendo os valores do formulário.
            conn (Optional[Any]): Conexão opcional.

        Returns:
            Optional[int]: O ID (lastrowid) gerado, ou None em caso de falha.
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
        try:
            sql = "INSERT INTO despesas (local, valor_total, parcelas, descricao, categoria, data_compra, data_primeiro_pagamento, dia_vencimento, id_usuario, id_cartao) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"

            cursor.execute(sql, (despesa.local, despesa.valor_total, despesa.parcelas, despesa.descricao, despesa.categoria, despesa.data_compra, despesa.data_pp, despesa.dia_vencimento, id_user, despesa.id_cc))
            conn.commit()
            return cursor.lastrowid 
    
        except MySQLdb.Error as e: 
            print(f"Erro MySQL ao inserir despesa: {e}")
            conn.rollback()
            return None 
    
        except Exception as e:
            print(f"Erro inesperado ao inserir despesa: {e}")
            conn.rollback()
            return None
        
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def atualizar_despesa(self, despesa: Despesa, conn: Optional[Any] = None) -> bool:
        """
        Atualiza as informações de uma despesa baseada em seu ID.

        Args:
            despesa (Despesa): Entidade atualizada pela interface.
            conn (Optional[Any]): Gerenciamento de conexão flexível.

        Returns:
            bool: Indicador de transação (True = Commit, False = Rollback).
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
    
        try:
            sql = "UPDATE despesas SET local = %s, valor_total= %s, parcelas= %s, descricao= %s, categoria= %s, data_compra= %s, data_primeiro_pagamento= %s, dia_vencimento= %s, id_cartao= %s WHERE id = %s"
            cursor.execute(sql, (despesa.local, despesa.valor_total, despesa.parcelas, despesa.descricao, despesa.categoria, despesa.data_compra, despesa.data_pp, despesa.dia_vencimento, despesa.id_cc, despesa.id_desp))
            conn.commit()

            print(f"Despesa - '{despesa.local}' Atualizado com Sucesso!")
            return True
    
        except MySQLdb.Error as e: 
            print(f"Erro MySQL ao fazer atualização: {e}")
            conn.rollback()
            return False 
    
        except Exception as e:
            print(f"Erro inesperado ao atualizar despesa: {e}")
            conn.rollback()
            return False
        
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def deletar_despesa(self, id_desp: int, conn: Optional[Any] = None) -> bool:
        """
        Exclui o registro de uma despesa pelo ID.

        Args:
            id_desp (int): Identificador da despesa na tabela.
            conn (Optional[Any]): Conexão ativa no momento da exclusão.

        Returns:
            bool: Validador de sucesso (True) ou Falha (False).
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
        try:
            sql = "DELETE FROM despesas WHERE id = %s"
            cursor.execute(sql, (id_desp,))
            conn.commit()
            return True
    
        except Exception as e:
            print(f"Erro ao deletar no MySQL: {e}")
            conn.rollback()
            return False
    
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn) 


# =================================================================================
# --- REPOSITÓRIO CARTÃO DE CRÉDITO ---
# =================================================================================

class Rep_Cartao_credito:
    """
    Abstração de acesso aos dados para manipulação das faturas e propriedades de cartões.
    """

    def __init__(self, db_conn: Database) -> None:
        self.db_conn: Database = db_conn
    
    def dados_cartoes(self, id_user: int, conn: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Recupera as características de todos os cartões vinculados a um usuário.

        Args:
            id_user (int): PK do usuário.
            conn (Optional[Any]): Controle opcional de sessão do banco.

        Returns:
            List[Dict[str, Any]]: Mapeamento plano das Entidades Cartao_credito.
            
        Raises:
            MySQLdb.Error: Quando ocorre erro fatal na formatação do SQL.
        """
        gerenciar_conn = False

        if conn is None:
            conn= self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()

        try:
            query = "SELECT nome, limite, dia_fechamento, dia_vencimento, bandeira, cor, id  FROM cartoes_credito WHERE id_usuario= %s"
            cursor.execute(query, (id_user, ))
            cartoes = cursor.fetchall()

            if cartoes:
                objetos = [Cartao_credito(*card) for card in cartoes]
                return [obj.to_dict() for obj in objetos]
            else:
                return []
        
        except MySQLdb.Error as e: 
            print(f'Erro no MySQL ao buscar cartões de crédito: {e}')
            raise 

        except Exception as e:
            print(f'Erro inesperado ao buscar cartões de crédito: {e}')
            return []

        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def inserir_cc(self, id_user: int, cartao: Cartao_credito, conn: Optional[Any] = None) -> Optional[int]:
        """
        Registra um novo meio de pagamento (Cartão de Crédito) para o usuário.

        Args:
            id_user (int): FK do usuário responsável.
            cartao (Cartao_credito): Objeto contendo os campos formatados.
            conn (Optional[Any]): Parâmetro de transação.

        Returns:
            Optional[int]: O código ID registrado no BD, ou None.
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
        try:
            sql = "INSERT INTO cartoes_credito (nome, limite, dia_fechamento, dia_vencimento, bandeira, cor, id_usuario) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (cartao.nome_cartao, cartao.limite_cartao, cartao.dia_fechamento, cartao.dia_vencimento, cartao.bandeira, cartao.cor, id_user))
            conn.commit()
            return cursor.lastrowid 
    
        except MySQLdb.Error as e: 
            print(f"Erro MySQL ao inserir cartão: {e}")
            conn.rollback()
            return None 
    
        except Exception as e:
            print(f"Erro inesperado ao inserir cartão: {e}")
            conn.rollback()
            return None
        
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def atualizar_cartao(self, cartao: Cartao_credito, conn: Optional[Any] = None) -> bool:
        """
        Executa um UPDATE nas regras (fechamento, limite, visual) de um cartão.

        Args:
            cartao (Cartao_credito): Objeto contendo o estado atualizado.
            conn (Optional[Any]): Transação sob demanda.

        Returns:
            bool: Sucesso da operação via Commit/Rollback.
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
    
        try:
            sql = "UPDATE cartoes_credito SET nome = %s, limite = %s, dia_fechamento = %s, dia_vencimento = %s, bandeira= %s, cor = %s WHERE id = %s"
            cursor.execute(sql, (cartao.nome_cartao, cartao.limite_cartao, cartao.dia_fechamento, cartao.dia_vencimento, cartao.bandeira, cartao.cor,  cartao.id_cartao))
            conn.commit()

            print(f"Cartão - '{cartao.nome_cartao}' atualizado com sucesso!")
            return True
    
        except MySQLdb.Error as e: 
            print(f"Erro MySQL ao fazer atualização: {e}")
            conn.rollback()
            return False 
    
        except Exception as e:
            print(f"Erro inesperado ao atualizar cartão: {e}")
            conn.rollback()
            return False
        
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def deletar_cartao(self, id_card: int, conn: Optional[Any] = None) -> bool:
        """
        Remove o cadastro do cartão do banco de dados (Gera Exclusão em Cascata se configurado).

        Args:
            id_card (int): ID de destino.
            conn (Optional[Any]): Flag gerencial de sessão.

        Returns:
            bool: Retorno limpo indicando sucesso/falha do `DELETE`.
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
        try:
            sql = "DELETE FROM cartoes_credito WHERE id = %s"
            cursor.execute(sql, (id_card,))
            conn.commit()
            return True
    
        except Exception as e:
            print(f"Erro ao deletar no MySQL: {e}")
            conn.rollback()
            return False
    
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


# =================================================================================
# --- REPOSITÓRIO ASSINATURA ---
# =================================================================================

class Rep_Assinatura:
    """
    Controla o fluxo de dados dos gastos recorrentes (Assinaturas).
    """

    def __init__(self, db_conn: Database) -> None:
        self.db_conn: Database = db_conn
    
    def dados_assinaturas(self, id_user: int, conn: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Extrai todo o pool de assinaturas pertencentes a um ID de usuário.

        Args:
            id_user (int): Parâmetro de busca WHERE.
            conn (Optional[Any]): Objeto de conexão externa.

        Returns:
            List[Dict[str, Any]]: Lista plana convertida pela entidade base Assinatura.
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()

        try:
            query = """
                SELECT nome, valor, descricao, categoria, data_aquisicao, data_primeiro_pagamento, dia_vencimento, id_cartao, id
                FROM assinaturas 
                WHERE id_usuario = %s 
            """
        
            cursor.execute(query, (id_user,))
            assinaturas = cursor.fetchall()
        
            if assinaturas:
                objetos = [Assinatura(*ass) for ass in assinaturas]
                return [obj.to_dict() for obj in objetos]
            return []

        except Exception as e:
            print(f"Erro ao buscar todas as Assinaturas: {e}")
            return []
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def pega_assinaturas_cartao(self, id_user: int, id_card: int, conn: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Consulta DTO: Assinaturas acopladas ao seu modelo de cobrança (Cartão de Crédito).

        Args:
            id_user (int): FK Usuário.
            id_card (int): FK Cartão requerido para o JOIN.
            conn (Optional[Any]): Estado da conexão.

        Returns:
            List[Dict[str, Any]]: Dicionários do objeto AssinaturaDetalhadoDTO para leitura densa.
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()

        try:
            query = """
                SELECT 
                    a.id, 
                    a.nome, 
                    a.valor,
                    a.descricao,
                    a.categoria,
                    a.data_aquisicao,
                    a.data_primeiro_pagamento,
                    a.dia_vencimento,
                    c.nome,
                    c.limite, 
                    c.dia_fechamento, 
                    c.dia_vencimento,
                    c.bandeira,
                    c.cor
                FROM assinaturas a
                INNER JOIN cartoes_credito c ON a.id_cartao = c.id
                WHERE a.id_usuario = %s AND a.id_cartao = %s
            """
        
            cursor.execute(query, (id_user, id_card))
            resultados = cursor.fetchall()
        
            if resultados:
                objetos = [AssinaturaDetalhadoDTO(*resul)  for resul in resultados]
                return [obj.to_dict() for obj in objetos]
            return []

        except Exception as e:
            print(f"[repositórios] Erro ao buscar assinaturas do cartão informado, ID:{id_card}: {e}")
            return []
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def pega_assinaturas_avulsas(self, id_user: int, conn: Optional[Any] = None) -> List[Dict[str, Any]]:
        """
        Retorna as assinaturas cobradas via PIX/Boleto, descontadas da renda principal.

        Args:
            id_user (int): Busca por usuário local.
            conn (Optional[Any]): Parâmetro de conexão.

        Returns:
            List[Dict[str, Any]]: Objetos base extraídos de linhas onde a FK do cartão é nula.
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()

        try:
            query = """
                SELECT nome, valor, descricao, categoria, data_aquisicao, data_primeiro_pagamento, dia_vencimento, id_cartao, id FROM assinaturas WHERE id_usuario = %s and id_cartao IS NULL
            """
        
            cursor.execute(query, (id_user,))
            assinaturas = cursor.fetchall()
        
            if assinaturas:
                objetos = [Assinatura(*ass)  for ass in assinaturas]
                return [obj.to_dict()  for obj in objetos]
            return []

        except Exception as e:
            print(f"Erro ao buscar Assinaturas avulças: {e}")
            return []
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def inserir_assinatura(self, id_user: int, assinatura: Assinatura, conn: Optional[Any] = None) -> Union[int, bool]:
        """
        Persiste um novo compromisso recorrente (Assinatura) no banco.

        Args:
            id_user (int): Identificação do dono.
            assinatura (Assinatura): Entidade base com os dados requeridos.
            conn (Optional[Any]): Fluxo opcional, cria conexão própria por padrão.

        Returns:
            Union[int, bool]: ID numérico da inserção se sucesso, booleano False em caso de erro.
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True
            
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO assinaturas 
                (nome, valor, descricao, categoria, data_aquisicao, data_primeiro_pagamento, dia_vencimento, id_usuario, id_cartao) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (assinatura.nome, assinatura.valor, assinatura.descricao, assinatura.categoria, assinatura.data_aquisicao, assinatura.data_pp, assinatura.dia_vencimento, id_user, assinatura.id_cc)

            cursor.execute(query, valores)
            conn.commit()
            return cursor.lastrowid
    
        except Exception as e:
            print(f"Erro ao salvar assinatura: {e}")
            return False
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)       


    def atualizar_assinatura(self, assinatura: Assinatura, conn: Optional[Any] = None) -> bool:
        """
        Substitui as configurações atuais de uma assinatura por novos valores.

        Args:
            assinatura (Assinatura): Objeto de transporte das alterações contendo `id_ass`.
            conn (Optional[Any]): Injeção de dependência de conexão.

        Returns:
            bool: Indicador do final do fluxo SQL (True se Commit executado).
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
    
        try:
            sql = "UPDATE assinaturas SET nome = %s, valor = %s, descricao = %s, categoria= %s, data_aquisicao = %s, data_primeiro_pagamento = %s, dia_vencimento = %s,  id_cartao = %s WHERE id = %s"

            cursor.execute(sql, (assinatura.nome, assinatura.valor, assinatura.descricao, assinatura.categoria, assinatura.data_aquisicao, assinatura.data_pp, assinatura.dia_vencimento, assinatura.id_cc, assinatura.id_ass))

            conn.commit()

            print(f"Assinatura - '{assinatura.nome}' atualizada com sucesso!")
            return True
    
        except MySQLdb.Error as e: 
            print(f"Erro MySQL ao fazer atualização: {e}")
            conn.rollback()
            return False 
    
        except Exception as e:
            print(f"Erro inesperado ao atualizar assinatura: {e}")
            conn.rollback()
            return False
        
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def deletar_assinatura(self, id_ass: int, conn: Optional[Any] = None) -> bool:
        """
        Executa a exclusão de uma assinatura da listagem do usuário.

        Args:
            id_ass (int): Target ID de exclusão.
            conn (Optional[Any]): Estado de sessão.

        Returns:
            bool: True se os dados foram obliterados corretamente.
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
        try:
            sql = "DELETE FROM assinaturas WHERE id = %s"
            cursor.execute(sql, (id_ass,))
            conn.commit()
            return True
    
        except Exception as e:
            print(f"Erro ao deletar no MySQL: {e}")
            conn.rollback()
            return False
    
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)