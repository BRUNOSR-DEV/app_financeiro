# 💰 APP_FINANCEIRO | Gestão de Fluxo de Caixa Desktop

![Status do Projeto](https://img.shields.io/badge/Status-Finalizando-green?style=for-the-badge)
![CI/CD Pipeline](https://github.com/BRUNOSR-DEV/app_financeiro/actions/workflows/ci.yml/badge.svg)
![Python Version](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![Database](https://img.shields.io/badge/MySQL-8.0+-orange?style=for-the-badge&logo=mysql)


Um ecossistema comercialmente resiliente para gerenciamento, projeção e análise de capacidade de controle financeiro. Desenvolvido sob os pilares de **Programação Orientada a Objetos (POO)**,  **Arquitetura Limpa** e **Integridade de Dados** o sistema mitiga falhas humanas e imprecisões matemáticas comuns em planilhas financeiras tradicionais.

---

## 🚀 Diferenciais da Engenharia de Software

Este projeto abandonou scripts planos e estruturas "burras" para se tornar um software blindado, utilizando padrões de design de mercado:

* **Gerenciamento Ágil (Kanban Rastreável):** O ciclo de vida do projeto foi orquestrado utilizando a metodologia Kanban via **Trello**.Cada funcionalidade, refatoração de banco ou implementação de teste foi mapeada para garantir previsibilidade, foco em valor incremental e eliminação de desperdícios (débito técnico).
* **Motor de Simulação & Mocks Temporais Avançados:** Sandbox de Projeção Financeira (Simulação Volátil em Memória): O ecossistema introduz uma funcionalidade avançada de simulação preditiva integrada aos formulários nativos de despesas e cartões de crédito. O usuário pode simular o impacto de novas compras parceladas ou recorrentes para o mês vigente e para os próximos 5 meses... eliminando completamente a poluição do banco de dados de produção.
* **Padrão Mediator (Orquestração de Interface):** Centralização da lógica de comunicação entre frames via `crud_app.py` (Pattern Facade) e controle de ciclo de vida mestre sem estouro de pilha na *Super Main*.
* **Encapsulamento Rígido de Domínio:** Atributos críticos (como senhas, salários e limites) são privados/protegidos (`__`). Nenhuma camada visual corrompe o negócio, pois o domínio rejeita valores inválidos em tempo de execução via **Setters de Validação**.
* **Separação de Conceitos com DTOs:** Uso de *Data Transfer Objects* (`DespesaDetalhadoDTO` e `AssinaturaDetalhadoDTO`) para transportar o resultado de queries complexas de `JOIN`, mantendo a UI em modo de leitura única (*Read-Only*).
* **Data Access Layer (DAL):** Camada de persistência isolada em `repositorios.py`, utilizando **Row Mappers** para converter resultados SQL em dicionários Python.
* **Sanitização Proativa & Hot-Reload:** Validação de inputs em tempo real via **Regex** no Front-end para evitar TypeErrors e atualização inteligente da interface (método `att_app`) sem reinicializar a aplicação.

---

## 🏛️ Arquitetura do Banco de Dados (v2.0)

O sistema opera em uma modelagem relacional centralizada (*Star Schema* Orgânico), onde a entidade `Usuario` atua como o núcleo do sistema.

### 🌌 Filosofia de Modelagem (Do Céu ao Inferno)
* **Camada Celestial (Topo):** A tabela de `receitas` funciona como a entrada soberana do sistema, gerenciando o aporte financeiro.
* **O Núcleo Central (Sol):** A tabela `usuarios` centraliza credenciais, chaves criptográficas e dados de auditoria (`criado_em`, `ativo`).
* **A Camada do Submundo (Base):** As tabelas de `cartoes_credito`, `despesas` e a nova tabela de `assinaturas` gerenciam o fluxo de passivos estruturais.

```text
       [ RECEITAS ]  (Céu - Entradas)
            │
            ▼
      [ USUARIOS ]   (O Sol - Núcleo Central)
       /    │    \
      ▼     ▼     ▼
 [CARTÕES] [DESPESAS] [ASSINATURAS] (Submundo - Saídas e Passivos)

```
---

## 🧠 Motores de Negócio & Inteligência Contábil
### 🧮  Algoritmo de Distribuição Residual
Para evitar a perda invisível de centavos em dízimas de parcelamentos (ex: R$ 100,00 divididos em 3x gerando R$ 99,99), o sistema utiliza a biblioteca Decimal com quantize, interceptando a sobra matemática e injetando-a automaticamente na última parcela do vetor:$$\text{Vetor de Parcelas: } [33.33, \; 33.33, \; 33.34] \implies \text{Total Cravado: } R\$ \, 100,00$$

---

## 🗺️ Motor Temporal Dinâmico e Geolocalização de Feriados
A engenharia de vencimentos realiza uma leitura nativa da localização do Windows do usuário, injetando o estado federativo dinamicamente na biblioteca holidays. Se uma fatura vence em um feriado regional (ex: 9 de Julho em SP) ou final de semana, o motor recalcula e empurra o fluxo automaticamente para o próximo dia útil, eliminando projeções falsas de juros.

---

## 🔐 Segurança On-the-Fly Migration (Bcrypt)
Camada de segurança por criptografia de via única (Hashing) utilizando Bcrypt com fator de custo configurado em 12 rounds. O repositório executa uma migração em tempo de execução: senhas legadas em texto limpo são validadas diretamente e, no primeiro login bem-sucedido, o sistema gera o hash automaticamente e sobrescreve o registro antigo no banco de dados de forma transparente.

---

## 🧪 Testes Automatizados e Esteira CI/CD (DevOps)
A estabilidade do ecossistema é garantida por uma suíte de 23 testes automatizados (Unitários + Integração) integrados a um pipeline de nuvem.
Testes de Integração (Banco Real): Utiliza o framework unittest acoplado ao gerenciador de conexões do MySQLdb. Aplica isolamento total com SET FOREIGN_KEY_CHECKS = 0 no setUp de limpeza de tabelas, permitindo que os testes rodem em paralelo sem travar em constraints.
Mocks Temporários: Injeção estática de objetos datetime.date para testar viradas de mês automáticas independentemente do relógio da máquina local.

---

## 🚀 Pipeline GitHub Actions (Ambiente Docker Headless)
A cada commit na branch principal, o GitHub Actions dispara o workflow .github/workflows/ci.yml, executando as seguintes etapas em cerca de 1 minuto:

Inicializa o interpretador Python 3.13 em um ambiente Linux.
Levanta um container Docker oficial do MySQL 8.0 isolado na nuvem.
Executa a DDL centralizada respeitando a hierarquia de chaves estrangeiras.
Isolamento de Credenciais: Lê chaves dinâmicas via os.getenv(), mantendo as senhas locais protegidas no arquivo test_config.ini pelo .gitignore.
Tratamento Headless: Captura exceções preventivas no pygame.mixer.init() para impedir falhas catastróficas em servidores Linux sem hardware de áudio.

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
├── .github/workflows/   # Pipeline de Integração Contínua (GitHub Actions)
├── assets/              # Recursos de mídia e feedbacks sonoros (Pygame)
├── avir_af/             # Ambiente Virtual Python (Virtual Environment isolado)
├── docs/                # Documentações do projeto, scripts MySQL, prints temporais - Quadros KAMBAM e MER v2.0
├── htmlcov/             # Relatórios analíticos de cobertura de testes em HTML
├── models/              # Camada de Domínio (Entidades, Repositórios e DTOs e POO)
├── tests/               # Suíte de Testes Automatizados (Unitários e Integração)
├── ui/                  # View Layer (Telas CustomTkinter, Modais e Frames)
├── utils/               # Motores Contábeis, RegEx, Mocks e Auxiliares de Áudio
├── .coverage            # Dados brutos de cobertura gerados pelo Coverage.py
├── .gitignore           # Bloqueio de subida de binários, venv e arquivos com credenciais
├── config.ini           # Arquivo de configuração e credenciais de Produção (Local)
├── example_config.ini   # Template de exemplo para configuração do banco de produção
├── example_test_config.ini # Template de exemplo para configuração do banco de testes
├── main.py              # Bootstrapper (Orquestrador do Ciclo de Vida e Super Main)
├── README.md            # Manual de Engenharia e Documentação do Ecossistema
└── requirements.txt     # Manifesto de dependências e bibliotecas do ecossistema
```
---

## 🔧 Como Rodar o Projeto
Siga o passo a passo abaixo para levantar o ambiente virtual, instalar as dependências, criar a estrutura do banco de dados e rodar tanto a aplicação quanto a suíte de testes.

### 1. Clonar o Repositório e Acessar o Diretório
Bash: git clone [Link](https://github.com/BRUNOSR-DEV/app_financeiro.git)

### 2. Ativar o Ambiente Virtual (venv)
O projeto utiliza um ambiente virtual isolado chamado avir_af. No Windows, ative-o executando:

Bash:  .\avir_af\Scripts\activate 
(Nota: Certifique-se de que o prompt do seu terminal agora exibe (avir_af) no início da linha).

### 3. Instalar as Dependências do Ecossistema
Bash: pip install -r requirements.txt

### 4. Configurar a Infraestrutura do Banco de Dados (MySQL)
Certifique-se de que o seu servidor MySQL local (8.0+) está ativo e rodando.
Acesse o diretório DOCS/MER/ no seu projeto, onde está localizado o script SQL de criação das tabelas (.sql). execute o script no seu MySQL Workbench ou console para criar o esquema completo do banco v2.0 com a hierarquia correta de chaves estrangeiras.

### 5. Configurar as Chaves e Credenciais (.ini)
O sistema gerencia os ambientes de produção local e laboratório de testes através de arquivos separados. Nunca comite seus dados reais.

Para Rodar o Aplicativo Principal: Duplique o arquivo example_config.ini, renomeie a cópia para config.ini e insira as credenciais do seu banco de dados de produção local.

Para Rodar a Suíte de Testes Automatizados: Duplique o arquivo example_test_config.ini, renomeie para test_config.ini e insira as credenciais do seu banco de dados dedicado aos testes.

### 6. Executar a Suíte de Testes Locais
Para garantir que o motor de negócios e a camada de persistência estão 100% íntegros antes de subir a interface, execute os 23 testes automatizados via terminal:

Bash: python -m unittest discover -s tests

### 7. Inicializar o Aplicativo
Com os testes aprovados e as credenciais do config.ini prontas, dê o start no bootstrapper mestre para abrir a interface gráfica do CustomTkinter:

Bash: python main.py

