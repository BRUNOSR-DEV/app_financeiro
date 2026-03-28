
from models.conecte_bd import (
      inserir_usuario, inserir_receitas, inserir_cc, inserir_despesas, inserir_assinatura
     )

from utils.helper import(
    gerar_opcoes_meses, data_para_mysql
)

from tkcalendar import DateEntry
from datetime import datetime
from dateutil.relativedelta import relativedelta

from utils.audio_helper import tocar_notificacao 

import customtkinter as ctk
ctk.set_appearance_mode('dark')


class Registro_usuario(ctk.CTkToplevel):
    """Classe para registro: configuração da interface para receber dados e a inserção dos dados no BD. (inserir_usuario)"""

    def __init__(self,  parent=None, login_instance=None):
        super().__init__(parent)

        self.master = parent # A referência à janela pai (opcional, mas útil)
        self.login_instance = login_instance
        
        self.title("Registrar Novo Usuário")
        self.geometry("350x500")
        self.transient(parent) # Faz a popup aparecer sobre a janela principal e fechar com ela
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

            tocar_notificacao("erro")
            self.update_idletasks()
            self.after(3000, lambda: self.status_label.configure(text='')) 
            return

        if senha1 == senha2:
            retorno = inserir_usuario(nome_comp, usuario, senha1, sal_fixo)

            if retorno:
                self.status_label.configure(text='Os dados foram inseridos com sucesso!', text_color='green')
                tocar_notificacao("sucesso")
                self.update_idletasks()
                self.after(3000, lambda: self.status_label.configure(text='')) 

                self.status_label.configure(text=f'usuário: {usuario} Já pode fazer login no sistema! ', text_color='blue')
                self.update_idletasks()
                self.after(3000, lambda: self.status_label.configure(text='')) 

                self.destroy()
            else:
                self.status_label.configure(text='Não foi possível registrar, contate o adm do sistema...', text_color='red')
                tocar_notificacao('erro')
                self.update_idletasks()
        else:
            self.status_label.configure(text='As senhas não correspondem!', text_color='red')
            tocar_notificacao('erro')
            self.update_idletasks()



