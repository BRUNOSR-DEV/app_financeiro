from models.database import Database

class Rep_Usuarios:

    def __init__(self, conn: Database):
        self.conn = conn.conectar_bd_original()


class Rep_Receitas:

    def __init__(self, conn: Database):
        self.conn = conn.conectar_bd_original()


class Rep_Despesas:

    def __init__(self, conn: Database):
        self.conn = conn.conectar_bd_original()


class Rep_Card_credito:

    def __init__(self, conn: Database):
        self.conn = conn.conectar_bd_original()


class Rep_Assinaturas:

    def __init__(self, conn: Database):
        self.conn = conn.conectar_bd_original()