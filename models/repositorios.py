import MySQLdb
from models.database import Database

from models.entidades import *

from utils.segurança import SegurancaService

from decimal import Decimal


class Rep_Usuario:

    def __init__(self, db_conn: Database):
        self.db_conn = db_conn
    
    def validar_credenciais(self, username, senha_digitada):
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
            if senha_digitada == senha_salva:
                nova_senha_cripto = SegurancaService.criptografar_senha(senha_digitada)
                self.atualizar_senha_usuario(user_id, nova_senha_cripto)
                
                print(f"🔒 Usuário {usuario[0]['nome_user']} migrado com sucesso para criptografia avançada!")
                return usuario
            return None


    def dados_usuarios(self, conn=None):
        """
        Função que retorna lista de usuarios
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
        
        except MySQLdb.Error as e: # Captura erro específico do MySQL
            print(f'Erro no MySQL ao pegar dados: {e}')
            raise # Re-levanta a exceção para que o chamador saiba que algo deu errado

        except Exception as e:
            print(f'Erro inesperado ao pegar usuários: {e}')

        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def pega_usuario(self, id_user:int, conn=None):
        """
        Função que retorna os dados do  usuario
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

        
        except MySQLdb.Error as e: # Captura erro específico do MySQL
            print(f'Erro no MySQL ao buscar dados do usuário: {e}')
            raise # Re-levanta a exceção para que o chamador saiba que algo deu errado

        except Exception as e:
            print(f'Erro inesperado ao buscar dados do usuário: {e}')

        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def pega_id(self, usuario: int, conn=None): 
        '''função que busca id do usuário no bd, passando o nome do usuário ''' 

        gerenciar_conn = False

        if conn is None:
            conn= self.db_conn.conectar_bd_original()
            gerenciar_conn= True

        cursor = conn.cursor() 

        try:
            sql = "SELECT id FROM usuarios WHERE nome_usuario = %s" 
            cursor.execute(sql, (usuario,)) #obs. obrigatório passar uma tupla como parâmetro para cursor
            result = cursor.fetchone()
        

            if result:
                return result[0]
        
        except MySQLdb.Error as e:
            print(f"Erro MySQL ao pegar ID: {e}")
            return None # Retorna None em caso de erro no DB  
        except Exception as e:
            print(f"Erro inesperado ao pegar ID: {e}")

        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def inserir_usuario(self, usuario: Usuario, conn=None):
        """
        Função para inserir um usuário novo completo
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

            if cursor.rowcount == 1: #retorna o número de linhas afetadas pela última operação executada.
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


    def atualizar_renda(self, id_user: int, nova_renda: Decimal, conn=None)-> bool: 

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


    def atualizar_senha_usuario(self, user_id: int, nova_senha: str, conn=None):

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
                                         


class Rep_Receita:

    def __init__(self, db_conn: Database):
        self.db_conn = db_conn
    
    def dados_receitas(self, id_user: int, conn=None):
        """
        Função que retorna os dados do  usuario
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
        
        except MySQLdb.Error as e: # Captura erro específico do MySQL
            print(f'Erro no MySQL ao buscar dados de receitas: {e}')
            raise # Re-levanta a exceção para que o chamador saiba que algo deu errado

        except Exception as e:
            print(f'Erro inesperado ao buscar dados de receitas: {e}')

        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def inserir_receita(self, id_user: int, receita: Receita, conn=None):
        """ Função que inseri a receita do usuário no BD e retorna o id da mesma"""
    
        gerenciar_conn = False

        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
        try:
            sql = "INSERT INTO receitas (fonte, valor, descricao, data_recebimento, id_usuario) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (receita.fonte, receita.valor, receita.descricao, receita.data, id_user))
            conn.commit()
            return cursor.lastrowid # Retorna o ID da receita recém-inserida
    
        except MySQLdb.Error as e: # Captura erro específico do MySQL
            print(f"Erro MySQL ao inserir receita: {e}")
            conn.rollback()
            return None # Retorna None para indicar falha
    
        except Exception as e:
            print(f"Erro inesperado ao inserir receita: {e}")
            conn.rollback()
            return None
        
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def atualizar_receita(self, receita: Receita, conn=None):

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
    
        except MySQLdb.Error as e: # Captura erro específico do MySQL
            print(f"Erro MySQL ao fazer atualização: {e}")
            conn.rollback()
            return None # Retorna None para indicar falha
    
        except Exception as e:
            print(f"Erro inesperado ao atualizar receita: {e}")
            conn.rollback()
            return None
        
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def deletar_receita(self, id_rec: int, conn=None):

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



