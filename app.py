
from models.conecte_bd import (
     pega_usuarios, dados_user, pega_id, dados_card, inserir_usuario, inserir_receitas, inserir_cc, inserir_despesas, pega_despesas_cartao, pega_despesas, dados_receita, inserir_assinatura
     )

from utils.helper import(
    gerar_opcoes_meses, controle_data_parc, mysql_para_obj, data_para_mysql, formatar_moeda, data_para_exibicao, controle_data_parc_cc
)

from time import sleep

#interface gráfica 
import customtkinter as ctk

#Calendário e data e tempo
from tkcalendar import DateEntry
from datetime import datetime
from dateutil.relativedelta import relativedelta
import locale

#gráficos
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from collections import defaultdict 

#configura a aparência
ctk.set_appearance_mode('dark')

#Configuração de lingua - PTBR
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')


class Login(ctk.CTk):
    """Classe Login herda de ctk.CTK - configura a interface para receber os dados do usuário e faz a verificação no BD."""

    def __init__(self):
        super().__init__()
        self.title('Sistem de Login')
        self.geometry('350x400')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=0)

        self.label = ctk.CTkLabel(self, text="Faça seu Login", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.grid(row=0, column=0, pady=20)

        self.usuario_entry = ctk.CTkEntry(self, placeholder_text="Usuário")
        self.usuario_entry.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.senha_entry = ctk.CTkEntry(self, placeholder_text="Senha", show="*")
        self.senha_entry.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.botao_enter = ctk.CTkButton(self, text="Entrar", command=self.validar_login, 
                                         fg_color="#000200", hover_color="#FC0404")
        self.botao_enter.grid(row=3, column=0, padx=20, pady=10)
        self.bind("<Return>", lambda event: self.botao_enter.invoke())

        self.registrar = ctk.CTkButton(self, text="Registrar", command=self.abrir_tela_registro,
                                       fg_color="#000200", hover_color="#FC0404")
        self.registrar.grid(row=4, column=0, padx=20, pady=10)

        self.status_label = ctk.CTkLabel(self, text="", text_color="red")
        self.status_label.grid(row=5, column=0, pady=5)

    def validar_login(self):
        """ Valida o login que o usuário inseriu na entry"""
        
        usuario = self.usuario_entry.get()
        senha = self.senha_entry.get()
        login_sucesso = False
        usuario_logado = usuario

        for _, v in enumerate(pega_usuarios()):
            if usuario == v[2] and senha == v[3]:
                login_sucesso = True
                break
         
        if login_sucesso:
            self.status_label.configure(text='Login feito com sucesso', text_color='green')
            self.update_idletasks() # Atualiza a UI para mostrar a mensagem
            sleep(2)
            self.destroy()

            # Abre a janela principal (Gerenciador de Tarefas)
            main_app = Main_app(logged_in_username=usuario_logado)
            main_app.mainloop()
        else:
            self.status_label.configure(text='Login Incorreto!', text_color='red')

    def nome_usuario(self):
        return self.usuario
    

    def abrir_tela_registro(self):
        """ Direciona o usuário para fazer cadastro chamando a classe Registro_usuario"""
        
        # Passa a própria instância da tela de login para a tela de registro
        register_window = Registro_usuario(self, login_instance=self)
        #self.status_label.configure(text='Abrindo tela de registro...', text_color='blue')
        
        # A mainloop() não é chamada para toplevels, elas são gerenciadas pelo master.
        self.wait_window(register_window) #Pausa a janela de login até a popup fechar



class Registro_usuario(ctk.CTkToplevel):
    """Classe para registro: configuração da interface para receber dados e a inserção dos dados no BD. (inserir_usuario)"""

    def __init__(self,  master=None, login_instance=None):
        super().__init__(master)

        self.master = master # A referência à janela pai (opcional, mas útil)
        self.login_instance = login_instance


        self.title("Registrar Novo Usuário")
        self.geometry("350x500")
        self.transient(master) # Faz a popup aparecer sobre a janela principal e fechar com ela
        self.grab_set() # Bloqueia interações com a janela principal enquanto a popup está aberta
        self.focus_set() # Define o foco para esta janela

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=0)

        ctk.CTkLabel(self, text="Crie sua nova conta", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=15)

        self.nome_completo = ctk.CTkEntry(self, placeholder_text="Nome Completo")
        self.nome_completo.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.sal_fixo = ctk.CTkEntry(self, placeholder_text="Salário Fixo por mês")
        self.sal_fixo.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
            
        self.novo_usuario = ctk.CTkEntry(self, placeholder_text="Novo Usuário")
        self.novo_usuario.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.nova_senha = ctk.CTkEntry(self, placeholder_text="Nova Senha", show="*")
        self.nova_senha.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.rep_nova_senha = ctk.CTkEntry(self, placeholder_text="Repita a senha", show="*")
        self.rep_nova_senha.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        self.botao_registrar = ctk.CTkButton(self, text="Confirmar Registro", command=self.processar_registro)
        self.botao_registrar.grid(row=6, column=0, padx=20, pady=10, sticky="ew")

        self.status_label = ctk.CTkLabel(self, text="", text_color="red")
        self.status_label.grid(row=7, column=0, pady=5)


    def processar_registro(self):
        """Processa o registro - pega os dados inseridos, verifica e guarda no BD"""

        nome_comp = self.nome_completo.get().strip()
        usuario = self.novo_usuario.get().strip()
        senha1 = self.nova_senha.get().strip()
        senha2 = self.rep_nova_senha.get().strip()
        sal_fixo = self.sal_fixo.get().strip()


        if not usuario or not senha1 or not senha2:
            self.status_label.configure(text='Por favor, preencha todos os campos!', text_color='red')
            self.update_idletasks()
            sleep(1)
            return

        if senha1 == senha2:
            retorno = inserir_usuario(nome_comp, usuario, senha1, sal_fixo)

            if retorno:
                self.status_label.configure(text='Os dados foram inseridos com sucesso!', text_color='green')
                self.update_idletasks()
                sleep(2)

                self.status_label.configure(text=f'usuário: {usuario} Já pode fazer login no sistema! ', text_color='blue')
                self.update_idletasks()
                sleep(6)

                self.destroy()
            else:
                self.status_label.configure(text='Não foi possível registrar, contate o adm do sistema...', text_color='red')
                self.update_idletasks()
        else:
            self.status_label.configure(text='As senhas não correspondem!', text_color='red')
            self.update_idletasks()



