📝 Controle de Finanças (Desktop App)
Este é um projeto de aplicação desktop para gerenciamento de finanças, focado em  operações de CRUD (Create, Read, Update, Delete) e persistência de dados com MySQL.

🚀 Funcionalidades
Cadastro de Usuários: Interface para novos usuários.

Gestão de Tasks: Adicionar, listar e deletar tarefas vinculadas ao banco de dados.

Interface Moderna: Utilização da biblioteca customtkinter para um visual Dark Mode profissional.

Arquitetura Modular: Separação de responsabilidades entre lógica de interface (gerenciador.py) e conexão com banco (conecte_bd.py).

🛠 Tecnologias e Bibliotecas
Linguagem: Python 3.11

Interface Gráfica: CustomTkinter

Banco de Dados: MySQL

Ambiente Virtual: venv (vir_gt)

📁 Estrutura do Projeto
gerenciador.py: Ponto de entrada da aplicação e lógica da UI.

models/conecte_bd.py: Funções de manipulação de dados (queries SQL).

config.ini: Configurações de ambiente e banco de dados.

assets/: Arquivos de imagem e ícones do projeto.

🔧 Como Rodar o Projeto
Clone o repositório:

Bash git clone https://github.com/BRUNOSR-DEV/app_financeiro.git Ative o ambiente virtual:

Bash No Windows .\vir_gt\Scripts\activate Instale as dependências:

Bash pip install customtkinter mysql-connector-python Configure o Banco de Dados: Certifique-se de que o MySQL está rodando e configure as credenciais no arquivo config.ini.

Execute:

Bash python gerenciador.py
