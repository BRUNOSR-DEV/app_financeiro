import MySQLdb
from models.database import Database

from models.entidades import *


class Rep_Usuario:

    def __init__(self, db: Database):
        self.db = db
    

    def dados_usuarios(self, conn=None):
        """
        Função que retorna lista de usuarios
        """
        gerenciar_conn = False

        if conn is None:
            conn= self.db.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM usuarios')
            usuarios = cursor.fetchall()

            if usuarios:
                objetos = [Usuario(*user) for user in usuarios]
                return [obj.to_dict() for obj in objetos]
        
        except MySQLdb.Error as e: # Captura erro específico do MySQL
            print(f'Erro no MySQL ao pegar dados: {e}')
            raise # Re-levanta a exceção para que o chamador saiba que algo deu errado

        except Exception as e:
            print(f'Erro inesperado ao pegar usuários: {e}')

        finally:
            if gerenciar_conn:
                self.db.desconectar(conn)


    def pega_usuario(self, id_user, conn=None):
        """
        Função que retorna os dados do  usuario
        """
        gerenciar_conn = False

        if conn is None:
            conn= self.db.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()

        try:
            sql = "SELECT * FROM usuarios WHERE id= %s"
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
                self.db.desconectar(conn)


    def pega_id(self, usuario, conn=None): 
        '''função que busca id do usuário no bd, passando o nome do usuário ''' 

        gerenciar_conn = False

        if conn is None:
            conn = self.db.conectar_bd_original()
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
                self.db.desconectar(conn)


    def inserir_usuario(self, nome_comp, nome_usu, senha, sal_fixo, conn=None):
        """
        Função para inserir um usuário novo completo
        """  
        gerenciar_conn = False

        if conn is None:
            conn= self.db.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
        sucesso = False

        try:

            cursor.execute("INSERT INTO usuarios (nome_completo, nome_usuario, senha, salario_fixo) VALUES (%s, %s, %s, %s)",(nome_comp, nome_usu, senha, sal_fixo))
            conn.commit()

            if cursor.rowcount == 1: #retorna o número de linhas afetadas pela última operação executada.
                print(f'Usuário inserido com sucesso! olá {nome_comp}')
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
                self.db.desconectar(conn)


    def atualizar_renda(self, id_user, nova_renda, conn=None):

        gerenciar_conn = False
        if conn is None:
            conn = self.db.conectar_bd_original()
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
            return None 
    
        except Exception as e:
            print(f"Erro inesperado ao atualizar renda fixa: {e}")
            conn.rollback()
            return None
        
        finally:
            if gerenciar_conn:
                self.db.desconectar(conn)



class Rep_Receita:

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

            if receitas:
                objetos = [Receita(*rec) for rec in receitas]
                return [obj.to_dict() for obj in objetos]
        
        except MySQLdb.Error as e: # Captura erro específico do MySQL
            print(f'Erro no MySQL ao buscar dados de receitas: {e}')
            raise # Re-levanta a exceção para que o chamador saiba que algo deu errado

        except Exception as e:
            print(f'Erro inesperado ao buscar dados de receitas: {e}')

        finally:
            if gerenciar_conn:
                self.db.desconectar(conn)


    def inserir_receita(self, id_usu, valor, descricao, data, conn=None):
        """ Função que inseri a receita do usuário no BD e retorna o id da mesma"""
    
        gerenciar_conn = False

        if conn is None:
            conn = self.db.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
        try:
            sql = "INSERT INTO receitas (id_usuario, valor, descricao, data) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (id_usu, valor, descricao, data))
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
                self.db.desconectar(conn)


    def atualizar_receita(self, id_rec, valor, descricao, data, conn=None):

        gerenciar_conn = False
        if conn is None:
            conn = self.db.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
    
        try:
            sql = "UPDATE receitas SET valor = %s, descricao = %s, data = %s WHERE id = %s"
            cursor.execute(sql, (valor, descricao, data, id_rec))
            conn.commit()

            print(f"Receita com ID {id_rec} atualizada com sucesso!")
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
                self.db.desconectar(conn)


    def deletar_receita(self, id_rec, conn=None):

        gerenciar_conn = False
        if conn is None:
            conn = self.db.conectar_bd_original()
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
                self.db.desconectar(conn)



