import MySQLdb

import configparser
from datetime import datetime

#------------------Configuração banco de dados-------------------
def ler_configuracao_bd():
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


def conectar_bd_original():
    """
    Função para conectar ao servidor
    """
    db_config = ler_configuracao_bd()
    if not db_config:
        # Se as credenciais não puderam ser lidas, não tente conectar
        print("Não foi possível conectar ao banco de dados devido a um erro de configuração.")
        return None
    
    try:
        conn = MySQLdb.connect(
            db=db_config['db'],
            host=db_config['host'],
            user=db_config['user'],
            passwd=db_config['passwd']
        )
        return conn

    except MySQLdb.Error as e:
        print(f'Erro na conexão ao MySql Server: {e}')


def desconectar(conn):
    """ 
    Função para desconectar do servidor.
    """
    if conn:
        conn.close()

#-------------------------------------------------------------------

#-------------------- Listagem de dados / entidades  -----------------------------
def pega_usuarios(conn=None):
    """
    Função que retorna lista de usuarios
    """
    gerenciar_conn = False

    if conn is None:
        conn= conectar_bd_original()
        gerenciar_conn = True

    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM usuarios')
        usuarios = cursor.fetchall()

        if usuarios:
            return usuarios
        else:
            return []
        
    except MySQLdb.Error as e: # Captura erro específico do MySQL
        print(f'Erro no MySQL ao pegar dados: {e}')
        raise # Re-levanta a exceção para que o chamador saiba que algo deu errado

    except Exception as e:
        print(f'Erro inesperado ao pegar dados: {e}')

    finally:
        if gerenciar_conn:
            desconectar(conn)


def dados_user(id_user, conn=None):
    """
    Função que retorna os dados do  usuario
    """
    gerenciar_conn = False

    if conn is None:
        conn= conectar_bd_original()
        gerenciar_conn = True

    cursor = conn.cursor()

    try:
        sql = "SELECT * FROM usuarios WHERE id= %s"
        cursor.execute(sql, (id_user, ))
        usuario = cursor.fetchall()

        colunas = [
            'id_user', 'nome_completo', 'nome_user', 'senha', 'sal_fixo'
        ]
        resultado = [dict(zip(colunas, valor)) for valor in usuario]

        for dado in resultado:

            if dado:
                return dado
            else:
                return []
        
    except MySQLdb.Error as e: # Captura erro específico do MySQL
        print(f'Erro no MySQL ao buscar dados do usuário: {e}')
        raise # Re-levanta a exceção para que o chamador saiba que algo deu errado

    except Exception as e:
        print(f'Erro inesperado ao buscar dados do usuário: {e}')

    finally:
        if gerenciar_conn:
            desconectar(conn)


def dados_receita(id_user, conn=None):
    """
    Função que retorna os dados do  usuario
    """
    gerenciar_conn = False

    if conn is None:
        conn= conectar_bd_original()
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
            desconectar(conn)


def dados_card(id_user, conn=None):
    """
    Função que retorna uma lista com o id do cartão e o nome da tabela cartoes_credito
    """
    gerenciar_conn = False

    if conn is None:
        conn= conectar_bd_original()
        gerenciar_conn = True

    cursor = conn.cursor()

    try:
        query = "SELECT id, nome, limite, dia_fechamento, dia_vencimento FROM cartoes_credito WHERE id_usuario= %s"
        cursor.execute(query, (id_user, ))
        cartoes = cursor.fetchall()

        colunas = [
            'id_cartao', 'nome_cartao', 'limite_cartao', 'fechamento_fatura', 'vencimento_fatura'
        ]

        if cartoes:
            return [dict(zip(colunas, linha)) for linha in cartoes]
        else:
            return []
        
    except MySQLdb.Error as e: # Captura erro específico do MySQL
        print(f'Erro no MySQL ao buscar cartões de crédito: {e}')
        raise # Re-levanta a exceção para que o chamador saiba que algo deu errado

    except Exception as e:
        print(f'Erro inesperado ao buscar cartões de crédito: {e}')

    finally:
        if gerenciar_conn:
            desconectar(conn)


def pega_id(usuario, conn=None): 
    '''função que busca id do usuário no bd, passando o nome do usuário ''' 

    gerenciar_conn = False

    if conn is None:
        conn = conectar_bd_original()
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
            desconectar(conn)