class Main_app(ctk.CTk):
    """ Classe Main - app principal, configuração de interface, listamento de tarefas do BD. Intereção com app, atualição, delete, inserção... (CRUD)"""

    def __init__(self, logged_in_username=None):
        super().__init__()
        self.title("Controle Financeiro")
        self.geometry("1500x800")

        self.__dict__['usuario_logado'] = logged_in_username
        
        self.user_id = pega_id(self.usuario_logado)
        self.dados_usuario = dados_user(self.user_id)

        self.data_atual = datetime.now()
        self.mes_atual = self.data_atual.month
        self.prox_mes =  (self.data_atual + relativedelta(months=1)).month
        self.seg_prox_mes =  (self.data_atual + relativedelta(months=2)).month

        opcoes = gerar_opcoes_meses()
        self.nomes_datas = [
            opcoes.get(self.mes_atual, 'Mês inválido'),
            opcoes.get(self.prox_mes, 'Mês inválido'),
            opcoes.get(self.seg_prox_mes, 'Mês inválido'),
            
        ]
        self.mes_atual_str = opcoes.get(self.mes_atual)
        self.prox_mes_str = opcoes.get(self.prox_mes)
        self.seg_prox_mes_str = opcoes.get(self.seg_prox_mes)

        self.dados_cartoes = dados_card(self.user_id)
        self.nomes_cartoes = [c.get('nome_cartao') for c in self.dados_cartoes]

        self.grid_rowconfigure(0, weight=0) # Linha para o frame superior (usuário e add tarefa)
        self.grid_rowconfigure(1, weight=1) 
        self.grid_columnconfigure(0, weight=1)

        self.top_section_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_section_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.top_section_frame.grid_columnconfigure(0, weight=0) # primeira coluna para label usuário
        self.top_section_frame.grid_columnconfigure(0, weight=1) # segunda coluna para botão sair

        if self.usuario_logado: 
            self.nomeusuario_label = ctk.CTkLabel(self.top_section_frame,
                                               text=f"Bem-vindo, {self.dados_usuario.get('nome_completo')}!",
                                               font=ctk.CTkFont(size=16, weight="bold"))
            
        else:
            self.nomeusuario_label = ctk.CTkLabel(self.top_section_frame,
                                               text="Bem-vindo!",
                                               font=ctk.CTkFont(size=16, weight="bold"))
            
        self.nomeusuario_label.grid(row=0, column=0, pady=(0, 10), sticky="w")
            
        self.btn_att_app = ctk.CTkButton(self.top_section_frame, text="Atualizar", command=self.att_app, width=80,
                                        fg_color="#0400FF", hover_color="#7D0081")
        
        self.btn_att_app.grid(row=0, column=1,sticky="e")
        

        self.mes_vigente_label = ctk.CTkLabel(self.top_section_frame, text=f"Mês : ", font=ctk.CTkFont(size=16, weight="bold"))

        self.mes_vigente_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")

        self.menu_mes = ctk.CTkOptionMenu(self.top_section_frame, values=self.nomes_datas, command=self.trocar_mes)

        self.menu_mes.grid(row=0, column=3, padx=10, pady=5)
            
        self.botao_sair = ctk.CTkButton(self.top_section_frame, text="Sair", command=self.voltar_Plogin, width=80,
                                        fg_color="#FF0000", hover_color="#810000")
        
        self.botao_sair.grid(row=0, column=4,sticky="e") #coluna 2 alinhado a direita

        #Primeira Label da janela   
        

        

        #-------------------------------------------------------------------------------------
        # Frame para agrupar os botões de cadastro
        self.cadastro_frame = ctk.CTkFrame(self.top_section_frame, fg_color="transparent")
        self.cadastro_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")
        self.cadastro_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1) # Distribui o espaço entre os botões
        #---------------------------------------------------------------------------------------
        #---------------------------------------------------------------------------------------

        # Botões
        self.btn_receitas = ctk.CTkButton(self.cadastro_frame, text="Cadastar Receitas", command=self.abrir_receitas)
        self.btn_receitas.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.btn_despesas = ctk.CTkButton(self.cadastro_frame, text="Cadastrar Despesas", command=self.abrir_despesas)
        self.btn_despesas.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.btn_cc = ctk.CTkButton(self.cadastro_frame, text="Cadastrar C.Crédito", command=self.abrir_cc)
        self.btn_cc.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.btn_assin = ctk.CTkButton(self.cadastro_frame, text="Cadastrar Assinaturas", command=self.abrir_assinaturas)
        self.btn_assin.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        self.label_cc = ctk.CTkLabel(self.cadastro_frame, text="Selecione o Cartão:")
        self.label_cc.grid(row=0, column=4, padx=10, pady=5)

        self.menu_cartoes = ctk.CTkOptionMenu(self.cadastro_frame, values=self.nomes_cartoes)
        self.menu_cartoes.grid(row=1, column=4, padx=10, pady=5)

        self.det_despesas_cc = ctk.CTkButton(self.cadastro_frame, text="Detalhar", command=self.abrir_det_cc)
        self.det_despesas_cc.grid(row=1, column=5, padx=5, pady=5, sticky="ew")


        
        # -------------------------------------------------------------------------
        # FRAME DE CONTEÚDO PRINCIPAL (Main Content) - DEVE SER DEFINIDO AQUI
        # -------------------------------------------------------------------------
        self.main_content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Configuração de expansão das colunas do conteúdo principal
        self.main_content_frame.grid_columnconfigure(0, weight=2) # Tabela (Grande)
        self.main_content_frame.grid_columnconfigure(1, weight=1) # Gráfico (Pequeno)
        self.main_content_frame.grid_rowconfigure(0, weight=1)


        # -------------------------------------------------------------------------
        # FRAME DA TABELA DETALHADA (AGORA PODE SER DEFINIDO
        # -------------------------------------------------------------------------

        self.tabela_frame = ctk.CTkScrollableFrame(
        self.main_content_frame, 
        label_text=f"Pagamentos Detalhados: {self.mes_atual_str} / {self.data_atual.year}"
        )


        self.tabela_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew") # Coluna 0

        # Chamar o método para preencher a tabela ao iniciar
        self.preencher_total_dividas(self.user_id)


        # -------------------------------------------------------------------------
        # FRAME DO GRÁFICO (AGORA PODE SER DEFINIDO)
        # -------------------------------------------------------------------------
        self.grafico_frame = ctk.CTkFrame(self.main_content_frame)
        self.grafico_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew") # Coluna 1
        self.grafico_frame.grid_columnconfigure(0, weight=1)
        self.grafico_frame.grid_rowconfigure(0, weight=1)

        # Gerar o gráfico ao iniciar
        
        self.gerar_grafico_mensal()


        #-------------------------------------------------------------------------------------
        # Frame para agrupar card saldo do mês

        self.frame_resumo = ctk.CTkFrame(self.top_section_frame, width=250, height=100, corner_radius=15, # Bordas arredondadas (estil card moderno)
        border_width=2    # Espessura da borda que vai mudar de cor
        )
        self.frame_resumo.grid(row=1, column=6, padx=20, pady=10, sticky="n")

        self.label_titulo_resumo = ctk.CTkLabel(
        self.frame_resumo, 
        text="SALDO DO MÊS", 
        font=ctk.CTkFont(size=12, weight="bold")
        )
        self.label_titulo_resumo.pack(pady=(10, 0))

        self.label_valor_saldo = ctk.CTkLabel(
        self.frame_resumo, 
        text="R$ 0,00", 
        font=ctk.CTkFont(size=24, weight="bold")
        )
        self.label_valor_saldo.pack(pady=(0, 10), padx=20)

        self.atualizar_cores_saldo(self.dados_usuario.get('sal_fixo'), self.preencher_total_dividas(self.user_id))




    #------ Chamada das classes ---------

    def abrir_receitas(self):
        
        register_window = Cadastrar_receitas(self, self.user_id, login_instance=self)

        self.wait_window(register_window) 


    def abrir_despesas(self):
        register_window = Cadastrar_despesas(self, self.user_id, self.dados_cartoes, login_instance=self)

        self.wait_window(register_window)


    def abrir_cc(self):
        register_window = Cadastrar_car_cred(self, self.user_id, login_instance=self)

        self.wait_window(register_window)


    def abrir_det_cc(self):

        nome_selecionado = self.menu_cartoes.get()
        id_card = None

        for i in self.dados_cartoes:
            if i.get('nome_cartao') == nome_selecionado:
                id_card = i.get('id_cartao')

        if id_card:

            register_window = Despesas_cc(self, self.user_id, id_card, nome_card=nome_selecionado)

            self.wait_window(register_window)
        else:
            print("Erro: Cartão não encontrado")
    

    def abrir_assinaturas(self):

        register_window = Cadastrar_assinaturas(self, self.user_id, self.dados_cartoes)

        self.wait_window(register_window)


    # --------- Lógica do sistema ------------

    def trocar_mes(self, escolha=None):

        print("Botão clicado! Chamando com vigente False")

        for widget in self.tabela_frame.winfo_children():
            widget.destroy()

        for widget in self.grafico_frame.winfo_children():
            widget.destroy()
        
        if self.mes_atual_str == escolha:
            controle_mes = 1
            att_mes = self.preencher_total_dividas(self.user_id)
            self.gerar_grafico_mensal()

        elif self.prox_mes_str == escolha:
            controle_mes = 2
            att_mes = self.preencher_total_dividas(self.user_id, controle_mes)
            self.gerar_grafico_mensal(controle_mes=2)

        elif self.seg_prox_mes_str == escolha:
            controle_mes = 3
            att_mes = self.preencher_total_dividas(self.user_id, controle_mes)
            self.gerar_grafico_mensal(controle_mes=3)

        self.atualizar_cores_saldo(self.dados_usuario.get('sal_fixo'), att_mes, controle_mes)

        
            

            

        self.tabela_frame._label.configure(text=f"Pagamentos Detalhados: {escolha} / {self.data_atual.year}")


    def att_app(self):

        self.config(cursor="watch")
        self.update() 

        self.preencher_total_dividas(self.user_id)
        self.gerar_grafico_mensal()
    

        self.config(cursor="")
        print("Dashboard atualizado com sucesso! 🚀")


    def atualizar_cores_saldo(self, sal_fixo, despesa, controle_mes=1):

        receitas = dados_receita(self.user_id)
        receitas_fornecidas = 0.0

        prox_mes =  (self.data_atual + relativedelta(months=1))
        seg_prox_mes =  (self.data_atual + relativedelta(months=2))
        

        for dado in receitas:
            data_obj = mysql_para_obj(dado.get('data'))
            valor = float(dado.get('valor_recebido'))

            if controle_mes == 1: #mes_atual
                if self.data_atual.month == data_obj.month and self.data_atual.year == data_obj.year:
                    receitas_fornecidas = receitas_fornecidas +  valor
                    print(f"Soma Mes 1: + {valor}") # Print de Debug

            elif controle_mes == 2: #prox_mes
                if prox_mes.month == data_obj.month and prox_mes.year == data_obj.year:
                    receitas_fornecidas = valor
                    print(f"Soma Mes 2: + {valor}") # Print de Debug

            elif controle_mes == 3: #seg_prox_mes
                if seg_prox_mes.month == data_obj.month and seg_prox_mes.year == data_obj.year:
                    receitas_fornecidas += valor
                    print(f"Soma Mes 3: + {valor}") # Print de Debug


        receita_total = (float(sal_fixo) + receitas_fornecidas)
        saldo =  receita_total - float(despesa)


        if saldo > (receita_total * 0.03):
            cor_status = "#2ecc71" # Verde (Sucesso)
        elif saldo >= 0:
            cor_status = "#f1c40f" # Amarelo (No limite)
        else:
            cor_status = "#e74c3c" # Vermelho (Prejuízo)

        # Aplica a cor na borda do Frame e no texto do Saldo
        self.frame_resumo.configure(border_color=cor_status)
        self.label_valor_saldo.configure(text=f"{formatar_moeda(saldo)}", text_color=cor_status)


    def gerar_grafico_mensal(self, controle_mes= 1):

        print(f"Calculando dados : Está {controle_mes}")

        for widget in self.grafico_frame.winfo_children():
            widget.destroy()


        gastos_por_categoria = defaultdict(float)
        total_previsto = 0.0
    
        # Pegamos os dados necessários
        id_cartoes = [d.get('id_cartao') for d in self.dados_cartoes]
        desp_avulsas = pega_despesas(self.user_id)

        #DESPESAS DE CARTÃO
        for id_cc in id_cartoes:
            desp_cc = pega_despesas_cartao(self.user_id, id_cc)
        
            for desp in desp_cc:
                data_compra = mysql_para_obj(desp.get('data_compra'))
                dia_venc = desp.get('vencimento_fatura')
                fechamento = desp.get('fechamento_fatura')
                parcelas = desp.get('parcelas')

                # Verifica se entra na fatura atual
                resultado = controle_data_parc_cc(data_compra, fechamento, dia_venc, parcelas, controle_mes= controle_mes)
                _, entra_na_fatura, _ = resultado

                if entra_na_fatura:
                    valor_mensal = desp.get('valor_total') / parcelas
                    # SOMA NO DICIONÁRIO USANDO A CATEGORIA
                    categoria = desp.get('categoria', 'Outros')
                    gastos_por_categoria[categoria] += float(valor_mensal)
                    total_previsto += float(valor_mensal)

        # parte avulsas
        for desp in desp_avulsas:
            primeira_parc = mysql_para_obj(desp.get('primeira_parc'))
            data_compra = mysql_para_obj(desp.get('data_compra'))
            parcelas = desp.get('parcelas')
            dia_venc = desp.get('dia_vencimento')
        
            # Usando sua função de controle para avulsas
            resultado = controle_data_parc(data_compra, primeira_parc, dia_venc , parcelas, controle_mes = controle_mes)
            _, entra_no_mes, _ = resultado

            if entra_no_mes:
                valor_mensal = desp.get('valor_total') / parcelas
                categoria = desp.get('categoria', 'Outros')
                gastos_por_categoria[categoria] += float(valor_mensal)
                total_previsto += float(valor_mensal)

        #Verifica se tem algo para mostrar
        if total_previsto == 0:
            ctk.CTkLabel(self.grafico_frame, text="Nenhum gasto para este mês.").grid(row=0, column=0, padx=20, pady=20)
            return

        # Prepara os dados para o Matplotlib
        categorias = list(gastos_por_categoria.keys())
        totais = list(gastos_por_categoria.values())

        # 5. Criação do Gráfico
        fig, ax = plt.subplots(figsize=(5, 5), facecolor='#2b2b2b') # Cor de fundo igual ao CTk
        ax.pie(
            totais, 
            labels=categorias, 
            autopct='%1.1f%%', 
            startangle=90,
            textprops={'fontsize': 8, 'color': 'white'}
        )
        ax.axis('equal')
    
        # Título (Ajuste o gerar_opcoes_meses conforme sua estrutura)
        ax.set_title(f"Distribuição de Gastos\nTotal: R$ {total_previsto:,.2f}", color='white', fontsize=12)

        # 6. Renderização no CustomTkinter
        canvas = FigureCanvasTkAgg(fig, master=self.grafico_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, sticky="nsew")
        canvas.draw()

    
    def preencher_total_dividas(self, id_user, controle_mes = 1):

        print(f"Calculando dados: Está {controle_mes}")

        for widget in self.tabela_frame.winfo_children():
            widget.destroy()

        despesas = pega_despesas(id_user) 
        cartoes = dados_card(id_user)     

        total_avulsas = 0
        total_cards = 0


        lista_faturas_resumo = []

        if cartoes:
            for cartao in cartoes:
                nome_cartao = cartao.get('nome_cartao')
                id_cartao = cartao.get('id_cartao') 
            
                despesas_do_cartao = pega_despesas_cartao(id_user, id_cartao)
            
                total_deste_cartao = 0
                data_vencimento_fatura = None

                if despesas_do_cartao:

                    for desp in despesas_do_cartao:

                        data_compra = mysql_para_obj(desp.get('data_compra'))
                        dia_venc = desp.get('vencimento_fatura')
                        fechamento = desp.get('fechamento_fatura')
                        parcelas = desp.get('parcelas')


                        resultado = controle_data_parc_cc(data_compra, fechamento, dia_venc, parcelas, controle_mes= controle_mes)
                        _, entra_na_fatura, controle_data = resultado

                        if entra_na_fatura:
                            valor_mensal = desp.get('valor_total') / parcelas
                            total_deste_cartao += valor_mensal
                            data_vencimento_fatura = controle_data 

                        

                # Se o cartão tem fatura para pagar, guardamos na lista!
                if total_deste_cartao > 0:
                    lista_faturas_resumo.append({
                        'local': f"Fatura - {nome_cartao}",
                        'valor': total_deste_cartao,
                        'vencimento': data_vencimento_fatura
                    })

                


    
        # Se tiver despesas avulsas OU tiver faturas de cartão, a gente desenha a tabela
        if despesas or lista_faturas_resumo:
        
            # Cabeçalho
            ctk.CTkLabel(self.tabela_frame, text="Local", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self.tabela_frame, text="Parcelas", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5, sticky="e")
            ctk.CTkLabel(self.tabela_frame, text="Mensalidade", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self.tabela_frame, text="Vencimento", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5, sticky="w")

            linha = 1


            if despesas:
                for _, dados in enumerate(despesas):
                    data_compra = mysql_para_obj(dados.get('data_compra'))
                    primeira_parc = mysql_para_obj(dados.get('primeira_parc'))
                    dia_venc = primeira_parc.day
                
                    resultado_avulso = controle_data_parc(data_compra, primeira_parc, dia_venc, dados.get('parcelas'), controle_mes= controle_mes)
                    str_parcela, control_parc, control_mes = resultado_avulso

                    dia_venc = int(primeira_parc.day)

                    if control_mes:
                        data_fatura = control_mes.replace(day=dia_venc)
                    else:
                        data_fatura = datetime.now().replace(day=dia_venc)

                    if control_parc:
                        valor_mensal = dados.get('valor_total') / dados.get('parcelas')
                    
                        ctk.CTkLabel(self.tabela_frame, text=dados.get('local')).grid(row=linha, column=0, padx=5, pady=2, sticky="w")
                        ctk.CTkLabel(self.tabela_frame, text=str_parcela).grid(row=linha, column=1, padx=3, pady=1, sticky="w")
                        ctk.CTkLabel(self.tabela_frame, text=formatar_moeda(valor_mensal), justify=ctk.LEFT, text_color="green").grid(row=linha, column=2, padx=5, pady=2, sticky="e")
                        ctk.CTkLabel(self.tabela_frame, text=data_para_exibicao(data_fatura)).grid(row=linha, column=3, padx=5, pady=2, sticky="w")

                        total_avulsas += valor_mensal
                    
                        linha += 1

            # Desenha o Resumo das Faturas dos Cartões
            for fatura in lista_faturas_resumo:
                ctk.CTkLabel(self.tabela_frame, text=fatura['local']).grid(row=linha, column=0, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.tabela_frame, text="-").grid(row=linha, column=1, padx=3, pady=1, sticky="w") # Fatura não tem "1/12"
                ctk.CTkLabel(self.tabela_frame, text=formatar_moeda(fatura['valor']), justify=ctk.LEFT, text_color="red").grid(row=linha, column=2, padx=5, pady=2, sticky="e")
            
                # Formata a data se ela não vier vazia
                venc_str = data_para_exibicao(fatura['vencimento']) if fatura['vencimento'] else "N/A"
                ctk.CTkLabel(self.tabela_frame, text=venc_str).grid(row=linha, column=3, padx=5, pady=2, sticky="w")

                total_cards += fatura['valor']

                linha += 1

            ctk.CTkLabel(
                self.tabela_frame, 
                text="TOTAL DA FATURA:", 
                font=ctk.CTkFont(weight="bold", size=14)
            ).grid(row=linha, column=0, columnspan=2, padx=5, pady=(20, 5), sticky="e")

            ctk.CTkLabel(
                self.tabela_frame, 
                text=formatar_moeda((total_avulsas + total_cards)), 
                font=ctk.CTkFont(weight="bold", size=14), 
                text_color="red" 
            ).grid(row=linha, column=2, padx=5, pady=(20, 5), sticky="e")

            self.tabela_frame.grid_columnconfigure(2, weight=1)

            return (total_avulsas + total_cards)

        else:
            ctk.CTkLabel(self.tabela_frame, text="Nenhum pagamento previsto.").grid(row=0, column=0, padx=10, pady=10)
            self.tabela_frame.grid_columnconfigure(2, weight=1)


    def voltar_Plogin(self):
        """ Método para voltar para a tela de login (botão 'Sair')"""

        self.nomeusuario_label.configure(text=f'Até a próxima {self.usuario_logado} !', text_color='red')
        self.update_idletasks()

        sleep(1)

        self.destroy()
        from app import Login

        login_app = Login()
        login_app.mainloop()