class Rep_Despesa:

    def __init__(self, db_conn: Database):
        self.db_conn = db_conn


    def dados_despesas(self, id_user, conn=None):

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

    
    # método de busca join - (despesas-cartoes_credito)
    def pega_despesas_cartao(self, id_user: int, id_card: int, conn=None):
        """
        Busca todas as despesas de um cartão específico, trazendo junto 
        os dados do cartão em um único dicionário usando INNER JOIN.
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()

        try:
            # A mágica acontece aqui: Juntamos as duas tabelas onde as chaves se encontram
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

    #Método que busca só despesas avulsas
    def pega_despesas_avulsas(self, id_user: int, conn= None):
        """
        Busca todas as despesas de um usuário que o retono do id_cc é None/Null
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

        except Exception as e:
            print(f"Erro ao buscar despesas: {e}")
            return []
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def inserir_despesa(self, id_user: int, despesa: Despesa, conn= None):
        """ Função que inseri as despesas do usuário no BD e retorna o id da mesma"""
    
        gerenciar_conn = False
        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
        try:
            sql = "INSERT INTO despesas (local, valor_total, parcelas, descricao, categoria, data_compra, data_primeiro_pagamento, dia_vencimento, id_usuario, id_cartao) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"

            cursor.execute(sql, (despesa.local, despesa.valor_total, despesa.parcelas, despesa.descricao, despesa.categoria, despesa.data_compra, despesa.data_pp, despesa.dia_vencimento, id_user, despesa.id_cc))
            conn.commit()
            return cursor.lastrowid # Retorna o ID da despesa recém-inserida
    
        except MySQLdb.Error as e: # Captura erro específico do MySQL
            print(f"Erro MySQL ao inserir despesa: {e}")
            conn.rollback()
            return None # Retorna None para indicar falha
    
        except Exception as e:
            print(f"Erro inesperado ao inserir despesa: {e}")
            conn.rollback()
            return None
        
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def atualizar_despesa(self, despesa: Despesa, conn= None):

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


    def deletar_despesa(self, id_desp: int, conn=None):

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



