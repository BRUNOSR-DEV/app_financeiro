# 💰 APP_FINANCEIRO | Gestão de Fluxo de Caixa Desktop

![Status do Projeto](https://img.shields.io/badge/Status-Finalizando-green?style=for-the-badge)
![Python Version](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![Database](https://img.shields.io/badge/MySQL-8.0+-orange?style=for-the-badge&logo=mysql)

Um ecossistema robusto para gerenciamento financeiro pessoal, focado em **Experiência do Usuário (UX)**, **Modularidade de Código** e **Integridade de Dados**.

---

## 🚀 Diferenciais da Engenharia de Software

Este projeto não é apenas um CRUD. Ele foi construído utilizando conceitos modernos de arquitetura:

* **Padrão Mediator (Controller):** Centralização da lógica de comunicação entre frames via `crud_app.py`.
* **Data Access Layer (DAL):** Camada de persistência isolada em `conecte_bd.py`, utilizando **Row Mappers** para converter resultados SQL em dicionários Python.
* **Sanitização Proativa:** Validação de inputs em tempo real via **Regex** no Front-end para evitar TypeErrors.
* **Hot-Reload UI:** Atualização inteligente da interface (método `att_app`) sem a necessidade de reinicializar a aplicação.

---
## 🛠️ Tecnologias e Bibliotecas

* **Ideação e Arquitetura:** Colaboração técnica via Gemini AI (Google).
* **Gestão Ágil:** Kanban via Trello (Documentado em `/DOCS` [Quadro Trello](https://trello.com/b/PaYLzi3t/appfinanceiro)).
* **Design de Banco de Dados:** MySQL Workbench.
* **GUI:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (Visual Dark Mode moderno).
* **Áudio:** Pygame (Feedback sonoro para operações do sistema).

## 📈 Metodologia de Desenvolvimento

Foi utilizada a metodologia Kanban para o mapeamento de ciclo de vida das tarefas, garantindo rastreabilidade e foco em entrega de valor incremental. Este projeto contou com o suporte técnico e consultoria de arquitetura da Gemini (Google AI), auxiliando na estruturação de padrões de projeto (Mediator, DAL), refino de UX/UI e lógica de banco de dados.

---
## 📁 Estrutura do Projeto

```text
APP_FINANCEIRO/
├── assets/         # Recursos visuais e sonoros (feedbacks auditivos)
├── docs/           # Documentação técnica, MER e logs do Kanban
├── models/         # Camada de banco de dados (Query Engine)
├── ui/             # View Layer (Telas, Formulários e Listagens)
├── utils/          # Helpers, Validadores Regex e Audio Engine
└── main.py         # Bootstrapper e Gerenciador de Ciclo de Vida

---
🔧 Como Rodar o Projeto
Clone o repositório:

Bash: git clone [Link](https://github.com/BRUNOSR-DEV/app_financeiro.git)

Ative o ambiente virtual (venv):
Bash: No Windows .\avir_af\Scripts\activate Instale as dependências:

Instale as dependências:
Bash: pip install customtkinter mysql-connector-python 

Configure o Banco de Dados: 
Certifique-se de que o MySQL está rodando e configure as credenciais no arquivo config.ini.

Execute:
Bash: python main.py