# -------- Classes de Cadastro --------------  

class Cadastrar_receitas(ctk.CTkToplevel):

    def __init__(self,  parent=None, user_id=None, login_instance=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id

        self.title("Registrar Novas Receitas")
        self.geometry("400x600")
        self.transient(parent) # Faz a popup aparecer sobre a janela principal e fechar com ela
        self.grab_set() # Bloqueia interações com a janela principal enquanto a popup está aberta
        self.focus_set() # Define o foco para esta janela

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=0)

        ctk.CTkLabel(self, text="Cadastre Seus Ganhos", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=15)

        self.valor = ctk.CTkEntry(self, placeholder_text="Valor Ganho")
        self.valor.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.descricao = ctk.CTkEntry(self, placeholder_text="Descrição")
        self.descricao.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.label_data_compra = ctk.CTkLabel(self, text="Data de recebimento:", font=ctk.CTkFont(size=16, weight="bold"))
        self.label_data_compra.grid(row=3, column=0)
            
        self.data_recebimento = DateEntry(self, width=12, background='darkblue',
                            foreground='white', borderwidth=2, year=2026, 
                            locale='pt_BR', date_pattern='dd/mm/yyyy')
        self.data_recebimento.grid(row=4, column=0, padx=10, pady=10)

        self.botao_salvar = ctk.CTkButton(self, text="Salvar Dados", command=self.salvar_dados)
        self.botao_salvar.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        self.status_label = ctk.CTkLabel(self, text="", text_color="red")
        self.status_label.grid(row=6, column=0, pady=5)



    def salvar_dados(self):
        """ Verifica e salva os dados no db """

        valor = self.valor.get().strip()
        descricao = self.descricao.get().strip()
        data_obj = self.data_recebimento.get_date()

        # Formata o objeto datetime para a string 'AAAA-MM-DD'
        data_mysql = data_para_mysql(data_obj)
        
        try:
            valor = float(valor.replace(',', '.'))
        except ValueError:
            print('Valor precisa ser um número valido, decimal!')


        if not valor or not descricao or not data_obj:
            self.status_label.configure(text='Por favor, preencha todos os campos!', text_color='red')
            self.update_idletasks()
            sleep(1)
            return
        else:
            retorno = inserir_receitas(self.user_id, valor, descricao, data_mysql)

        if retorno:
            self.status_label.configure(text='Os dados foram inseridos com sucesso!', text_color='green')
            self.update_idletasks()
            sleep(2)
                
        else:
            self.status_label.configure(text='Não foi possível salvar dados, contate o adm do sistema...', text_color='red')
            self.update_idletasks()

 
