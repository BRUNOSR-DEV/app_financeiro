import MySQLdb

import configparser
from calendar import monthrange
from datetime import datetime


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
            return 'Não tem usuários cadastrados'
        
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

        if usuario:
            return usuario
        else:
            return []
            return 'Não tem usuários cadastrados'
        
    except MySQLdb.Error as e: # Captura erro específico do MySQL
        print(f'Erro no MySQL ao buscar usuário: {e}')
        raise # Re-levanta a exceção para que o chamador saiba que algo deu errado

    except Exception as e:
        print(f'Erro inesperado ao buscar usuário: {e}')

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
        sql = "SELECT * FROM cartoes_credito WHERE id_usuario= %s"
        cursor.execute(sql, (id_user, ))
        cartoes = cursor.fetchall()

        if cartoes:
            return cartoes
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


def inserir_despesas(id_usu, local, valor_total, parcelas, descricao, categoria, data, dia_venc=None, id_cc=None, conn=None):
    """ Função que inseri as despesas do usuário no BD e retorna o id da mesma"""
    
    gerenciar_conn = False
    if conn is None:
        conn = conectar_bd_original()
        gerenciar_conn = True

    cursor = conn.cursor()
    try:
        sql = "INSERT INTO despesas (id_usuario, local, valor_total, parcelas, descricao, categoria, data, dia_vencimento, id_cc) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (id_usu, local,valor_total, parcelas, descricao, categoria, data, dia_venc, id_cc))
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
    
    except MySQLdb.Error as e: # Captura erro específico do MySQL
        print(f"Erro MySQL ao fazer atualização: {e}")
        conn.rollback()
        return None # Retorna None para indicar falha
    
    except Exception as e:
        print(f"Erro inesperado ao inserir cartão: {e}")
        conn.rollback()
        return None
        
    finally:
        if gerenciar_conn:
            desconectar(conn)




def pegar_despesas_por_local_mensal(id_usuario, ano, mes):
    """
    Busca o total gasto em cada categoria para um dado mês e ano.
    Retorna uma lista de tuplas: (categoria, total_gasto).
    """
    conn = conectar_bd_original()
    if conn:
        try:
            cursor = conn.cursor()
            
            # ATENÇÃO: A coluna data_compra é 'AAAA-MM-DD'. 
            # Usamos a função MONTH() e YEAR() do MySQL.
            sql = """
            SELECT local, SUM(valor_total) AS total_gasto
            FROM despesas
            WHERE id_usuario = %s 
              AND YEAR(data_compra) = %s 
              AND MONTH(data_compra) = %s
            GROUP BY local
            ORDER BY total_gasto DESC;
            """
            
            cursor.execute(sql, (id_usuario, ano, mes))
            resultados = cursor.fetchall()
            return resultados
            
        except MySQLdb.Error as e:
            print(f"Erro ao buscar despesas: {e}")
            return []
        finally:
            if 'cursor' in locals() and cursor:
                 cursor.close()
            if conn:
                 conn.close()
    return []


def pegar_gastos_previstos_proximo_mes(id_usuario):
    """
    Busca todas as despesas parceladas ou com dia de vencimento para calcular a previsão.
    """
    conn = conectar_bd_original()
    if not conn:
        return []

    # 1. Determina o mês e ano da PREVISÃO (Mês Seguinte)
    hoje = datetime.now()
    if hoje.month == 12:
        mes_previsto = 1
        ano_previsto = hoje.year + 1
    else:
        mes_previsto = hoje.month + 1
        ano_previsto = hoje.year

    try:
        cursor = conn.cursor()
        
        # 2. SQL busca despesas que podem gerar pagamentos futuros:
        #    a) Despesas parceladas (id_cartao IS NOT NULL)
        #    b) Despesas com dia_vencimento (boletos/contas a pagar)
        sql = """
        SELECT local, valor_total, parcelas, categoria, id_cc, dia_vencimento, data
        FROM despesas
        WHERE id_usuario = %s AND (parcelas > 1 OR dia_vencimento IS NOT NULL)
        ORDER BY data DESC;
        """
        
        cursor.execute(sql, (id_usuario,))
        todas_despesas = cursor.fetchall()
        
        # 3. Lógica em Python para calcular o valor REAL a pagar no Mês Previsto
        gastos_previstos = []
        
        for despesa in todas_despesas:
            # Desempacota os dados da despesa
            (local, valor_total, total_parcelas, categoria, id_cartao, dia_vencimento_str, data_compra) = despesa
            
            # Converte valores importantes
            valor_total = float(valor_total)
            total_parcelas = int(total_parcelas)
            valor_parcela = valor_total / total_parcelas
            
            # Determina o mês e ano da PRIMEIRA parcela (sempre o mês seguinte à compra)
            mes_compra = data_compra.month
            ano_compra = data_compra.year
            
            if mes_compra == 12:
                mes_inicio = 1
                ano_inicio = ano_compra + 1
            else:
                mes_inicio = mes_compra + 1
                ano_inicio = ano_compra
                
            # Calcula a qual parcela corresponde o Mês Previsto
            delta_anos = ano_previsto - ano_inicio
            delta_meses = mes_previsto - mes_inicio
            
            # Número de meses desde a primeira parcela
            meses_passados = delta_anos * 12 + delta_meses
            
            parcela_atual = meses_passados + 1
            
            # Verifica se a despesa é devida no Mês Previsto
            deve_pagar = False
            
            if id_cartao is not None and parcela_atual <= total_parcelas:
                # É uma parcela de cartão e está dentro do limite de parcelas
                deve_pagar = True
            
            elif id_cartao is None and dia_vencimento_str is not None:
                # É um boleto/conta com dia de vencimento, deve pagar TODO mês
                valor_parcela = valor_total # Se não é cartão e não tem parcela, o valor é o total
                deve_pagar = True
            
            if deve_pagar:
                # Adiciona o gasto à lista de previsão
                gastos_previstos.append({
                    'categoria': categoria,
                    'valor': valor_parcela,
                    'origem': local if id_cartao is None else f"Parcela {parcela_atual}/{total_parcelas} em {local}"
                })
        
        return gastos_previstos
        
    except MySQLdb.Error as e:
        print(f"Erro ao buscar gastos previstos: {e}")
        return []
    finally:
        if 'cursor' in locals() and cursor:
             cursor.close()
        if conn:
             conn.close()
    return []