class Rep_Despesa:

    def __init__(self, db: Database):
        self.db = db


    def dados_despesas(self, id_user, conn=None):

        gerenciar_conn = False
        if conn is None:
            conn = self.db.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()

        try:

            query = """
                SELECT 
                    id, 
                    local, 
                    valor_total, 
                    parcelas,
                    descricao,
                    categoria,
                    data,
                    data_primeira_parc,
                    dia_vencimento,
                    id_cc
                FROM despesas 
                WHERE id_usuario = %s
            """
        
            cursor.execute(query, (id_user, ))
            despesas = cursor.fetchall()
        
            if despesas:
                objetos = [Despesa(*desp) for desp in despesas]
                return [obj.to_dict() for obj in objetos]

        except Exception as e:
            print(f"Erro ao buscar despesas: {e}")
            return []
        finally:
            if gerenciar_conn:
                self.db.desconectar(conn)

    
    # método de busca join - (despesas-cartoes_credito)
    def pega_despesas_cartao(self, id_user, id_card, conn=None):
        """
        Busca todas as despesas de um cartão específico, trazendo junto 
        os dados do cartão em um único dicionário usando INNER JOIN.
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db.conectar_bd_original()
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
                    d.data,
                    c.nome,
                    c.limite, 
                    c.dia_fechamento, 
                    c.dia_vencimento
                FROM despesas d
                INNER JOIN cartoes_credito c ON d.id_cc = c.id
                WHERE d.id_usuario = %s AND d.id_cc = %s
            """
        
            cursor.execute(query, (id_user, id_card))
            resultados = cursor.fetchall()
        
            if resultados:
                objetos = [DespesaDetalhadoDTO(*resul) for resul in resultados]
                return [obj.to_dict()  for obj in objetos]

        except Exception as e:
            print(f"Erro ao buscar despesas e cartão (JOIN): {e}")
            return []
        finally:
            if gerenciar_conn:
                self.db.desconectar(conn)


    #Método que busca só despesas avulsas
    def pega_despesas_avulsas(self, id_user, conn= None):
        """
        Busca todas as despesas de um usuário que o retono do id_cc é None/Null
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()

        try:

            query = """
                SELECT 
                    id, 
                    local, 
                    valor_total, 
                    parcelas,
                    descricao,
                    categoria,
                    data,
                    data_primeira_parc,
                    dia_vencimento
                FROM despesas 
                WHERE id_usuario = %s AND id_cc IS NULL
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
                self.db.desconectar(conn)


    def inserir_despesa(self, id_usu, local, valor_total, parcelas, descricao, categoria, data, dc_prim_parc=None, dia_vencimento = None, id_cc= None, conn= None):
        """ Função que inseri as despesas do usuário no BD e retorna o id da mesma"""
    
        gerenciar_conn = False
        if conn is None:
            conn = self.db.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
        try:
            sql = "INSERT INTO despesas (id_usuario, local, valor_total, parcelas, descricao, categoria, data, data_primeira_parc, dia_vencimento, id_cc) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"
            cursor.execute(sql, (id_usu, local,valor_total, parcelas, descricao, categoria, data, dc_prim_parc, dia_vencimento, id_cc))
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
                self.db.desconectar(conn)


    def atualizar_despesa(self, id_desp, local, valor_total, parcelas, descricao, categoria, data, dc_prim_parc, dia_venc, id_cc, conn= None):

        gerenciar_conn = False
        if conn is None:
            conn = self.db.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
    
        try:
            sql = "UPDATE despesas SET local = %s, valor_total= %s, parcelas= %s, descricao= %s, categoria= %s, data= %s, data_primeira_parc= %s, dia_vencimento= %s, id_cc= %s WHERE id = %s"
            cursor.execute(sql, (local, valor_total, parcelas, descricao, categoria, data, dc_prim_parc, dia_venc, id_cc, id_desp))
            conn.commit()

            print(f"Despesa - '{local}' Atualizado com Sucesso!")
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
                self.db.desconectar(conn)


    def deletar_despesa(self, id_desp, conn=None):

        gerenciar_conn = False
        if conn is None:
            conn = self.db.conectar_bd_original()
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
                self.db.desconectar(conn) 



class Rep_Cartao_credito:

    def __init__(self, db: Database):
        self.db = db

    
    def dados_cartoes(self, id_user, conn=None):
        """
        Função que retorna uma lista com o id do cartão e o nome da tabela cartoes_credito
        """
        gerenciar_conn = False

        if conn is None:
            conn= self.db.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()

        try:
            query = "SELECT id, nome, limite, dia_fechamento, dia_vencimento FROM cartoes_credito WHERE id_usuario= %s"
            cursor.execute(query, (id_user, ))
            cartoes = cursor.fetchall()

            if cartoes:
                objetos = [Cartao_credito(*car)  for car in cartoes]
                return [obj.to_dict()  for obj in objetos]
        
        except MySQLdb.Error as e: # Captura erro específico do MySQL
            print(f'Erro no MySQL ao buscar cartões de crédito: {e}')
            raise # Re-levanta a exceção para que o chamador saiba que algo deu errado

        except Exception as e:
            print(f'Erro inesperado ao buscar cartões de crédito: {e}')

        finally:
            if gerenciar_conn:
                self.db.desconectar(conn)


    def inserir_cc(self, id_usu, nome, limite, dia_f, dia_v, conn=None):
        """ Função que inseri os cartões de crédito do usuário no BD e retorna o id do mesmo"""
    
        gerenciar_conn = False
        if conn is None:
            conn = self.db.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
        try:
            sql = "INSERT INTO cartoes_credito (id_usuario, nome, limite, dia_fechamento, dia_vencimento) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (id_usu, nome, limite, dia_f, dia_v))
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
                self.db.desconectar(conn)


    def atualizar_cartao(self, id_card, nome, limite,  dia_fec, dia_venc, conn=None):

        gerenciar_conn = False
        if conn is None:
            conn = self.db.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
    
        try:
            sql = "UPDATE cartoes_credito SET nome = %s, limite = %s, dia_fechamento = %s, dia_vencimento = %s WHERE id = %s"
            cursor.execute(sql, (nome, limite, dia_fec, dia_venc, id_card))
            conn.commit()

            print(f"Cartão - '{nome}' atualizado com sucesso!")
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
                self.db.desconectar(conn)


    def deletar_cartao(self, id_card, conn=None):

        gerenciar_conn = False
        if conn is None:
            conn = self.db.conectar_bd_original()
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
                self.db.desconectar(conn)



