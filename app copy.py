import customtkinter
import mysql.connector
from mysql.connector import Error
import hashlib

# ---------------------------------------------------------------------------------------------------
# INSTRUÇÕES IMPORTANTES
# ---------------------------------------------------------------------------------------------------
# 1. Certifique-se de ter o MySQL instalado e um banco de dados configurado.
# 2. Instale as bibliotecas necessárias. Abra seu terminal e execute:
#    pip install customtkinter
#    pip install mysql-connector-python
# 3. Altere as variáveis de conexão abaixo com as suas credenciais do MySQL.
# 4. A senha do usuário será armazenada no banco de dados como um hash SHA256 para segurança.
# ---------------------------------------------------------------------------------------------------

# Suas credenciais do banco de dados MySQL
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "your_password"  # Altere para sua senha do MySQL
DB_NAME = "controle_financeiro" # Pode ser qualquer nome de banco de dados que você crie

class App(customtkinter.CTk):
    """
    Classe principal do aplicativo de controle financeiro.
    Gerencia a interface do usuário e a conexão com o banco de dados.
    """
    def __init__(self):
        super().__init__()

        self.title("Controle Financeiro")
        self.geometry("500x450")
        self.resizable(False, False)

        # Configura o layout da grade
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Inicializa a conexão com o banco de dados
        self.db = DBConnector()
        self.db.connect()
        self.db.create_user_table() # Cria a tabela de usuários se ela não existir

        # Exibe a tela de login inicialmente
        self.show_login_screen()

    def show_login_screen(self):
        """Cria e exibe a tela de login."""
        # Frame para a tela de login, para facilitar a troca de telas
        if hasattr(self, 'current_frame'):
            self.current_frame.destroy()
        
        self.current_frame = customtkinter.CTkFrame(self)
        self.current_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.current_frame.grid_rowconfigure(5, weight=1)
        self.current_frame.grid_columnconfigure(0, weight=1)

        # Widgets da tela de login
        label = customtkinter.CTkLabel(self.current_frame, text="Login", font=customtkinter.CTkFont(size=24, weight="bold"))
        label.grid(row=0, column=0, pady=(20, 10))
        
        self.login_user_entry = customtkinter.CTkEntry(self.current_frame, placeholder_text="Nome de Usuário")
        self.login_user_entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.login_password_entry = customtkinter.CTkEntry(self.current_frame, placeholder_text="Senha", show="*")
        self.login_password_entry.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.login_button = customtkinter.CTkButton(self.current_frame, text="Entrar", command=self.login_user)
        self.login_button.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.register_button = customtkinter.CTkButton(self.current_frame, text="Não tem uma conta? Registre-se", fg_color="transparent", text_color="gray", hover_color="#222222", command=self.show_register_screen)
        self.register_button.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        
        self.message_label = customtkinter.CTkLabel(self.current_frame, text="", text_color="red")
        self.message_label.grid(row=5, column=0, pady=(10, 20))

    def show_register_screen(self):
        """Cria e exibe a tela de registro."""
        if hasattr(self, 'current_frame'):
            self.current_frame.destroy()
        
        self.current_frame = customtkinter.CTkFrame(self)
        self.current_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.current_frame.grid_rowconfigure(5, weight=1)
        self.current_frame.grid_columnconfigure(0, weight=1)

        # Widgets da tela de registro
        label = customtkinter.CTkLabel(self.current_frame, text="Registro", font=customtkinter.CTkFont(size=24, weight="bold"))
        label.grid(row=0, column=0, pady=(20, 10))

        self.register_user_entry = customtkinter.CTkEntry(self.current_frame, placeholder_text="Nome de Usuário")
        self.register_user_entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.register_password_entry = customtkinter.CTkEntry(self.current_frame, placeholder_text="Senha", show="*")
        self.register_password_entry.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.register_button = customtkinter.CTkButton(self.current_frame, text="Registrar", command=self.register_user)
        self.register_button.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.back_button = customtkinter.CTkButton(self.current_frame, text="Já tem uma conta? Voltar", fg_color="transparent", text_color="gray", hover_color="#222222", command=self.show_login_screen)
        self.back_button.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        
        self.message_label = customtkinter.CTkLabel(self.current_frame, text="", text_color="red")
        self.message_label.grid(row=5, column=0, pady=(10, 20))

    def register_user(self):
        """Processa o registro de um novo usuário."""
        username = self.register_user_entry.get()
        password = self.register_password_entry.get()

        if not username or not password:
            self.message_label.configure(text="Nome de usuário e senha são obrigatórios.")
            return

        # Hash da senha para segurança
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            cursor = self.db.conn.cursor()
            
            # Verifica se o usuário já existe
            query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()

            if result:
                self.message_label.configure(text="Nome de usuário já existe.")
            else:
                # Insere o novo usuário
                insert_query = "INSERT INTO users (username, password) VALUES (%s, %s)"
                cursor.execute(insert_query, (username, hashed_password))
                self.db.conn.commit()
                self.message_label.configure(text="Registro bem-sucedido!", text_color="green")
                # Limpa os campos de entrada
                self.register_user_entry.delete(0, customtkinter.END)
                self.register_password_entry.delete(0, customtkinter.END)
                # Opcional: voltar para a tela de login
                self.after(1500, self.show_login_screen)

        except Error as e:
            self.message_label.configure(text=f"Erro de registro: {e}")
            print(f"Erro de registro: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def login_user(self):
        """Processa o login de um usuário."""
        username = self.login_user_entry.get()
        password = self.login_password_entry.get()

        if not username or not password:
            self.message_label.configure(text="Por favor, insira o nome de usuário e a senha.")
            return

        # Hash da senha para verificação
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            cursor = self.db.conn.cursor()
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (username, hashed_password))
            result = cursor.fetchone()

            if result:
                self.message_label.configure(text="Login bem-sucedido!", text_color="green")
                print("Login bem-sucedido!")
                self.after(500, self.show_hub_screen)
            else:
                self.message_label.configure(text="Nome de usuário ou senha incorretos.")

        except Error as e:
            self.message_label.configure(text=f"Erro de login: {e}")
            print(f"Erro de login: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
    
    def show_hub_screen(self):
        """
        Método placeholder para a tela principal (Hub).
        Aqui é onde você adicionará a lógica para mostrar as dívidas,
        despesas, etc.
        """
        if hasattr(self, 'current_frame'):
            self.current_frame.destroy()
        
        self.current_frame = customtkinter.CTkFrame(self)
        self.current_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.current_frame.grid_rowconfigure(0, weight=1)
        self.current_frame.grid_columnconfigure(0, weight=1)
        
        hub_label = customtkinter.CTkLabel(self.current_frame, text="Bem-vindo ao Hub Financeiro!", font=customtkinter.CTkFont(size=20, weight="bold"))
        hub_label.grid(row=0, column=0, padx=20, pady=20)
        
        logout_button = customtkinter.CTkButton(self.current_frame, text="Sair", command=self.show_login_screen)
        logout_button.grid(row=1, column=0, padx=20, pady=10)

class DBConnector:
    """
    Classe para gerenciar a conexão e operações com o banco de dados MySQL.
    """
    def __init__(self):
        self.conn = None
        
    def connect(self):
        """Estabelece a conexão com o banco de dados."""
        try:
            self.conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            if self.conn.is_connected():
                print("Conexão com o banco de dados bem-sucedida.")
            else:
                 print("Não foi possível conectar ao banco de dados.")

        except Error as e:
            print(f"Erro ao conectar ao banco de dados MySQL: {e}")
            
    def create_user_table(self):
        """Cria a tabela 'users' se ela não existir."""
        if not self.conn or not self.conn.is_connected():
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL
                )
            """)
            print("Tabela 'users' verificada/criada com sucesso.")
            self.conn.commit()
        except Error as e:
            print(f"Erro ao criar a tabela 'users': {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

if __name__ == "__main__":
    app = App()
    app.mainloop()