def listar_tarefas(id_usuario, conn=None):
    """ Função que retorna a lista de tarefas do usuário passando o id do mesmo"""
    
    gerenciar_conn = False

    if conn is None:
        conn= conectar_bd_original()
        gerenciar_conn= True

    cursor = conn.cursor()

    try:
        # CORREÇÃO: Usar placeholder %s e passar id_usuario como tupla
        cursor.execute("SELECT id, descricao, checkbox FROM tarefas WHERE fk_usuario = %s", (id_usuario,))
        tarefas = cursor.fetchall() # fetchall() para obter todas as linhas, retorna tupla de tuplas 

        return [(t[0], t[1], t[2]) for t in tarefas] # Se o row_factory não estiver definido, acesse por índice
    
    except MySQLdb.Error as e:
        print(f"Erro MySQL ao listar tarefas: {e}")
        return [] # Retorna lista vazia em caso de erro no DB
    except Exception as e: # Capture exceções para depuração
        print(f"Erro ao listar tarefas: {e}")
        return [] # Retorne uma lista vazia em caso de erro geral
    
    finally:
        if gerenciar_conn:
            desconectar(conn)
        


def deletar_tarefa(tarefa_id, conn=None):
    """ Função que deleta uma tarefa da tabela de tarefas, passando id da tarefa"""

    gerenciar_conn = False

    if conn is None:
        conn = conectar_bd_original()
        gerenciar_conn = True

    cursor = conn.cursor()
    try:
        sql = "DELETE FROM tarefas WHERE id = %s"
        cursor.execute(sql, (tarefa_id,))
        conn.commit()
        return cursor.rowcount > 0 # Retorna True se deletou, False caso contrário
    
    except MySQLdb.Error as e:
        print(f"Erro MySQL ao deletar tarefa ID {tarefa_id}: {e}")
        conn.rollback()
        return False
    except Exception as e:
        print(f"Erro inesperado ao tentar deletar tarefa ID {tarefa_id}: {e}")
        conn.rollback()
        return False
    
    finally:
        if gerenciar_conn:
            desconectar(conn)

    """ ----------- forma mais correta ------------

    def deletar_tarefa(id_tarefa):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM tarefas WHERE id = ?", (id_tarefa,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao deletar tarefa: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()"""



def atualizar_checkbox(tarefa_id, novo_status, conn=None):
    """ Atualiza o status de checkbox no banco de dados """
    
    gerenciar_conn = False

    if conn is None:
        conn = conectar_bd_original()
        gerenciar_conn = True

    cursor = conn.cursor()
    try:
        sql = "UPDATE tarefas SET checkbox = %s WHERE id = %s"
        cursor.execute(sql, (novo_status, tarefa_id,))
        conn.commit()
        return cursor.rowcount > 0 # Retorna True se atualizou, False caso contrário
    except MySQLdb.Error as e:
        print(f"Erro MySQL ao atualizar checkbox - ID {tarefa_id}: {e}")
        conn.rollback()
        return False
    except Exception as e:
        print(f"Erro inesperado ao tentar atualizar checkbox - ID {tarefa_id}: {e}")
        conn.rollback()
        return False
    finally:
        if gerenciar_conn:
            desconectar(conn)
    
    """------ forma mais correta --------------

    def atualizar_status_tarefa(id_tarefa, status_concluida):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE tarefas SET concluida = ? WHERE id = ?",
                       (status_concluida, id_tarefa))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao atualizar status: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()"""