class Cadastrar_despesas(ctk.CTkToplevel):

    def __init__(self,  parent=None, user_id=None, dados_cartoes =None, login_instance=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.dados_cartoes = dados_cartoes

        self.title("Registrar Novas Despesas")
        self.geometry("800x900")
        self.transient(parent)
        self.grab_set() 
        self.focus_set() 

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # O frame rolavel ocupará toda a janela

        self.nomes_cartoes = [c.get('nome_cartao') for c in self.dados_cartoes]

        self.data_atual = datetime.now().date()

        # ------------------------------------------------------------------------
        # PASSO 1: Criar o CTkScrollableFrame e posicioná-lo
        # Ele será o master de todo o conteúdo da janela
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Cadastre Suas Despesas")
        self.scrollable_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Configuração da grade interna do frame rolavel
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        # ------------------------------------------------------------------------

        # TODOS OS WIDGETS USAM self.scrollable_frame COMO SEU MASTER

        # LOCAL DA COMPRA
        self.local = ctk.CTkEntry(self.scrollable_frame, placeholder_text="Local da compra*")
        self.local.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        # TOTAL DA COMPRA
        self.valor_total = ctk.CTkEntry(self.scrollable_frame, placeholder_text="Valor total da compra*")
        self.valor_total.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # PARCELAS
        parcelas_opcoes = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        self.menu_parcelas = ctk.CTkOptionMenu(self.scrollable_frame, values=parcelas_opcoes)
        self.menu_parcelas.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        self.menu_parcelas.set("N° Parcelas")

        # DESCRIÇÃO DA COMPRA
        self.descricao = ctk.CTkEntry(self.scrollable_frame, placeholder_text="Descrição da compra")
        self.descricao.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # CATEGORIA
        categorias = ['Lazer', 'Roupas', 'Essencial', 'Estudos', 'Saúde', 'Empréstimo', ' Hobby', 'Trabalho']
        self.categoria = ctk.CTkOptionMenu(self.scrollable_frame, values=categorias)
        self.categoria.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.categoria.set("Categoria")

        # DATA DA COMPRA
        self.label_data_compra = ctk.CTkLabel(self.scrollable_frame, text="Data da Compra:", font=ctk.CTkFont(size=16, weight="bold"))
        self.label_data_compra.grid(row=5, column=0)

        self.campo_data_compra = DateEntry(self.scrollable_frame, width=12, background='darkblue',
                            foreground='white', borderwidth=2, year=2026, 
                            locale='pt_BR', date_pattern='dd/mm/yyyy')
        self.campo_data_compra.grid(row=6, column=0, padx=10, pady=10)

        # data primeira parcela - se não for no cartão
        self.label_primeira_dc = ctk.CTkLabel(self.scrollable_frame, text="Data do Primeiro Pagamento: (obs. Não preencher se a compra for no C. Crédito)", font=ctk.CTkFont(size=12, weight="bold"))
        self.label_primeira_dc.grid(row=7, column=0)

        self.campo_primeira_dc = DateEntry(self.scrollable_frame, width=12, background='darkblue',
                            foreground='white', borderwidth=2, year=2026, 
                            locale='pt_BR', date_pattern='dd/mm/yyyy')
        self.campo_primeira_dc.grid(row=8, column=0, padx=10, pady=10)
        
        #Seleção de cartão de crédito
        if self.nomes_cartoes:
            
            self.car_cred = ctk.CTkOptionMenu(self.scrollable_frame, values=self.nomes_cartoes)
            self.car_cred.grid(row=9, column=0, padx=20, pady=10, sticky="ew")
            self.car_cred.set("Cartão de Cobrança")
        else:
            self.car_cred = ctk.CTkOptionMenu(self.scrollable_frame, values=[' ', ' ',])
            self.car_cred.grid(row=9, column=0, padx=20, pady=10, sticky="ew")
            self.car_cred.set("Cadastre cartões na área destinada")

        # Linha 10 (Antiga Linha 9)
        self.botao_salvar = ctk.CTkButton(self.scrollable_frame, text="Salvar Dados", command=self.salvar_dados)
        self.botao_salvar.grid(row=10, column=0, padx=20, pady=20, sticky="ew") # Maior padding para destacar

        # Linha 11 (Antiga Linha 10)
        self.status_label = ctk.CTkLabel(self.scrollable_frame, text="", text_color="red")
        self.status_label.grid(row=11, column=0, pady=5)


    def salvar_dados(self):
        """ Verifica e salva os dados no BD """

        dia_venc = None
        id_card = None
        verifica_pri_dc = False

        local = self.local.get().strip()
        valor_total = self.valor_total.get().strip()
        menu_parcelas_str = self.menu_parcelas.get()
        descricao = self.descricao.get().strip()
        categoria = self.categoria.get()
        dc_select = self.campo_data_compra.get_date()
        prim_dc_select = self.campo_primeira_dc.get_date()

        prim_dc_select_mysql = None

        if prim_dc_select != self.data_atual:
            dia_venc = prim_dc_select.day
            verifica_pri_dc = True
            prim_dc_select_mysql = data_para_mysql(prim_dc_select)

        car_cred = self.car_cred.get()

        # Formata o objeto datetime para a string 'AAAA-MM-DD' para mandar para o db
        dc_select_mysql = data_para_mysql(dc_select)
        


        if not local or not valor_total or categoria == "Categoria" or menu_parcelas_str == "N° Parcelas":
            self.status_label.configure(text='Preencha Local, Valor Total, Categoria , N° Parcelas e Data da compra', text_color='red')
            self.after(2000, lambda: self.status_label.configure(text='')) # Usa after() para não travar
            return
    
        try:
            parcelas = int(menu_parcelas_str)
             # Tenta converter o valor para float
            valor_total = float(valor_total.replace(",", "."))
        except ValueError:
            self.status_label.configure(text='Valor Total ou Parcelas devem ser números válidos!', text_color='red')
            self.after(2000, lambda: self.status_label.configure(text=''))
            return
        
        
        tem_cartao = car_cred != "Selecione um Cartão"

        
        if not tem_cartao and not verifica_pri_dc:
            # Se não tem cartão E não tem dia de vencimento, falha!
            self.status_label.configure(text='Informe um Cartão OU Data do primeiro pagamento', text_color='red')
            self.after(4000, lambda: self.status_label.configure(text=''))
            return # Sai do método

        
        if tem_cartao:
            for dado in self.dados_cartoes:
                if dado.get('nome_cartao') == car_cred:
                    id_card = dado.get('id_cartao')

        #Chama o método para inserir no bd - retorna se tiver sucesso
        retorno = inserir_despesas(self.user_id, local, valor_total, parcelas,  descricao, categoria, dc_select_mysql, prim_dc_select_mysql, dia_venc, id_card)


        if retorno:
            self.status_label.configure(text='Os dados foram inseridos com sucesso!', text_color='green')
            self.update_idletasks()

            if hasattr(self.master, 'trocar_mes'): 
                self.master.trocar_mes()

            self.limpar_campos()
            
            self.after(3000, lambda: self.status_label.configure(text=''))

                
        else:
            self.status_label.configure(text='Não foi possível salvar dados, contate o adm do sistema...', text_color='red')
            self.update_idletasks()


    

    def limpar_campos(self):
        """Limpa todos os campos de entrada do formulário de despesas."""
        
        # Limpa CTkEntry's
        self.local.delete(0, ctk.END)
        self.valor_total.delete(0, ctk.END)
        self.descricao.delete(0, ctk.END)

        
        # Reseta CTkOptionMenu's para seus valores padrão
        self.menu_parcelas.set("N° Parcelas")
        self.categoria.set("Categoria")
        self.car_cred.set("Selecione um Cartão")

        self.campo_data_compra.set_date(self.data_atual)
        self.campo_primeira_dc.set_date(self.data_atual)
        

                

class Cadastrar_car_cred(ctk.CTkToplevel):

    def __init__(self,  parent=None, user_id=None, login_instance=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id

        self.title("Registrar Novos Cartões de Crédito")
        self.geometry("400x600")
        self.transient(parent)
        self.grab_set() 
        self.focus_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=0)

        ctk.CTkLabel(self, text="Cadastre Seus Cartões de Crédito", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=15)

        self.nome_cc = ctk.CTkEntry(self, placeholder_text="Nome do Cartão*")
        self.nome_cc.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.limite = ctk.CTkEntry(self, placeholder_text="Limite do Cartão*")
        self.limite.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.dia_fechamento = ctk.CTkEntry(self, placeholder_text="Dia do fechamento*")
        self.dia_fechamento.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.dia_vencimento = ctk.CTkEntry(self, placeholder_text="Dia do vencimento*")
        self.dia_vencimento.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.botao_salvar = ctk.CTkButton(self, text="Salvar Dados", command=self.salvar_dados)
        self.botao_salvar.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        self.status_label = ctk.CTkLabel(self, text="", text_color="red")
        self.status_label.grid(row=6, column=0, pady=5)


    def salvar_dados(self):
        """ Verifica e salva os dados no BD """


        """VERIFICAR SE O USUÁRIO NÃO ESTÁ COLOCANDO UM NOME DE CARTÃO REPETIDO"""


        nome_cc = self.nome_cc.get().strip()
        limite = self.limite.get().strip()
        dia_f = self.dia_fechamento.get().strip()
        dia_v = self.dia_vencimento.get().strip()
                

        if not nome_cc or not limite or not dia_f or not dia_v:
            self.status_label.configure(text='Por favor, preencha todos os campos obrigarórios', text_color='red')
            self.update_idletasks()
            sleep(1)
            return
        else:
            retorno = inserir_cc(self.user_id, nome_cc, limite, dia_f, dia_v)

        if retorno:
            self.status_label.configure(text='Os dados foram inseridos com sucesso!', text_color='green')
            self.update_idletasks()
            sleep(2)

            #self.destroy()
                
        else:
            self.status_label.configure(text='Não foi possível salvar os dados, contate o adm do sistema...', text_color='red')
            self.update_idletasks()


class Cadastrar_assinaturas(ctk.CTkToplevel):

    def __init__(self, parent=None, user_id=None, dados_cartoes=None):
        super().__init__(parent)
        self.title("Gerenciar Assinaturas")
        self.geometry("600x600")
        self.grab_set() 
        self.focus_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.user_id = user_id
        self.dados_cartoes = dados_cartoes 

        self.data_atual = datetime.now()
        
        # --- UI scrollable Com Título ---
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Cadastre Suas Assinaturas")
        self.scrollable_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Configuração da grade interna do frame rolavel
        self.scrollable_frame.grid_columnconfigure(0, weight=1)


        # --- UI - Campos de Entrada ---
        self.entry_nome = ctk.CTkEntry(self.scrollable_frame, placeholder_text="Nome (Ex: Netflix, Academia)", width=300)
        self.entry_nome.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.entry_valor = ctk.CTkEntry(self.scrollable_frame, placeholder_text="Valor Mensal (R$)", width=300)
        self.entry_valor.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.entry_desc = ctk.CTkEntry(self.scrollable_frame, placeholder_text="Descrição (Opcional)", width=300)
        self.entry_desc.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.data_aquisicao = DateEntry(self.scrollable_frame, width=12, background='darkblue',
                            foreground='white', borderwidth=2, year=2026, 
                            locale='pt_BR', date_pattern='dd/mm/yyyy')
        
        self.data_aquisicao.grid(row=4, column=0, padx=10, pady=10)

        self.label_primeira_dc = ctk.CTkLabel(self.scrollable_frame, text="Data do Primeiro Pagamento: (obs. Não preencher se a compra for no C. Crédito)", font=ctk.CTkFont(size=12, weight="bold"))
        self.label_primeira_dc.grid(row=5, column=0)

        self.campo_prim_dp = DateEntry(self.scrollable_frame, width=12, background='darkblue',
                            foreground='white', borderwidth=2, year=2026, 
                            locale='pt_BR', date_pattern='dd/mm/yyyy')
        self.campo_prim_dp.grid(row=6, column=0, padx=10, pady=10)

        # Menu de Categorias
        categorias = ['Lazer', 'Essencial', 'Estudos', 'Saúde', ' Hobby','Streaming',]
        self.menu_cat = ctk.CTkOptionMenu(self.scrollable_frame, values=categorias, width=300)
        self.menu_cat.grid(row=7, column=0, padx=20, pady=10, sticky="ew")
        self.menu_cat.set("Selecione a Categoria")

        # Menu de Cartões utilizando de dados_cartos - list(dict)
        nomes_cartoes = ["Cartão de Cobrança - Sem Cartão"] + [c['nome_cartao'] for c in self.dados_cartoes]
        self.menu_cc = ctk.CTkOptionMenu(self.scrollable_frame, values=nomes_cartoes, width=300)
        self.menu_cc.grid(row=8, column=0, padx=20, pady=10, sticky="ew")
        self.menu_cc.set("Cartão de Cobrança - Sem Cartão")

        # --- Botão Salvar ---
        self.btn_salvar = ctk.CTkButton(self.scrollable_frame, text="Confirmar Assinatura", command=self.salvar_dados, fg_color="#2c3e50", hover_color="#34495e")
        self.btn_salvar.grid(row=9, column=0, padx=20, pady=10, sticky="ew")

        self.status_label = ctk.CTkLabel(self.scrollable_frame, text="", text_color="red")
        self.status_label.grid(row=10, column=0, pady=5)


    def salvar_dados(self):
        """ Verifica e salvar dados no db

        Args: 
            objeto self
        Returns:

        
        """
        dia_venc = None
        verifica_data_pp = False

        id_card = None
        
        so_data = self.data_atual.date()

        nome = self.entry_nome.get().strip()
        valor = self.entry_valor.get().strip()
        descricao = self.entry_desc.get().strip()
        data_aq =  self.data_aquisicao.get_date()
        data_pp = self.campo_prim_dp.get_date()
        categoria = self.menu_cat.get().strip()
        cartao = self.menu_cc.get().strip()

        #preparando para mandar para o db

        data_aq_mysql = data_para_mysql(data_aq)

        data_pp_mysql = None

        if data_pp != so_data:
            dia_venc = data_pp.day
            verifica_data_pp = True
            data_pp_mysql = data_para_mysql(data_pp)

        if not nome or not valor or categoria == "Selecione a Categoria":
            self.status_label.configure(text='Preencha Nome, Valor, Categoria ,', text_color='red')
            self.after(2000, lambda: self.status_label.configure(text='')) 
            return

        try:
             # Converte o valor para float
            valor = float(valor.replace(",", "."))
        except ValueError:
            self.status_label.configure(text=" 'Valor' deve ser números válidos!", text_color='red')
            self.after(2000, lambda: self.status_label.configure(text=''))
            return
        
        #Verifica de o usuário selecionou um cartão
        tem_cartao = cartao != "Cartão de Cobrança - Sem Cartão"
        if tem_cartao:
            for dado in self.dados_cartoes:
                if dado.get('nome_cartao') == cartao:
                    id_card = dado.get('id_cartao')

        #Verifica se data_pp ou seleção do cartão não foi alterado 
        if not verifica_data_pp and cartao == "Cartão de Cobrança - Sem Cartão":
            self.status_label.configure(text='Selecione uma data de primeiro pagamento ou um cartão de crédito ', text_color='red')
            self.after(2000, lambda: self.status_label.configure(text='')) 
            return
        
        #chama o método para inserir os dados no db e retorna se bem sucedido
        retorno = inserir_assinatura(self.user_id, nome, valor, descricao, data_aq_mysql, data_pp_mysql, dia_venc, categoria, id_card )

        #retorno do banco - texto de indicação
        if retorno:
            self.status_label.configure(text='Os dados foram inseridos com sucesso!', text_color='green')
            self.update_idletasks()

            """if hasattr(self.master, 'trocar_mes'): 
                self.master.trocar_mes()"""

            self.limpar_campos()
            
            self.after(3000, lambda: self.status_label.configure(text=''))

        else:
            self.status_label.configure(text='Não foi possível salvar dados, contate o adm do sistema...', text_color='red')
            self.update_idletasks()


    def limpar_campos(self):
        """Limpa todos os campos de entrada do formulário de assinaturas."""
        
        # Limpa CTkEntry's
        self.entry_nome.delete(0, ctk.END)
        self.entry_valor.delete(0, ctk.END)
        self.entry_desc.delete(0, ctk.END)

        
        # Reseta CTkOptionMenu's para seus valores padrão
        self.menu_cat.set("Selecione a Categoria")
        self.menu_cc.set("Cartão de Cobrança - Sem Cartão")

        self.data_aquisicao.set_date(self.data_atual)
        self.campo_prim_dp.set_date(self.data_atual)
        

        

#------------  Classe(s) de Detalhe(s) -----------

class Despesas_cc(ctk.CTkToplevel):
    
    def __init__(self, parent, id_user, id_card, nome_card, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.title(f"Detalhes: {nome_card}")
        self.geometry("1000x800")
        self.transient(parent)
        
        # Garante que a janela fique na frente
        self.attributes("-topmost", True) 

        self.data_atual = datetime.now()
        self.mes_atual = self.data_atual.month
        self.prox_mes =  (self.data_atual + relativedelta(months=1)).month
        self.seg_prox_mes =  (self.data_atual + relativedelta(months=2)).month

        opcoes = gerar_opcoes_meses()
        self.nomes_datas = [
            opcoes.get(self.mes_atual, 'Mês inválido'),
            opcoes.get(self.prox_mes, 'Mês inválido'),
            opcoes.get(self.seg_prox_mes, 'Mês inválido'),
            
        ]
        self.mes_atual_str = opcoes.get(self.mes_atual)
        self.prox_mes_str = opcoes.get(self.prox_mes)
        self.seg_prox_mes_str = opcoes.get(self.seg_prox_mes)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Onde fica o frame principal das tabelas

        self.label_titulo = ctk.CTkLabel(self, text=f"Fatura: {nome_card}", font=("Arial", 22, "bold"))
        self.label_titulo.grid(row=0, column=0, pady=20)
        

        self.main_content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Configuração de expansão das colunas do conteúdo principal
        self.main_content_frame.grid_columnconfigure(0, weight=1) # Tabela (Grande)
        self.main_content_frame.grid_columnconfigure(1, weight=1) 
        self.main_content_frame.grid_rowconfigure(0, weight=1)

        # mês vigente
        self.tabela_frame = ctk.CTkScrollableFrame(
        self.main_content_frame, 
        label_text=f"Pagamentos Detalhados: {self.mes_atual_str} / {self.data_atual.year}"
        )
        self.tabela_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Aqui você vai criar os dois frames (Mês Vigente e Próximo)
        # e chamar seu método de busca detalhada (aquele do INNER JOIN!)
        self.tabela_vigente(id_user, id_card)

        #Próximo mês
        self.tabela_frame_prox = ctk.CTkScrollableFrame(self.main_content_frame, label_text=f"Pagamentos Detalhados: {self.prox_mes_str} / {self.data_atual.year}" )
        self.tabela_frame_prox.grid(row=0, column=1, padx=10, pady=10, sticky="nsew") # Coluna 1
        self.tabela_frame_prox.grid_columnconfigure(0, weight=1)
        self.tabela_frame_prox.grid_rowconfigure(0, weight=1)

        self.tabela_prox(id_user, id_card)



    def tabela_vigente(self, id_user, id_card, controle_mes = 1):


        for widget in self.tabela_frame.winfo_children():
            widget.destroy()

        dados_desp_card = pega_despesas_cartao(id_user, id_card)

        data_teste = mysql_para_obj('2026-06-02')

        total_fatura = 0

        data_atual = data_atual = datetime.now()


        

        if dados_desp_card:

                        # Cabeçalho
            ctk.CTkLabel(self.tabela_frame, text="Local.", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self.tabela_frame, text="Parcelas", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5, sticky="e")
            ctk.CTkLabel(self.tabela_frame, text="Valor", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self.tabela_frame, text="Vencimento", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5, sticky="w")

            linha = 1

            for _, dado  in enumerate(dados_desp_card):

                """"'despesa_id', 'local', 'valor_total', 'parcelas','descricao', 'categoria', 'data_compra', 
                        'nome_cartao', 'limite_cartao', 'fechamento_fatura', 'vencimento_fatura'"""
                
                data_compra = mysql_para_obj(dado.get('data_compra'))
                fecha_fatura = dado.get('fechamento_fatura')
                dia_venc = dado.get('vencimento_fatura')
                parcelas = dado.get('parcelas')


                resultado = controle_data_parc_cc(data_compra, fecha_fatura ,dia_venc, parcelas, controle_mes=controle_mes)

                str_parc, control_parc, controle_data = resultado


                if control_parc:
                    
                    valor_mensal = dado.get('valor_total') / dado.get('parcelas')
                    total_fatura += valor_mensal

                    ctk.CTkLabel(self.tabela_frame, text=dado.get('local')).grid(row=linha, column=0, padx=5, pady=2, sticky="w")

                    ctk.CTkLabel(self.tabela_frame, text=str_parc).grid(row=linha, column=1, padx=3, pady=1, sticky="w")

                    ctk.CTkLabel(self.tabela_frame, text=formatar_moeda(valor_mensal),justify=ctk.LEFT, text_color="green").grid(row=linha, column=2, padx=5, pady=2, sticky="e")

                    ctk.CTkLabel(self.tabela_frame, text=data_para_exibicao(controle_data)).grid(row=linha, column=3, padx=5, pady=2, sticky="w")

                    linha += 1
            
            ctk.CTkLabel(
                self.tabela_frame, 
                text="TOTAL DA FATURA:", 
                font=ctk.CTkFont(weight="bold", size=14)
            ).grid(row=linha, column=0, columnspan=2, padx=5, pady=(20, 5), sticky="e")

            ctk.CTkLabel(
                self.tabela_frame, 
                text=formatar_moeda(total_fatura), 
                font=ctk.CTkFont(weight="bold", size=14), 
                text_color="red" 
            ).grid(row=linha, column=2, padx=5, pady=(20, 5), sticky="e")
            



        self.tabela_frame.grid_columnconfigure(2, weight=1)



    def tabela_prox(self, id_user, id_card, controle_mes = 2):

        for widget in self.tabela_frame_prox.winfo_children():
            widget.destroy()

        dados_desp_card = pega_despesas_cartao(id_user, id_card)

        data_teste = mysql_para_obj('2026-06-02')

        total_fatura = 0

        data_atual = data_atual = datetime.now()


        

        if dados_desp_card:

                        # Cabeçalho
            ctk.CTkLabel(self.tabela_frame_prox, text="Local.", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self.tabela_frame_prox, text="Parcelas", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5, sticky="e")
            ctk.CTkLabel(self.tabela_frame_prox, text="Valor", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self.tabela_frame_prox, text="Vencimento", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5, sticky="w")

            linha = 1

            for _, dado  in enumerate(dados_desp_card):

                """"'despesa_id', 'local', 'valor_total', 'parcelas','descricao', 'categoria', 'data_compra', 
            'nome_cartao', 'limite_cartao', 'fechamento_fatura', 'vencimento_fatura'"""
                
                data_compra = mysql_para_obj(dado.get('data_compra'))
                fecha_fatura = dado.get('fechamento_fatura')
                parcelas = dado.get('parcelas')
                dia_venc = dado.get('vencimento_fatura')

                resultado = controle_data_parc_cc(data_compra, fecha_fatura, dia_venc, parcelas, controle_mes= controle_mes)

                str_parc, control_parc, controle_data = resultado

                if control_parc:
                    
                    valor_mensal = dado.get('valor_total') / dado.get('parcelas')
                    total_fatura += valor_mensal

                    ctk.CTkLabel(self.tabela_frame_prox, text=dado.get('local')).grid(row=linha, column=0, padx=5, pady=2, sticky="w")

                    ctk.CTkLabel(self.tabela_frame_prox, text=str_parc).grid(row=linha, column=1, padx=3, pady=1, sticky="w")

                    ctk.CTkLabel(self.tabela_frame_prox, text=formatar_moeda(valor_mensal),justify=ctk.LEFT, text_color="green").grid(row=linha, column=2, padx=5, pady=2, sticky="e")

                    ctk.CTkLabel(self.tabela_frame_prox, text=data_para_exibicao(controle_data)).grid(row=linha, column=3, padx=5, pady=2, sticky="w")

                    linha += 1

            ctk.CTkLabel(
                self.tabela_frame_prox, 
                text="TOTAL DA FATURA:", 
                font=ctk.CTkFont(weight="bold", size=14)
            ).grid(row=linha, column=0, columnspan=2, padx=5, pady=(20, 5), sticky="e")
            
            ctk.CTkLabel(
                self.tabela_frame_prox, 
                text=formatar_moeda(total_fatura), 
                font=ctk.CTkFont(weight="bold", size=14), 
                text_color="red" 
            ).grid(row=linha, column=2, padx=5, pady=(20, 5), sticky="e")

        self.tabela_frame.grid_columnconfigure(2, weight=1)














def encerrar_sistema():
    # 1. Para o loop principal
    login_app.quit()
    
    # 2. Destrói a janela e limpa os widgets da memória
    login_app.destroy()
    
    # 3. Força a saída do processo Python para liberar o terminal
    import sys
    sys.exit()

# Garante que tanto o "X" quanto qualquer botão de fechar chamem a função
    login_app.protocol("WM_DELETE_WINDOW", encerrar_sistema)

# Se tiver um botão de sair, use:
# btn_sair = ctk.CTkButton(master, text="Sair", command=encerrar_sistema)

login_app = ctk.CTk()
login_app.protocol("WM_DELETE_WINDOW", encerrar_sistema)

if __name__ == "__main__":
    # Inicia a primeira tela (tela de login)
    login_app = Login()
    login_app.mainloop()