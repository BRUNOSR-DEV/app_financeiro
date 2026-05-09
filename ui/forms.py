
from models.conecte_bd import (
      inserir_usuario, inserir_receita, inserir_cc, inserir_despesa, inserir_assinatura, atualizar_receita, atualiza_assinatura, atualizar_cartao, atualizar_despesa
     )

from utils.helper import(
    gerar_opcoes_meses, data_para_mysql, mysql_para_obj
)

from utils.typedDict import(Despesa_simulacao)

from tkcalendar import DateEntry
from datetime import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from utils.audio_helper import tocar_notificacao 

import customtkinter as ctk
ctk.set_appearance_mode('dark')


#Filho de Módulo Login (login_app.py)
class Cadastrar_usuarios(ctk.CTkFrame):
    """Classe para registro: configuração da interface para receber dados e a inserção dos dados no BD. (inserir_usuario)"""

    def __init__(self,  parent=None, cb_comandante_crud=None, cb_fechar=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.cdt_crud = cb_comandante_crud
        self.fechar = cb_fechar

        # --------------- Configuração da janela/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=0)

        ctk.CTkLabel(self, text="Crie sua nova conta", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=15)

        self.nome_completo = ctk.CTkEntry(self, placeholder_text="Nome Completo")
        self.nome_completo.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.sal_fixo = ctk.CTkEntry(self, placeholder_text="Salário Fixo por mês")
        self.sal_fixo.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
            
        self.novo_usuario = ctk.CTkEntry(self, placeholder_text="Novo Usuário")
        self.novo_usuario.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.nova_senha = ctk.CTkEntry(self, placeholder_text="Senha", show="*")
        self.nova_senha.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.rep_nova_senha = ctk.CTkEntry(self, placeholder_text="Repita a Senha", show="*")
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


        if not usuario or not senha1 or not senha2 or not sal_fixo:
            self.status_label.configure(text='Por favor, preencha todos os campos!', text_color='red')

            tocar_notificacao("dv_erro", True)
            self.update_idletasks()
            self.after(2000, lambda: self.status_label.configure(text='')) 
            return

        dados = {
            "nome_comp": nome_comp,
            "usuario": usuario,
            "senha": senha1,
            "sal_fixo": sal_fixo
        }

        if senha1 == senha2:
            retorno = self.cdt_crud(inserir=dados)

            if retorno:
                self.status_label.configure(text='Os dados foram inseridos com sucesso!', text_color='green')
                self.update_idletasks()

                self.after(2000, lambda: self.status_label.configure(text='')) 

                self.status_label.configure(text=f'Usuário: {usuario} Já pode fazer login no sistema! ', text_color='blue')
                self.update_idletasks()

                self.after(2000, lambda: self.status_label.configure(text=''))

                self.fechar()
                
            else:
                self.status_label.configure(text='Não foi possível registrar, contate o adm do sistema...', text_color='red')
                self.update_idletasks()

                self.after(2000, lambda: self.status_label.configure(text='')) 
                
        else:
            self.status_label.configure(text='As senhas não correspondem!', text_color='red')
            self.update_idletasks()

            self.after(2000, lambda: self.status_label.configure(text='')) 


#Filho de Módulo Receitas (crud_app.py)
class Cadastrar_receitas(ctk.CTkFrame):

    def __init__(self,  parent=None, user_id=None, callback_comandante_crud=None,  *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.cdt_crud = callback_comandante_crud

        # ---------------- Gerencimento de self ---------------------
        self.data_atual = datetime.now().date()
        self.sentinela = self.data_atual.replace(day=1, month=1, year=2099)

        # --------------- Configuração da janela/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Cadastre Seus Ganhos", font=("Arial", 18, "bold")).grid(row=0, column=0, pady=10)

        self.valor = ctk.CTkEntry(self, placeholder_text="Valor Ganho")
        self.valor.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.descricao = ctk.CTkEntry(self, placeholder_text="Descrição")
        self.descricao.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.label_data_compra = ctk.CTkLabel(self, text="Data de recebimento:", font=ctk.CTkFont(size=16, weight="bold"))
        self.label_data_compra.grid(row=3, column=0)
            
        self.data_recebimento = DateEntry(self, width=12, background='darkblue',
                            foreground='white', borderwidth=2, day=1, month=1, year=2099, 
                            locale='pt_BR', date_pattern='dd/mm/yyyy')
        self.data_recebimento.grid(row=4, column=0, padx=10, pady=10)

        self.botao_salvar = ctk.CTkButton(self, text="Salvar Dados", command=self.salvar_dados)
        self.botao_salvar.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        self.status_label = ctk.CTkLabel(self, text="", text_color="red")
        self.status_label.grid(row=6, column=0, pady=5)



    def salvar_dados(self, id_rec=None, atualizar=False):
        """ Verifica e salva os dados no db """

        valor = self.valor.get().strip()
        descricao = self.descricao.get().strip()
        data_obj = self.data_recebimento.get_date()

        # Formata o objeto datetime para a string 'AAAA-MM-DD'
        data_mysql = data_para_mysql(data_obj)
        
        try:
            valor = Decimal(str(valor.replace(',', '.')))

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
        
        sucesso = False

        dados = {
                'valor': valor, 
                'descricao': descricao,
                'data_mysql': data_mysql
            }
        
        if not atualizar: #inserir os dados novos

            dados['user_id'] =  self.user_id
            sucesso = self.cdt_crud(inserir=dados)

            msg_ok = "INSERIDOS"
            msg_falha = "Não foi possível SALVAR os dados, contate o adm do sistema...'"

        else: #Fazer atualização
            
            dados['id_rec'] = id_rec
            sucesso = self.cdt_crud(atualizar=dados)

            msg_ok = "ATUALIZADOS"
            msg_falha = "Não foi possível ATUALIZAR os dados, contate o adm do sistema..."


        if sucesso:
            self.status_label.configure(text=f'Os dados foram {msg_ok} com sucesso!', text_color='green')
            self.update_idletasks()
            self.after(2000, lambda: self.status_label.configure(text=''))

            if atualizar:
                self.controla_campos(None)

        else:
            self.status_label.configure(text=f'{msg_falha}', text_color='red')
            self.update_idletasks()
            self.after(2000, lambda: self.status_label.configure(text=''))



    def controla_campos(self, dados= None): #dados = dict(valor_recebido,descricao,data)
        
        #Limpa os capos
        self.limpa_campos()

        if dados:
            id_rec = dados.get('id_receita')

            data_obj = mysql_para_obj(dados.get('data'))

            self.valor.insert(0, str(dados.get('valor_recebido')))
            self.descricao.insert(0, dados.get('descricao'))
            self.data_recebimento.set_date(data_obj)

            self.botao_salvar.configure(text='Atualizar', fg_color="orange", command=lambda: self.salvar_dados(id_rec, atualizar=True))
        
        else:
            id_rec = None

            self.botao_salvar.configure(
            text="Salvar Dados", 
            fg_color=["#3B8ED0", "#1F6AA5"], # Cores padrão do CTk
            command=self.salvar_dados # Função original de INSERT
        )


    def limpa_campos(self):
        self.valor.delete(0, ctk.END)
        self.descricao.delete(0, ctk.END)
        self.data_recebimento.set_date(self.sentinela)


#Filho de Despesas e Simulacao (crud_app.py)
class Cadastrar_despesas(ctk.CTkFrame):

    def __init__(self,  parent=None, user_id=None, dados_cartoes =None, trocar_mes=None, atualizar_lista=None, simulacao=None, dados_select=None, controle_dados=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.dados_cartoes = dados_cartoes
        self.trocar_mes = trocar_mes
        self.atualizar_lista = atualizar_lista

        self.dados_select = dados_select
        self.simulacao = simulacao #boolean passado por mãe Simulacao
        self.controle_dados = controle_dados #métoddo callback de mãe Simulacao (crud_app.py)

        # ---------------- Gerencimento de self ---------------------
        self.nomes_cartoes = [c.get('nome_cartao') for c in self.dados_cartoes]
        self.data_atual = datetime.now().date()

        self.sentinela = (self.data_atual.replace(day=1, month=1, year=2099))

        # --------------- Configuração da janela/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_cadastro = ctk.CTkFrame(self)
        self.frame_cadastro.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.frame_cadastro.grid_columnconfigure(0, weight=1)
        self.frame_cadastro.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(self.frame_cadastro, text="Cadastre Suas Despesas", font=("Arial", 18, "bold")).grid(row=0, column=0, pady=(5,10))

        # LOCAL DA COMPRA
        self.local = ctk.CTkEntry(self.frame_cadastro, placeholder_text="Local da compra*")
        self.local.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        # TOTAL DA COMPRA
        self.valor_total = ctk.CTkEntry(self.frame_cadastro, placeholder_text="Valor total da compra*")
        self.valor_total.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        # PARCELAS
        parcelas_opcoes = [str(i) for i in range(1, 13)]
        self.menu_parcelas = ctk.CTkOptionMenu(self.frame_cadastro, values=parcelas_opcoes)
        self.menu_parcelas.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
        self.menu_parcelas.set("N° Parcelas")

        # DESCRIÇÃO DA COMPRA
        self.descricao = ctk.CTkEntry(self.frame_cadastro, placeholder_text="Descrição da Compra")
        self.descricao.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        # CATEGORIA
        categorias = ['Essencial', 'Lazer', 'Hobby', 'Vestimenta/Acessórios', 'Evolução Pessoal', 'Saúde', 'Empréstimo', 'Reforma e Construção']
        self.categoria = ctk.CTkOptionMenu(self.frame_cadastro, values=categorias)
        self.categoria.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        self.categoria.set("Categoria")

        # DATA DA COMPRA
        self.label_data_compra = ctk.CTkLabel(self.frame_cadastro, text="Data da Compra:", font=ctk.CTkFont(size=16, weight="bold"))
        self.label_data_compra.grid(row=6, column=0)

        self.campo_data_compra = DateEntry(self.frame_cadastro, width=12, background='darkblue',
                            foreground='white', borderwidth=2, year=2026, 
                            locale='pt_BR', date_pattern='dd/mm/yyyy')
        self.campo_data_compra.grid(row=7, column=0, padx=10, pady=10)

        # data primeira parcela - se não for no cartão
        self.label_primeira_dc = ctk.CTkLabel(self.frame_cadastro, text="Data do Primeiro Pagamento: \n(obs. Não preencher se a compra for no Cartão)", font=ctk.CTkFont(size=12, weight="bold"))
        self.label_primeira_dc.grid(row=8, column=0)

        self.campo_primeira_dc = DateEntry(self.frame_cadastro, width=12, background='darkblue',
                            foreground='white', borderwidth=2, day=1, month=1, year=2099, 
                            locale='pt_BR', date_pattern='dd/mm/yyyy')
        self.campo_primeira_dc.grid(row=9, column=0, padx=10, pady=10)
        
        #Seleção de cartão de crédito
        if self.nomes_cartoes:
            campo_cartoes = ["Cartão de Cobrança - Sem Cartão"] + self.nomes_cartoes

            self.car_cred = ctk.CTkOptionMenu(self.frame_cadastro, values=campo_cartoes)
            self.car_cred.grid(row=10, column=0, padx=20, pady=10, sticky="ew")
            self.car_cred.set("Cartão de Cobrança")
        else:
            self.car_cred = ctk.CTkOptionMenu(self.frame_cadastro, values=[' ', ' ',])
            self.car_cred.grid(row=10, column=0, padx=20, pady=10, sticky="ew")
            self.car_cred.set("Cadastre Seus Cartões Na Área Destinada")

        #bortão salvar / atualizar e simular
        if not self.simulacao:
            self.botao_salvar = ctk.CTkButton(self.frame_cadastro, text="Salvar Dados", command=self.salvar_dados)
            self.botao_salvar.grid(row=11, column=0, padx=20, pady=20, sticky="ew")
        else:
            self.botao_salvar = ctk.CTkButton(self.frame_cadastro, text="Simular despesa", command=lambda: self.salvar_dados(simulacao=True, dados_select=self.dados_select))
            self.botao_salvar.grid(row=11, column=0, padx=20, pady=20, sticky="ew")

        #status label - campo informativo
        self.status_label = ctk.CTkLabel(self.frame_cadastro, text="", text_color="red")
        self.status_label.grid(row=12, column=0, pady=5)


    def salvar_dados(self, id_desp=None, atualizar=None, simulacao=False, dados_select=None):
        """ Verifica e salva os dados no BD """

        dia_venc = None
        verifica_pri_dc = False
        id_card = None
        controle_mes = None

        local = self.local.get().strip()
        valor_total = self.valor_total.get().strip()
        menu_parcelas_str = self.menu_parcelas.get()
        descricao = self.descricao.get().strip()
        categoria = self.categoria.get()
        self.dc_select = self.campo_data_compra.get_date()
        self.prim_dc_select = self.campo_primeira_dc.get_date()

        prim_dc_select_mysql = None

        self.sentinela = self.data_atual.replace(day=1, month=1, year=2099)

        if self.prim_dc_select != self.sentinela:
            dia_venc = self.prim_dc_select.day
            verifica_pri_dc = True
            prim_dc_select_mysql = data_para_mysql(self.prim_dc_select)

        car_cred = self.car_cred.get()

        # Formata o objeto datetime para a string 'AAAA-MM-DD' para mandar para o db
        dc_select_mysql = data_para_mysql(self.dc_select)
        

        if not local or not valor_total or categoria == "Categoria" or menu_parcelas_str == "N° Parcelas":

            self.status_label.configure(text='Preencha Local, Valor Total, Categoria,\n N° Parcelas e Data da compra', text_color='red')
            tocar_notificacao('erro')
            self.after(3000, lambda: self.status_label.configure(text=''))
            return
    
        try:
            parcelas = int(menu_parcelas_str)
             # Tenta converter o valor para float
            valor_total = float(valor_total.replace(",", "."))
        except ValueError:
            self.status_label.configure(text='Valor Total ou Parcelas devem ser \nnúmeros válidos!', text_color='red')
            tocar_notificacao('erro')

            self.after(3000, lambda: self.status_label.configure(text=''))
            return
        
        tem_cartao = car_cred != "Cartão de Cobrança - Sem Cartão" or car_cred != "Cadastre Seus Cartões Na Área Destinada"

        if not tem_cartao and not verifica_pri_dc:
            # Se não tem cartão E não tem dia de vencimento, falha!
            self.status_label.configure(text='Informe um Cartão OU Data do \nprimeiro pagamento', text_color='red')
            tocar_notificacao('erro')
            self.after(3000, lambda: self.status_label.configure(text=''))
            return 

        if tem_cartao:
            for dado in self.dados_cartoes:
                if dado.get('nome_cartao') == car_cred:
                    id_card = dado.get('id_cartao')
                    dia_fechamento = dado.get('fechamento_fatura')
                    dia_vencimento = dado['vencimento_fatura']

                    if dia_vencimento < 12: #se o fech é num mês e vencimento no outro
                        mes_fech = self.dc_select.month - 1
                        data_fechamento = self.dc_select.replace(day=dia_fechamento, month=mes_fech)
                    else:
                        data_fechamento = self.dc_select.replace(day=dia_fechamento)
 

                    if self.dc_select >= data_fechamento:
                        controle_mes = (self.dc_select + relativedelta(months=1)).month
                    else:
                        controle_mes = self.dc_select.month
        else:
            controle_mes = self.prim_dc_select.month


        verifica = tem_cartao is True and verifica_pri_dc is True

        if verifica:
            self.campo_primeira_dc.set_date(self.sentinela)
            import time
            time.sleep(0.8)

            prim_dc_select_mysql = None
            dia_venc = None

            self.status_label.configure(text='Como foi informado um Cartão, a Data \nprimeiro pagamento será desconsiderada', text_color='blue')
            self.update_idletasks()
            self.after(3000, lambda: self.status_label.configure(text=''))


        #----------------- simulação ---------------------------
        if simulacao:

            
            dict_dados: Despesa_simulacao = {
                "local": local,
                "valor_total": valor_total,
                "parcelas": menu_parcelas_str,
                "descricao": descricao,
                "categoria": categoria,
                "data_compra": self.dc_select,
                "prim_data_pag": self.prim_dc_select,
                "nome_cartao": car_cred,
                "info_cartao": None,
            }  
            dados_select.append(dict_dados)

            if self.controle_dados:
                self.controle_dados(dados=dados_select)

                self.limpa_campos()
                return
     
        #-------------- atualização e inserção --------------------
        if not atualizar:
            if verifica:
                sucesso = inserir_despesa(self.user_id, local, valor_total, parcelas,  descricao, categoria, dc_select_mysql, prim_dc_select_mysql, dia_venc, id_card)
            else:
                sucesso = inserir_despesa(self.user_id, local, valor_total, parcelas,  descricao, categoria, dc_select_mysql, prim_dc_select_mysql, dia_venc, id_card)

            msg_ok = 'INSERIDOS'
            msg_erro = "SALVAR"
        else:
            sucesso = atualizar_despesa(id_desp, local, valor_total, parcelas,  descricao, categoria, dc_select_mysql, prim_dc_select_mysql, dia_venc, id_card)
            msg_ok = 'ATUALIZADOS'
            msg_erro = "ATUALIZAR"


        if sucesso:
            self.status_label.configure(text=f'Os dados foram {msg_ok} com sucesso!', text_color='green')

            tocar_notificacao('dv_sucesso', True)
            self.update_idletasks()

            if self.trocar_mes:
                self.trocar_mes(gerar_opcoes_meses().get(controle_mes))

            self.controla_campos(None)

            if self.atualizar_lista():
                self.atualizar_lista()
            
            self.after(3000, lambda: self.status_label.configure(text=''))

        else:
            self.status_label.configure(text=f'Não foi possível {msg_erro} os dados, contate o adm do sistema...', text_color='red')
            tocar_notificacao('dv_erro', True)
            self.update_idletasks()

            self.after(3000, lambda: self.status_label.configure(text=''))



    def controla_campos(self, dados=None):
        #'id_desp', 'local', 'valor_total', 'parcelas','descricao', 'categoria', 'data_compra', 'data_pp', 'dia_venc', 'id_cc' 

        self.limpa_campos()
        
        if dados:

            id_desp = dados.get('id_desp')

            nome_card = "Cartão de Cobrança - Sem Cartão"

            if self.dados_cartoes:
                for cartao in self.dados_cartoes:
                    if cartao.get('id_cartao') == dados.get('id_cc'):
                        nome_card = cartao.get('nome_cartao')

            self.local.insert(0, (dados.get('local')))
            self.valor_total.insert(0, (dados.get('valor_total')))
            self.descricao.insert(0, (dados.get('descricao')))

            self.menu_parcelas.set(dados.get('parcelas'))
            self.categoria.set(dados.get('categoria'))
            self.car_cred.set(nome_card)

            data_compra_obj = mysql_para_obj(dados.get('data_compra'))
            data_pp = dados.get('data_pp')

            if data_pp is None:
                data_pp_obj = self.sentinela
            else:
                data_pp_obj = mysql_para_obj(data_pp)

            self.campo_data_compra.set_date(data_compra_obj)
            self.campo_primeira_dc.set_date(data_pp_obj)

            self.botao_salvar.configure(text='Atualizar Assinatura', fg_color="orange", command=lambda: self.salvar_dados(id_desp, atualizar=True))
        
        else:
            id_desp = None

            self.botao_salvar.configure(
            text="Confirmar Assinatura", 
            fg_color=["#3B8ED0", "#1F6AA5"], # Cores padrão do CTk
            command=self.salvar_dados # Função original de INSERT
        )


    def limpa_campos(self):
        """Limpa todos os campos de entrada do formulário de despesas."""
        
        # Limpa CTkEntry's
        self.local.delete(0, ctk.END)
        self.valor_total.delete(0, ctk.END)
        self.descricao.delete(0, ctk.END)

        self.menu_parcelas.set("N° Parcelas")
        self.categoria.set("Categoria")
        self.car_cred.set("Cartão de Cobrança - Sem Cartão")

        self.campo_data_compra.set_date(self.data_atual)
        self.campo_primeira_dc.set_date(self.sentinela)
        

#Filho de Cartões de Crédito (crud_app.py)
class Cadastrar_car_cred(ctk.CTkFrame):

    def __init__(self,  parent=None, user_id=None, nomes_cards =None, att_app= None, atualizar_lista =None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.nomes_cards = nomes_cards
        self.att_app = att_app
        self.atualizar_lista = atualizar_lista

        # ---------------- Gerencimento de self ---------------------
        

        # --------------- Configuração da janela/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1)


        ctk.CTkLabel(self, text="Cadastre Seus Cartões de Crédito", font=("Arial", 18, "bold")).grid(row=0, column=0, pady=10)

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


    def salvar_dados(self, id_card=None, atualizar=None):
        """ Verifica e salva os dados no BD """

        nome_cc = self.nome_cc.get().strip()
        limite = self.limite.get().strip()
        dia_f = self.dia_fechamento.get().strip()
        dia_v = self.dia_vencimento.get().strip()
        
        #verifiva se já tem o nome informado na entry no bd
        for nome in self.nomes_cards:
            if nome == nome_cc:
                tocar_notificacao("dv_erro", True)

                self.status_label.configure(text=f'Por favor, Não repitir nome de cartões, tente - ex: *{nome_cc}700', text_color='red')
                self.update_idletasks()

                self.after(3000, lambda: self.status_label.configure(text=''))
                return

        if not nome_cc or not limite or not dia_f or not dia_v:
            self.status_label.configure(text='Por favor, preencha todos os campos obrigarórios', text_color='red')
            tocar_notificacao("dv_erro", True)

            self.update_idletasks()
            self.after(2000, lambda: self.status_label.configure(text=''))
            
            return
        
        sucesso = False

        if not atualizar:
            sucesso = inserir_cc(self.user_id, nome_cc, limite, dia_f, dia_v)
            msg_ok = "INSERIDOS"
            msg_erro = "SALVAR"
        else:
            sucesso = atualizar_cartao(id_card, nome_cc, limite, dia_f, dia_v)
            msg_ok = "ATUALIZADOS"
            msg_erro = "ATUALIZAR"

        if sucesso:
            self.status_label.configure(text=f'Os dados foram {msg_ok} com sucesso!', text_color='green')
            tocar_notificacao("dv_sucesso", True)
            self.update_idletasks()
            
            self.after(2000, lambda: self.status_label.configure(text=''))

            self.controla_campos(None)

            if self.atualizar_lista:
                self.atualizar_lista()

            if self.att_app:
                self.att_app()
                
    
                
        else:
            self.status_label.configure(text=f'Não foi possível {msg_erro} os dados, contate o adm do sistema...', text_color='red')

            tocar_notificacao("dv_erro", True)
            self.update_idletasks()

            self.after(2000, lambda: self.status_label.configure(text=''))
    

    def controla_campos(self, dados=None):

        #'id_cartao', 'nome_cartao', 'limite_cartao', 'fechamento_fatura', 'vencimento_fatura'
        
        self.limpa_campos()

        if dados:

            id_card = dados.get('id_cartao')

            self.nome_cc.insert(0, (dados.get('nome_cartao')))
            self.limite.insert(0, str(dados.get('limite_cartao')))
            self.dia_fechamento.insert(0, dados.get('fechamento_fatura'))
            self.dia_vencimento.insert(0, dados.get('vencimento_fatura'))

            self.botao_salvar.configure(text='Atualizar Cartão', fg_color="orange", command=lambda: self.salvar_dados(id_card, atualizar=True))
        
        else:
            id_card = None

            self.botao_salvar.configure(
            text="Salvar Dados", 
            fg_color=["#3B8ED0", "#1F6AA5"], 
            command=self.salvar_dados 
        )


    def limpa_campos(self):
        """Limpa todos os campos de entrada do formulário""" 
        
        self.nome_cc.delete(0, ctk.END)
        self.limite.delete(0, ctk.END)
        self.dia_fechamento.delete(0, ctk.END)
        self.dia_vencimento.delete(0, ctk.END)


#Filho de Assinaturas (crud_app.py)
class Cadastrar_assinaturas(ctk.CTkFrame):

    def __init__(self, parent=None, user_id=None, dados_cartoes=None, trocar_mes=None, atualizar_lista = None):
        super().__init__(parent)

        self.trocar_mes = trocar_mes
        self.atualizar_lista = atualizar_lista
        self.user_id = user_id
        self.dados_cartoes = dados_cartoes 
        
        # ---------------- Gerencimento de self --------------------
        self.data_atual = datetime.now().date()
        self.sentinela = (self.data_atual.replace(day=1, month=1, year=2099))

        self.nomes_cartoes = [c['nome_cartao'] for c in self.dados_cartoes]

        
        # --------------- Configuração da janela/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Cadastre Suas Assinaturas", font=("Arial", 18, "bold")).grid(row=0, column=0, pady=10)

        # --- UI - Campos de Entrada ---
        self.entry_nome = ctk.CTkEntry(self, placeholder_text="Nome (Ex: Netflix, Academia)", width=300)
        self.entry_nome.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.entry_valor = ctk.CTkEntry(self, placeholder_text="Valor Mensal (R$)", width=300)
        self.entry_valor.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.entry_desc = ctk.CTkEntry(self, placeholder_text="Descrição (Opcional)", width=300)
        self.entry_desc.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.label_prim_dp = ctk.CTkLabel(self, text="Data Requisição)", font=ctk.CTkFont(size=12, weight="bold"))
        self.label_prim_dp.grid(row=4, column=0)

        self.data_aquisicao = DateEntry(self, width=12, background='darkblue',
                            foreground='white', borderwidth=2, year=2026, 
                            locale='pt_BR', date_pattern='dd/mm/yyyy')
        
        self.data_aquisicao.grid(row=5, column=0, padx=10, pady=10)

        self.label_primeira_dc = ctk.CTkLabel(self, text="Data do Primeiro Pagamento: (obs. Não preencher se a compra for no C. Crédito)", font=ctk.CTkFont(size=12, weight="bold"))
        self.label_primeira_dc.grid(row=6, column=0)

        self.campo_prim_dp = DateEntry(self, width=12, background='darkblue',
                            foreground='white', borderwidth=2, day=1, month=1, year=2099, 
                            locale='pt_BR', date_pattern='dd/mm/yyyy')
        self.campo_prim_dp.grid(row=7, column=0, padx=10, pady=10)

        # Menu de Categorias
        categorias = ['Lazer', 'Essencial', 'Estudos', 'Saúde', ' Hobby','Streaming',]
        self.menu_cat = ctk.CTkOptionMenu(self, values=categorias, width=300)
        self.menu_cat.grid(row=8, column=0, padx=20, pady=10, sticky="ew")
        self.menu_cat.set("Selecione a Categoria")


        if self.nomes_cartoes:
            campo_cartoes = ["Cartão de Cobrança - Sem Cartão"] + self.nomes_cartoes

            self.menu_cc = ctk.CTkOptionMenu(self, values=campo_cartoes, width=300)
            self.menu_cc.grid(row=9, column=0, padx=20, pady=10, sticky="ew")
            self.menu_cc.set("Cartão de Cobrança - Sem Cartão")
        else:
            self.car_cred = ctk.CTkOptionMenu(self, values=[' ', ' ',])
            self.car_cred.grid(row=10, column=0, padx=20, pady=10, sticky="ew")
            self.car_cred.set("Cadastre Seus Cartões Na Área Destinada")
    

        # --- Botão Salvar ---
        self.btn_salvar = ctk.CTkButton(self, text="Confirmar Assinatura", command=self.salvar_dados, fg_color="#2c3e50", hover_color="#34495e")
        self.btn_salvar.grid(row=10, column=0, padx=20, pady=10, sticky="ew")

        self.status_label = ctk.CTkLabel(self, text="", text_color="red")
        self.status_label.grid(row=11, column=0, pady=5)


    def salvar_dados(self, id_ass=None, atualizar=None):

        dia_venc = None
        verifica_data_pp = False

        id_card = None

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

        if data_pp != self.sentinela:
            dia_venc = data_pp.day
            verifica_data_pp = True
            data_pp_mysql = data_para_mysql(data_pp)

            if data_pp.year == self.sentinela.year:
                self.status_label.configure(text='Mude o ano da data de primeiro pagemento', text_color='red')

                tocar_notificacao("dv_erro", True)
                self.after(3000, lambda: self.status_label.configure(text='')) 
                return

        if not nome or not valor or categoria == "Selecione a Categoria":

            self.status_label.configure(text='Preencha Nome, Valor, Categoria ,', text_color='red')
            tocar_notificacao("dv_erro", True)
            self.after(3000, lambda: self.status_label.configure(text=''))
            return

        try:
             # Converte o valor para float
            valor = float(valor.replace(",", "."))
        except ValueError:
            self.status_label.configure(text=" 'Valor' deve ser números válidos!", text_color='red')
            tocar_notificacao("dv_erro", True)

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
            tocar_notificacao("dv_erro", True)

            self.after(3000, lambda: self.status_label.configure(text='')) 
            return
        
        sucesso = False
        if not atualizar:
            sucesso = inserir_assinatura(self.user_id, nome, valor, descricao, data_aq_mysql, data_pp_mysql, dia_venc, categoria, id_card )
            msg_ok = "INSERIDOS"
            msg_falha = "Não foi possível SALVAR os dados, contate o adm do sistema...'"
            
        else:
            sucesso = atualiza_assinatura(id_ass, nome, valor, descricao, data_aq_mysql, data_pp_mysql, dia_venc, categoria, id_card )
            msg_ok = "ATUALIZADOS"
            msg_falha = "Não foi possível ATUALIZAR os dados, contate o adm do sistema...'"

        #retorno do banco - texto de indicação
        if sucesso:
            tocar_notificacao("dv_sucesso", True)

            self.status_label.configure(text=f'Os dados foram {msg_ok} com sucesso!', text_color='green')
            self.update_idletasks()

            self.controla_campos(None)
            
            self.after(2000, lambda: self.status_label.configure(text=''))

            if self.trocar_mes:
                self.trocar_mes(gerar_opcoes_meses().get(data_pp.month)) 

            if self.atualizar_lista:
                self.atualizar_lista()     

        else:
            self.status_label.configure(text=f'{msg_falha}', text_color='red')
            tocar_notificacao("dv_erro", True)
            self.update_idletasks()
            self.after(2000, lambda: self.status_label.configure(text=''))


    def controla_campos(self, dados=None):

        #id_ass, nome, valor, descricao, data_aquisicao, data_prim_pag, categoria, id_cc

        self.limpa_campos()

        if dados:
            nome_card = "Cartão de Cobrança - Sem Cartão"

            if self.dados_cartoes:

                for cartao in self.dados_cartoes:
                    if cartao.get('id_cartao') == dados.get('id_cc'):
                        nome_card = cartao.get('nome_cartao')

            id_ass = dados.get('id_ass')

            data_aq_obj = mysql_para_obj(dados.get('data_aquisicao'))
            data_pp_obj = mysql_para_obj(dados.get('data_prim_pag'))

            self.entry_nome.insert(0, (dados.get('nome')))
            self.entry_valor.insert(0, str(dados.get('valor')))
            self.entry_desc.insert(0, dados.get('descricao'))
            self.data_aquisicao.set_date(data_aq_obj)
            self.campo_prim_dp.set_date(data_pp_obj)
            self.menu_cat.set(dados.get('categoria'))
            self.menu_cc.set(nome_card)
            

            self.btn_salvar.configure(text='Atualizar Assinatura', fg_color="orange", command=lambda: self.salvar_dados(id_ass, atualizar=True))
        
        else:
            id_ass = None

            self.btn_salvar.configure(
            text="Confirmar Assinatura", 
            fg_color=["#3B8ED0", "#1F6AA5"], # Cores padrão do CTk
            command=self.salvar_dados # Função original de INSERT
        )


    def limpa_campos(self):
        """Limpa todos os campos de entrada do formulário de assinaturas."""
        
        # Limpa CTkEntry's
        self.entry_nome.delete(0, ctk.END)
        self.entry_valor.delete(0, ctk.END)
        self.entry_desc.delete(0, ctk.END)

        # Reseta CTkOptionMenu's para seus valores padrão
        self.menu_cat.set("Selecione a Categoria")
        self.menu_cc.set("Cartão de Cobrança - Sem Cartão")

        self.data_aquisicao.set_date(self.data_atual)
        self.campo_prim_dp.set_date(self.sentinela)