class Cadastrar_receitas(ctk.CTkFrame):

    def __init__(self,  parent=None, user_id=None, login_instance=None, callback = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id

        self.callback = callback

        self.data_atual = datetime.now().date()

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
            tocar_notificacao("erro")
            self.after(2000, lambda: self.status_label.configure(text=''))


        if not valor or not descricao or not data_obj:
            self.status_label.configure(text='Por favor, preencha todos os campos!', text_color='red')

            tocar_notificacao("erro")
            self.update_idletasks()
            self.after(2000, lambda: self.status_label.configure(text=''))
            return
        else:
            retorno = inserir_receitas(self.user_id, valor, descricao, data_mysql)

        if retorno:
            self.status_label.configure(text='Os dados foram inseridos com sucesso!', text_color='green')

            tocar_notificacao("sucesso")
            self.update_idletasks()
            self.after(2000, lambda: self.status_label.configure(text=''))

            self.limpar_campos()

            if self.callback:
                self.callback(escolha=gerar_opcoes_meses().get(data_obj.month))
   
        else:
            self.status_label.configure(text='Não foi possível salvar dados, contate o adm do sistema...', text_color='red')
            tocar_notificacao("erro")
            self.update_idletasks()
            self.after(2000, lambda: self.status_label.configure(text=''))


    def limpar_campos(self):

        self.valor.delete(0, ctk.END)
        self.descricao.delete(0, ctk.END)

        self.data_recebimento.set_date(self.data_atual)


#Cadastro de despesas
class Cadastrar_despesas(ctk.CTkFrame):

    def __init__(self,  parent=None, user_id=None, dados_cartoes =None, login_instance=None, callback=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.dados_cartoes = dados_cartoes
        self.callback = callback

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
        categorias = ['Essencial', 'Lazer', 'Hobby', 'Vestimenta/Acessórios', 'Evolução Pessoal', 'Saúde', 'Empréstimo', 'Reforma e Construção']
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
                            foreground='white', borderwidth=2, day=1, month=1, year=2050, 
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
        verifica_pri_dc = False

        local = self.local.get().strip()
        valor_total = self.valor_total.get().strip()
        menu_parcelas_str = self.menu_parcelas.get()
        descricao = self.descricao.get().strip()
        categoria = self.categoria.get()
        dc_select = self.campo_data_compra.get_date()
        prim_dc_select = self.campo_primeira_dc.get_date()

        prim_dc_select_mysql = None

        self.sentinela = self.data_atual.replace(day=1, month=1, year=2050)

        if prim_dc_select != self.sentinela:
            dia_venc = prim_dc_select.day
            verifica_pri_dc = True
            prim_dc_select_mysql = data_para_mysql(prim_dc_select)

        car_cred = self.car_cred.get()

        # Formata o objeto datetime para a string 'AAAA-MM-DD' para mandar para o db
        dc_select_mysql = data_para_mysql(dc_select)
        


        if not local or not valor_total or categoria == "Categoria" or menu_parcelas_str == "N° Parcelas":

            self.status_label.configure(text='Preencha Local, Valor Total, Categoria , N° Parcelas e Data da compra', text_color='red')
            tocar_notificacao('erro')
            self.after(3000, lambda: self.status_label.configure(text=''))
            return
    
        try:
            parcelas = int(menu_parcelas_str)
             # Tenta converter o valor para float
            valor_total = float(valor_total.replace(",", "."))
        except ValueError:
            self.status_label.configure(text='Valor Total ou Parcelas devem ser números válidos!', text_color='red')
            tocar_notificacao('erro')

            self.after(3000, lambda: self.status_label.configure(text=''))
            return
        
        
        tem_cartao = car_cred != "Selecione um Cartão"

        
        if not tem_cartao and not verifica_pri_dc:
            # Se não tem cartão E não tem dia de vencimento, falha!
            self.status_label.configure(text='Informe um Cartão OU Data do primeiro pagamento', text_color='red')
            tocar_notificacao('erro')
            self.after(3000, lambda: self.status_label.configure(text=''))
            return 

        
        if tem_cartao:
            id_card = None
            mes_vencimento = None
            for dado in self.dados_cartoes:
                if dado.get('nome_cartao') == car_cred:
                    id_card = dado.get('id_cartao')
                    dia_fechamento = dado.get('fechamento_fatura')
            
            if dc_select.day >= dia_fechamento:
                mes_vencimento = (dc_select + relativedelta(months=1)).month
            else:
                mes_vencimento = dc_select.month


        #Chama o método para inserir no bd - retorna se tiver sucesso condição para evitar valores desnecessrios no bd
        if tem_cartao and verifica_pri_dc:
            self.campo_primeira_dc.set_date(self.sentinela)
            prim_dc_select_mysql = None
            dia_venc = None

            self.status_label.configure(text='Como foi informado um Cartão a Data primeiro pagamento será desconsiderada', text_color='red')
            self.update_idletasks()
            self.after(3000, lambda: self.status_label.configure(text=''))

            retorno = inserir_despesas(self.user_id, local, valor_total, parcelas,  descricao, categoria, dc_select_mysql, prim_dc_select_mysql, dia_venc, id_card)

        else:
            retorno = inserir_despesas(self.user_id, local, valor_total, parcelas,  descricao, categoria, dc_select_mysql, prim_dc_select_mysql, dia_venc, id_card)


        if retorno:
            self.status_label.configure(text='Os dados foram inseridos com sucesso!', text_color='green')

            tocar_notificacao('sucesso')
            self.update_idletasks()

            if self.callback:
                self.callback(gerar_opcoes_meses().get(mes_vencimento))

            self.limpar_campos()
            
            self.after(3000, lambda: self.status_label.configure(text=''))

                
        else:
            self.status_label.configure(text='Não foi possível salvar dados, contate o adm do sistema...', text_color='red')
            tocar_notificacao('erro')
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
        self.campo_primeira_dc.set_date(self.sentinela)
        


class Cadastrar_car_cred(ctk.CTkFrame):

    def __init__(self,  parent=None, user_id=None, login_instance=None, nomes_cards =None, callback = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id

        self.callback = callback
        self.nomes_cards = nomes_cards

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

        nome_cc = self.nome_cc.get().strip()
        limite = self.limite.get().strip()
        dia_f = self.dia_fechamento.get().strip()
        dia_v = self.dia_vencimento.get().strip()
        
        #verifiva se já a o nome informado no bd
        for nome in self.nomes_cards:
            if nome == nome_cc:

                tocar_notificacao("erro")

                self.status_label.configure(text=f'Por favor, Não repitir nome de cartões, tente - ex: *{nome_cc}700', text_color='red')
                self.update_idletasks()

                self.after(2000, lambda: self.status_label.configure(text=''))
                return


        if not nome_cc or not limite or not dia_f or not dia_v:
            self.status_label.configure(text='Por favor, preencha todos os campos obrigarórios', text_color='red')
            tocar_notificacao("erro")

            self.update_idletasks()
            self.after(2000, lambda: self.status_label.configure(text=''))
            
            return
        else:
            retorno = inserir_cc(self.user_id, nome_cc, limite, dia_f, dia_v)

        if retorno:
            self.status_label.configure(text='Os dados foram inseridos com sucesso!', text_color='green')
            tocar_notificacao("sucesso")
            self.update_idletasks()
            
            self.after(2000, lambda: self.status_label.configure(text=''))

            self.limpar_campos()
            

                
        else:
            self.status_label.configure(text='Não foi possível salvar os dados, contate o adm do sistema...', text_color='red')

            tocar_notificacao("erro")
            self.update_idletasks()


    def limpar_campos(self):
        """Limpa todos os campos de entrada do formulário""" 
        
        self.nome_cc.delete(0, ctk.END)
        self.limite.delete(0, ctk.END)
        self.dia_fechamento.delete(0, ctk.END)
        self.dia_vencimento.delete(0, ctk.END)



class Cadastrar_assinaturas(ctk.CTkFrame):

    def __init__(self, parent=None, user_id=None, dados_cartoes=None, callback=None):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.callback = callback

        self.user_id = user_id
        self.dados_cartoes = dados_cartoes 

        self.data_atual = datetime.now().date()
        self.data_futuro = (self.data_atual + relativedelta(years=73)).replace(day=1, month=1) #set de data no futuro ddistante, para lógica
        
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
                            foreground='white', borderwidth=2, day=1, month=1, year=2099, 
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

        if data_pp != self.data_futuro:
            dia_venc = data_pp.day
            verifica_data_pp = True
            data_pp_mysql = data_para_mysql(data_pp)

            if data_pp.year == self.data_futuro.year:
                self.status_label.configure(text='Mude o ano da data de primeiro pagemento', text_color='red')

                tocar_notificacao("erro")
                self.after(3000, lambda: self.status_label.configure(text='')) 
                return

        if not nome or not valor or categoria == "Selecione a Categoria":

            self.status_label.configure(text='Preencha Nome, Valor, Categoria ,', text_color='red')
            tocar_notificacao("erro")
            self.after(3000, lambda: self.status_label.configure(text=''))
            return

        try:
             # Converte o valor para float
            valor = float(valor.replace(",", "."))
        except ValueError:
            self.status_label.configure(text=" 'Valor' deve ser números válidos!", text_color='red')
            tocar_notificacao("erro")

            self.after(3000, lambda: self.status_label.configure(text=''))
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
            tocar_notificacao("erro")

            self.after(3000, lambda: self.status_label.configure(text='')) 
            return
        
        #chama o método para inserir os dados no db e retorna se bem sucedido
        retorno = inserir_assinatura(self.user_id, nome, valor, descricao, data_aq_mysql, data_pp_mysql, dia_venc, categoria, id_card )

        #retorno do banco - texto de indicação
        if retorno:
            tocar_notificacao("sucesso")

            self.status_label.configure(text='Os dados foram inseridos com sucesso!', text_color='green')
            self.update_idletasks()

            self.limpar_campos()
            
            self.after(2000, lambda: self.status_label.configure(text=''))

            """if self.callback:
                self.callback()"""

        else:
            self.status_label.configure(text='Não foi possível salvar dados, contate o adm do sistema...', text_color='red')
            tocar_notificacao("erro")
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
        self.campo_prim_dp.set_date(self.data_futuro)