class Rep_Cartao_credito:

    def __init__(self, db_conn: Database):
        self.db_conn = db_conn

    
    def dados_cartoes(self, id_user: int, conn=None):
        """
        Função que retorna uma lista com o id do cartão e o nome da tabela cartoes_credito
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
        
        except MySQLdb.Error as e: # Captura erro específico do MySQL
            print(f'Erro no MySQL ao buscar cartões de crédito: {e}')
            raise # Re-levanta a exceção para que o chamador saiba que algo deu errado

        except Exception as e:
            print(f'Erro inesperado ao buscar cartões de crédito: {e}')

        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def inserir_cc(self, id_user, cartao: Cartao_credito, conn=None):
        """ Função que inseri os cartões de crédito do usuário no BD e retorna o id do mesmo"""
    
        gerenciar_conn = False
        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
        try:
            sql = "INSERT INTO cartoes_credito (nome, limite, dia_fechamento, dia_vencimento, bandeira, cor, id_usuario) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (cartao.nome_cartao, cartao.limite_cartao, cartao.dia_fechamento, cartao.dia_vencimento, cartao.bandeira, cartao.cor, id_user))
            conn.commit()
            return cursor.lastrowid # Retorna o ID do c.c. recém-inserida
    
        except MySQLdb.Error as e: # Captura erro específico do MySQL
            print(f"Erro MySQL ao inserir cartão: {e}")
            conn.rollback()
            return None # Retorna None para indicar falha
    
        except Exception as e:
            print(f"Erro inesperado ao inserir cartão: {e}")
            conn.rollback()
            return None
        
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def atualizar_cartao(self, cartao: Cartao_credito, conn=None):

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


    def deletar_cartao(self, id_card: int, conn=None):

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



class Rep_Assinatura:

    def __init__(self, db_conn: Database):
        self.db_conn = db_conn

    
    def dados_assinaturas(self, id_user, conn=None):
        """
        Busca todas as assinaturas de um usuário específico.
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()

        try:
            query = """
                SELECT id, nome, valor, descricao, categoria, data_aquisicao, data_primeiro_pagamento, dia_vencimento, id_cartao
                FROM assinaturas 
                WHERE id_usuario = %s 
            """
        
            cursor.execute(query, (id_user,))
            assinaturas = cursor.fetchall()
        
            if assinaturas:
                objetos = [Assinatura(*ass) for ass in assinaturas]
                return [obj.to_dict() for obj in objetos]

        except Exception as e:
            print(f"Erro ao buscar todas as Assinaturas: {e}")
            return []
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def pega_assinaturas_cartao(self, id_user, id_card, conn=None):
        """
        Busca todas as assinaturas de um cartão específico
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
                    c.dia_vencimento
                FROM assinaturas a
                INNER JOIN cartoes_credito c ON a.id_cartao = c.id
                WHERE a.id_usuario = %s AND a.id_cartao = %s
            """
        
            cursor.execute(query, (id_user, id_card))
            resultados = cursor.fetchall()
        
            if resultados:

                objetos = [AssinaturaDetalhadoDTO(*resul)  for resul in resultados]
                return [obj.to_dict() for obj in objetos]
     

        except Exception as e:
            print(f"[repositórios] Erro ao buscar assinaturas do cartão informado, ID:{id_card}: {e}")
            return []
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def pega_assinaturas_avulsas(self, id_user, conn=None):
        """
        Busca todas as assinaturas sem cartão de um usuário específico.
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()

        try:
            query = """
                SELECT id, nome, valor, descricao, categoria, data_aquisicao, data_primeiro_pagamento, dia_vencimento FROM assinaturas WHERE id_usuario = %s and id_cartao IS NULL
            """
        
            cursor.execute(query, (id_user,))
            assinaturas = cursor.fetchall()
        
            if assinaturas:
                objetos = [Assinatura(*ass)  for ass in assinaturas]
                return [obj.to_dict()  for obj in objetos]

        except Exception as e:
            print(f"Erro ao buscar Assinaturas avulças: {e}")
            return []
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)


    def inserir_assinatura(self, id_user, nome, valor, descricao, data_aq, data_pp, dia_venc, categoria, id_cc):

        conn = self.db_conn.conectar_bd_original()
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO assinaturas 
                (id_usuario, nome, valor, descricao, categoria, data_aquisicao, data_primeiro_pagamento, dia_vencimento, id_cartao) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (id_user, nome, valor, descricao, data_aq, data_pp, dia_venc, categoria, id_cc)
            cursor.execute(query, valores)
            conn.commit()
            return cursor.lastrowid
    
        except Exception as e:
            print(f"Erro ao salvar assinatura: {e}")
            return False
        finally:
            self.db_conn.desconectar(conn)       


    def atualizar_assinatura(self, id_ass, nome,  valor, descricao, data_aq, data_pp, dia_venc, categoria, id_cc, conn=None):

        gerenciar_conn = False
        if conn is None:
            conn = self.db_conn.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
    
        try:
            sql = "UPDATE assinaturas SET nome = %s, valor = %s, descricao = %s, categoria= %s, data_aquisicao = %s, data_primeiro_pagamento = %s, dia_vencimento = %s,  id_cartao = %s WHERE id = %s"
            cursor.execute(sql, (nome, valor, descricao, categoria, data_aq, data_pp, dia_venc, id_cc, id_ass))
            conn.commit()

            print(f"Assinatura - '{nome}' atualizada com sucesso!")
            return True
    
        except MySQLdb.Error as e: # Captura erro específico do MySQL
            print(f"Erro MySQL ao fazer atualização: {e}")
            conn.rollback()
            return False # Retorna None para indicar falha
    
        except Exception as e:
            print(f"Erro inesperado ao atualizar assinatura: {e}")
            conn.rollback()
            return False
        
        finally:
            if gerenciar_conn:
                self.db_conn.desconectar(conn)

    
    def deletar_assinatura(self, id_ass, conn =None):

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