class Rep_Assinatura:

    def __init__(self, db: Database):
        self.db = db

    
    def dados_assinaturas(self, id_user, conn=None):
        """
        Busca todas as assinaturas de um usuário específico.
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()

        try:
            query = """
                SELECT id, nome, valor, descricao, data_aquisicao, data_prim_pag, categoria, id_cc
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
                self.db.desconectar(conn)


    def pega_assinaturas_cartao(self, id_user, id_card, conn=None):
        """
        Busca todas as assinaturas de um cartão específico
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db.conectar_bd_original
            gerenciar_conn = True

        cursor = conn.cursor()

        try:
            query = """
                SELECT 
                    a.id, 
                    a.nome, 
                    a.valor,
                    a.descricao,
                    a.data_aquisicao,
                    a.data_prim_pag,
                    a.dia_vencimento,
                    a.categoria,
                    c.nome,
                    c.limite, 
                    c.dia_fechamento, 
                    c.dia_vencimento
                FROM assinaturas a
                INNER JOIN cartoes_credito c ON a.id_cc = c.id
                WHERE a.id_usuario = %s AND a.id_cc = %s
            """
        
            cursor.execute(query, (id_user, id_card))
            resultados = cursor.fetchall()
        
            if resultados:

                objetos = [AssinaturaDetalhadoDTO(*resul)  for resul in resultados]
                return [obj.to_dict()  for obj in objetos]
     

        except Exception as e:
            print(f"Erro ao buscar assinaturas do cartão informado ID:{id_card}: {e}")
            return []
        finally:
            if gerenciar_conn:
                self.db.desconectar(conn)


    def pega_assinaturas_avulsas(self, id_user, conn=None):
        """
        Busca todas as assinaturas sem cartão de um usuário específico.
        """
        gerenciar_conn = False
        if conn is None:
            conn = self.db.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()

        try:
            query = """
                SELECT id, nome, valor, descricao, data_prim_pag, dia_vencimento, categoria
                FROM assinaturas 
                WHERE id_usuario = %s and id_cc IS NULL
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
                self.db.desconectar(conn)


    def inserir_assinatura(self, id_user, nome, valor, descricao, data_aq, data_prim_pag, dia_venc, categoria, id_cc):

        conn = self.db.conectar_bd_original()
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO assinaturas 
                (id_usuario, nome, valor, descricao, data_aquisicao, data_prim_pag, dia_vencimento, categoria, id_cc) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (id_user, nome, valor, descricao, data_aq, data_prim_pag, dia_venc, categoria, id_cc)
            cursor.execute(query, valores)
            conn.commit()
            return cursor.lastrowid
    
        except Exception as e:
            print(f"Erro ao salvar assinatura: {e}")
            return False
        finally:
            self.db.desconectar(conn)       


    def atualizar_assinatura(self, id_ass, nome,  valor, descricao, data_aq, data_pp, dia_venc, categoria, id_cc, conn=None):

        gerenciar_conn = False
        if conn is None:
            conn = self.db.conectar_bd_original()
            gerenciar_conn = True

        cursor = conn.cursor()
    
        try:
            sql = "UPDATE assinaturas SET nome = %s, valor = %s, descricao = %s, data_aquisicao = %s, data_prim_pag = %s, dia_vencimento = %s, categoria= %s, id_cc = %s WHERE id = %s"
            cursor.execute(sql, (nome, valor, descricao, data_aq, data_pp, dia_venc, categoria, id_cc, id_ass))
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
                self.db.desconectar(conn)

    
    def deletar_assinatura(self, id_ass, conn =None):

        gerenciar_conn = False
        if conn is None:
            conn = self.db.conectar_bd_original()
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
                self.db.desconectar(conn)