def pega_despesas_cartao(id_user, id_card, conn=None):
    """
    Busca todas as despesas de um cartão específico, trazendo junto 
    os dados do cartão em um único dicionário usando INNER JOIN.
    """
    gerenciar_conn = False
    if conn is None:
        conn = conectar_bd_original()
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
        
        # Mapeando as colunas. 
        colunas = [
            'despesa_id', 'local', 'valor_total', 'parcelas','descricao', 'categoria', 'data_compra', 
            'nome_cartao', 'limite_cartao', 'fechamento_fatura', 'vencimento_fatura'
        ]
        
        return [dict(zip(colunas, linha)) for linha in resultados]

    except Exception as e:
        print(f"Erro ao buscar despesas e cartão (JOIN): {e}")
        return []
    finally:
        if gerenciar_conn:
            desconectar(conn)


def pega_despesas(id_user, conn= None):

    """
    Busca todas as despesas de um usuário que o retono do id_cc é None
    """
    gerenciar_conn = False
    if conn is None:
        conn = conectar_bd_original()
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
        resultados = cursor.fetchall()
        
        # Mapeando as colunas. 
        colunas = [
            'despesa_id', 'local', 'valor_total', 'parcelas','descricao', 'categoria', 'data_compra', 'primeira_parc', 'dia_vencimento', 
        ]
        
        return [dict(zip(colunas, linha)) for linha in resultados]

    except Exception as e:
        print(f"Erro ao buscar despesas: {e}")
        return []
    finally:
        if gerenciar_conn:
            desconectar(conn)


def dados_assinaturas_avulsas(id_user, conn=None):
    """
    Busca todas as assinaturas sem cartão de um usuário específico.
    """
    gerenciar_conn = False
    if conn is None:
        conn = conectar_bd_original()
        gerenciar_conn = True

    cursor = conn.cursor()

    try:
        query = """
            SELECT id, nome, valor, descricao, data_prim_pag, dia_vencimento, categoria
            FROM assinaturas 
            WHERE id_usuario = %s and id_cc IS NULL
        """
        
        cursor.execute(query, (id_user,))
        resultados = cursor.fetchall()
        
        # Mapeando as colunas. 
        colunas = [
            'id_assinatura', 'nome', 'valor', 'descricao','data_pp', 'dia_vencimento', 'categoria', 
        ]
        
        return [dict(zip(colunas, linha)) for linha in resultados]

    except Exception as e:
        print(f"Erro ao buscar Assinaturas avulças: {e}")
        return []
    finally:
        if gerenciar_conn:
            desconectar(conn)


def dados_assinaturas_cartao(id_user, id_card, conn=None):
    """
    Busca todas as assinaturas de um cartão específico
    """
    gerenciar_conn = False
    if conn is None:
        conn = conectar_bd_original()
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
        
        # Mapeando as colunas. 
        colunas = [
            'id_assinatura', 'nome', 'valor','descricao','data_aquisicao','data_prim_pag','dia_vencimento','categoria','nome_cartao','limite','dia_fechamento_cc', 'dia_vencimento_cc'
        ]
        
        return [dict(zip(colunas, linha)) for linha in resultados]
     

    except Exception as e:
        print(f"Erro ao buscar assinaturas do cartão informado ID:{id_card}: {e}")
        return []
    finally:
        if gerenciar_conn:
            desconectar(conn)


def dados_assinaturas_full(id_user, conn=None):
    """
    Busca todas as assinaturas de um usuário específico.
    """
    gerenciar_conn = False
    if conn is None:
        conn = conectar_bd_original()
        gerenciar_conn = True

    cursor = conn.cursor()

    try:
        query = """
            SELECT id, nome, valor, descricao, data_aquisicao, data_prim_pag, categoria, id_cc
            FROM assinaturas 
            WHERE id_usuario = %s 
        """
        
        cursor.execute(query, (id_user,))
        resultados = cursor.fetchall()
        
        # Mapeando as colunas. 
        colunas = [
            'id_ass', 'nome', 'valor', 'descricao','data_aquisicao','data_prim_pag', 'categoria', 'id_cc'
        ]
        
        return [dict(zip(colunas, linha)) for linha in resultados]

    except Exception as e:
        print(f"Erro ao buscar todas as Assinaturas: {e}")
        return []
    finally:
        if gerenciar_conn:
            desconectar(conn)

#----------------------------------------------------------------------

#------------------------- Inserir ------------------------------------
def inserir_usuario(nome_comp, nome_usu, senha, sal_fixo, conn=None):
    """
    Função para inserir um usuário novo completo
    """  
    gerenciar_conn = False

    if conn is None:
        conn= conectar_bd_original()
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
            desconectar(conn)
      

def inserir_receitas(id_usu, valor, descricao, data, conn=None):
    """ Função que inseri a receita do usuário no BD e retorna o id da mesma"""
    
    gerenciar_conn = False
    if conn is None:
        conn = conectar_bd_original()
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
            desconectar(conn)

    
    ''' ------outra forma de se fazer---------
    
    def inserir_tarefas(descricao_tarefa, id_usuario, status_concluida):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO tarefas (descricao, id_usuario, concluida) VALUES (?, ?, ?)",
                       (descricao_tarefa, id_usuario, status_concluida))
        conn.commit()
        return cursor.lastrowid # Retorna o ID da última linha inserida
    except sqlite3.Error as e:
        print(f"Erro ao inserir tarefa: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()'''


def inserir_assinatura(id_user, nome, valor, descricao, data_aq, data_prim_pag, dia_venc, categoria, id_cc):

    conn = conectar_bd_original()
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
        desconectar(conn)


def inserir_despesas(id_usu, local, valor_total, parcelas, descricao, categoria, data, dc_prim_parc=None, dia_vencimento = None, id_cc= None, conn= None):
    """ Função que inseri as despesas do usuário no BD e retorna o id da mesma"""
    
    gerenciar_conn = False
    if conn is None:
        conn = conectar_bd_original()
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
            desconectar(conn)


def inserir_cc(id_usu, nome, limite, dia_f, dia_v, conn=None):
    """ Função que inseri os cartões de crédito do usuário no BD e retorna o id do mesmo"""
    
    gerenciar_conn = False
    if conn is None:
        conn = conectar_bd_original()
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
            desconectar(conn)


def inserir_dividas(id_usu, valor_total, descricao, data_venc, conn=None):
    """ Função que inseri as dividas do usuário no BD e retorna o id do mesmo"""
    
    gerenciar_conn = False
    if conn is None:
        conn = conectar_bd_original()
        gerenciar_conn = True

    cursor = conn.cursor()
    try:
        sql = "INSERT INTO dividas (id_usuario, valor_total, valor_pago, descricao, data_vencimento, status) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (id_usu, valor_total, 0, descricao, data_venc, 'Ativa'))
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
            desconectar(conn)

#------------------------------------------------------------------------------

# ----------------------------- Atualizar ---------------------------------

def atualizar_divida(id_divida, valor_pago, conn=None):
    """Atualiza a tabela 'dividas' no banco de dados"""

    gerenciar_conn = False
    if conn is None:
        conn = conectar_bd_original()
        gerenciar_conn = True

    cursor = conn.cursor()

    try:
        sql = "UPDATE dividas SET valor_pago = valor_pago + %s WHERE id = %s"
        cursor.execute(sql, (valor_pago, id_divida))
        conn.commit()
        print(f"Dívida com ID {id_divida} atualizada com sucesso!")
        return True
    
    except MySQLdb.Error as e: # Captura erro específico do MySQL
        print(f"Erro MySQL ao fazer atualização: {e}")
        conn.rollback()
        return False # Retorna None para indicar falha
    
    except Exception as e:
        print(f"Erro inesperado ao inserir cartão: {e}")
        conn.rollback()
        return False
        
    finally:
        if gerenciar_conn:
            desconectar(conn)


def atualizar_receitas(id_rec, valor, descricao, data, conn=None):

    gerenciar_conn = False
    if conn is None:
        conn = conectar_bd_original()
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
            desconectar(conn)


def atualiza_assinatura(id_ass, nome,  valor, descricao, data_aq, data_pp, dia_venc, categoria, id_cc, conn=None):

    gerenciar_conn = False
    if conn is None:
        conn = conectar_bd_original()
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
            desconectar(conn)


def atualizar_cartao(id_card, nome, limite,  dia_fec, dia_venc, conn=None):

    gerenciar_conn = False
    if conn is None:
        conn = conectar_bd_original()
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
            desconectar(conn)
#------------------------------------------------------------------------------

# ----------------------------- Deletar ---------------------------------

def deletar_receita(id_rec, conn=None):

    gerenciar_conn = False
    if conn is None:
        conn = conectar_bd_original()
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
            desconectar(conn)


def deletar_assinatura(id_ass, conn =None):

    gerenciar_conn = False
    if conn is None:
        conn = conectar_bd_original()
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
            desconectar(conn)
