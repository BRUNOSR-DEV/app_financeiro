
from models.conecte_bd import ( pega_usuarios, dados_user, pega_id, dados_card, inserir_usuario, inserir_receitas, inserir_cc, inserir_despesas, inserir_dividas)

from time import sleep
import customtkinter as ctk
from tkcalendar import Calendar
from datetime import datetime

#configura a aparência
ctk.set_appearance_mode('light')


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

        self.registrar = ctk.CTkButton(self, text="Registar", command=self.abrir_tela_registro,
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
        self.geometry("950x600")

        self.__dict__['usuario_logado'] = logged_in_username
        
        self.user_id = pega_id(self.usuario_logado)
        self.nomeComp = dados_user(self.user_id)[0][1]

        self.grid_rowconfigure(0, weight=0) # Linha para o frame superior (usuário e add tarefa)
        self.grid_rowconfigure(1, weight=1) 
        self.grid_columnconfigure(0, weight=1)

        self.top_section_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_section_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.top_section_frame.grid_columnconfigure(0, weight=0) # primeira coluna para label usuário
        self.top_section_frame.grid_columnconfigure(0, weight=1) # segunda coluna para botão sair

        if self.usuario_logado: 
            self.nomeusuario_label = ctk.CTkLabel(self.top_section_frame,
                                               text=f"Bem-vindo, {self.nomeComp}!",
                                               font=ctk.CTkFont(size=16, weight="bold"))
            
        else:
            self.nomeusuario_label = ctk.CTkLabel(self.top_section_frame,
                                               text="Bem-vindo!",
                                               font=ctk.CTkFont(size=16, weight="bold"))
            
        self.botao_sair = ctk.CTkButton(self.top_section_frame, text="Sair", command=self.voltar_Plogin, width=80,
                                        fg_color="#FF0000", hover_color="#810000")
        
        self.botao_sair.grid(row=0, column=1,sticky="e") #coluna 1 alinhado a direita

        #Primeira Label da janela   
        self.nomeusuario_label.grid(row=0, column=0, pady=(0, 10), sticky="w")


        #-------------------------------------------------------------------------------------
        # Frame para agrupar os botões de cadastro
        self.cadastro_frame = ctk.CTkFrame(self.top_section_frame, fg_color="transparent")
        self.cadastro_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")
        self.cadastro_frame.grid_columnconfigure((0, 1, 2), weight=1) # Distribui o espaço entre os botões
        #---------------------------------------------------------------------------------------
        #---------------------------------------------------------------------------------------
        # Botões de cadastro
        self.btn_receitas = ctk.CTkButton(self.cadastro_frame, text="Receitas", command=self.abrir_receitas)
        self.btn_receitas.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.btn_despesas = ctk.CTkButton(self.cadastro_frame, text="Despesas", command=self.abrir_despesas)
        self.btn_despesas.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.btn_cc = ctk.CTkButton(self.cadastro_frame, text="Cartão de Crédito", command=self.abrir_cc)
        self.btn_cc.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        #---------------------------------------------------------------------------------------


    def abrir_receitas(self):
        """ Direciona o usuário para fazer o cadastro de suas receitas, chamando a classe receitas"""
        
        # Passa a própria instância da tela de login para a tela de registro
        register_window = Receitas(self, self.user_id, login_instance=self)
        #self.status_label.configure(text='Abrindo tela de registro...', text_color='blue')
        
        # A mainloop() não é chamada para toplevels, elas são gerenciadas pelo master.
        self.wait_window(register_window) #Pausa a janela de login até a popup fechar

    def abrir_despesas(self):
        register_window = Despesas(self, self.user_id, login_instance=self)

        self.wait_window(register_window)

    def abrir_cc(self):
        register_window = Car_cred(self, self.user_id, login_instance=self)

        self.wait_window(register_window)



    def voltar_Plogin(self):
        """ Método para voltar para a tela de login (botão 'Sair')"""

        self.nomeusuario_label.configure(text=f'Até a próxima {self.usuario_logado} !', text_color='red')
        self.update_idletasks()

        sleep(3)

        self.destroy()
        from app import Login

        login_app = Login()
        login_app.mainloop()



class Receitas(ctk.CTkToplevel):

    def __init__(self,  master=None, user_id=None, login_instance=None):
        super().__init__(master)

        self.user_id = user_id

        self.title("Registrar Novas Receitas")
        self.geometry("450x600")
        self.transient(master) # Faz a popup aparecer sobre a janela principal e fechar com ela
        self.grab_set() # Bloqueia interações com a janela principal enquanto a popup está aberta
        self.focus_set() # Define o foco para esta janela

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=0)

        ctk.CTkLabel(self, text="Cadastre Seus Ganhos", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=15)

        self.valor = ctk.CTkEntry(self, placeholder_text="Valor Ganho")
        self.valor.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.descricao = ctk.CTkEntry(self, placeholder_text="Descrição")
        self.descricao.grid(row=2, column=0, padx=20, pady=10, sticky="ew")


            
        self.data_calendario = Calendar(self, selectmode='day', date_pattern='dd/mm/yyyy', background='gray80',
                                        foreground='black', normalbackground='gray90', headersbackground='gray70',
                                        selectbackground='gray60', othermonthforeground='gray70')
        self.data_calendario.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.botao_salvar = ctk.CTkButton(self, text="Salvar Dados", command=self.salvar_dados)
        self.botao_salvar.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.status_label = ctk.CTkLabel(self, text="", text_color="red")
        self.status_label.grid(row=5, column=0, pady=5)


    def salvar_dados(self):
        """ Verifica e salva os dados no BD """

        valor = self.valor.get().strip()
        descricao = self.descricao.get().strip()
        data_str = self.data_calendario.get_date()

        data_obj = datetime.strptime(data_str, '%d/%m/%Y')
    
        # Formata o objeto datetime para a string 'AAAA-MM-DD'
        data_formatada = data_obj.strftime('%Y-%m-%d')

        if not valor or not descricao or not data_str:
            self.status_label.configure(text='Por favor, preencha todos os campos!', text_color='red')
            self.update_idletasks()
            sleep(1)
            return
        else:
            retorno = inserir_receitas(self.user_id, valor, descricao, data_formatada)

        if retorno:
            self.status_label.configure(text='Os dados foram inseridos com sucesso!', text_color='green')
            self.update_idletasks()
            sleep(2)

            #self.destroy()
                
        else:
            self.status_label.configure(text='Não foi possível salvar dados, contate o adm do sistema...', text_color='red')
            self.update_idletasks()


 
class Despesas(ctk.CTkToplevel):

    def __init__(self,  master=None, user_id=None, login_instance=None):
        super().__init__(master)

        self.user_id = user_id

        self.title("Registrar Novas Receitas")
        self.geometry("600x700")
        self.transient(master)
        self.grab_set() 
        self.focus_set() 

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=0)

        ctk.CTkLabel(self, text="Cadastre Suas Despesas", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=15)

        self.local = ctk.CTkEntry(self, placeholder_text="Local da compra*")
        self.local.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.valor_total = ctk.CTkEntry(self, placeholder_text="Valor total da compra*")
        self.valor_total.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        parcelas_opcoes = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]

        self.menu_parcelas = ctk.CTkOptionMenu(self, values=parcelas_opcoes)
        self.menu_parcelas.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
        self.menu_parcelas.set("N° Parcelas")

        self.descricao = ctk.CTkEntry(self, placeholder_text="Descrição da compra")
        self.descricao.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        categorias = ['Laser', 'Roupas', 'Higiene', 'Curso', 'Comida', 'Divida',]

        self.categoria = ctk.CTkOptionMenu(self, values=categorias)
        self.categoria.grid(row=5, column=0, padx=20, pady=10, sticky="ew")
        self.categoria.set("Categoria")

        self.data = Calendar(self, selectmode='day', date_pattern='dd/mm/yyyy', background='gray80',
                                        foreground='black', normalbackground='gray90', headersbackground='gray70',
                                        selectbackground='gray60', othermonthforeground='gray70')
        self.data.grid(row=6, column=0, padx=20, pady=10, sticky="ew")

        self.dia_vencimento = ctk.CTkEntry(self, placeholder_text="Qual dia que vence a divida (opcional)")
        self.dia_vencimento.grid(row=7, column=0, padx=20, pady=10, sticky="ew")

        lista_nomes = []
        for i in self.verifica_cartoes():
            lista_nomes.append(i[1])

        self.car_cred = ctk.CTkOptionMenu(self, values=lista_nomes)
        self.car_cred.grid(row=8, column=0, padx=20, pady=10, sticky="ew")
        self.car_cred.set("Selecione um Cartão")

        self.botao_salvar = ctk.CTkButton(self, text="Salvar Dados", command=self.salvar_dados)
        self.botao_salvar.grid(row=9, column=0, padx=20, pady=10, sticky="ew")

        self.status_label = ctk.CTkLabel(self, text="", text_color="red")
        self.status_label.grid(row=10, column=0, pady=5)


    def salvar_dados(self):
        """ Verifica e salva os dados no BD """

        local = self.local.get().strip()
        valor_total = self.valor_total.get().strip()
        menu_parcelas_str = self.menu_parcelas.get().strip()
        descricao = self.descricao.get().strip()
        categoria = self.categoria.get().strip()
        data_str = self.data.get_date()
        dia_vencimento = self.dia_vencimento.get().strip()
        car_cred = self.car_cred.get().strip()

        data_obj = datetime.strptime(data_str, '%d/%m/%Y')
    
        # Formata o objeto datetime para a string 'AAAA-MM-DD'
        data_formatada = data_obj.strftime('%Y-%m-%d')


        if not local or not valor_total or categoria == "Categoria" or menu_parcelas_str == "N° Parcelas":
            self.status_label.configure(text='Preencha Local, Valor, Categoria e N° Parcelas!', text_color='red')
            self.after(2000, lambda: self.status_label.configure(text='')) # Usa after() para não travar
            return
    
        try:
            parcelas = int(menu_parcelas_str)
             # Tenta converter o valor para float
            float(valor_total.replace(',', '.'))
        except ValueError:
            self.status_label.configure(text='Valor ou Parcelas devem ser números válidos!', text_color='red')
            self.after(2000, lambda: self.status_label.configure(text=''))
            return
        
        # 2. VALIDAÇÃO CONDICIONAL PRINCIPAL
    
        # Verifica se a despesa é parcelada (se for mais de 1 parcela)
        is_parcelado = parcelas > 1
    
        # Flag para saber se o requisito de pagamento foi atendido
        pagamento_atendido = True
    
        if is_parcelado:
        # A despesa é parcelada, DEVE ter um cartão OU dia de vencimento
        
            tem_cartao = car_cred != "Selecione um Cartão"
            tem_vencimento = bool(dia_vencimento) # Verifica se a string não está vazia
        
            if not tem_cartao and not tem_vencimento:
                # Se não tem cartão E não tem dia de vencimento, falha!
                self.status_label.configure(text='Se parcelado, informe o Cartão OU Dia de Vencimento.', text_color='red')
                self.after(4000, lambda: self.status_label.configure(text=''))
                return # Sai do método


        id_card = None
        for i in self.verifica_cartoes():
            if car_cred == i[1]:
                id_card = i[0]
                break
                
        if not dia_vencimento:
            dia_vencimento = None


        retorno = inserir_despesas(self.user_id, local, valor_total, parcelas,  descricao, categoria, data_formatada, dia_vencimento, id_card)

        if retorno:
            self.status_label.configure(text='Os dados foram inseridos com sucesso!', text_color='green')
            self.update_idletasks()
            sleep(3)
            self.limpar_campos()

            #self.destroy()
                
        else:
            self.status_label.configure(text='Não foi possível salvar dados, contate o adm do sistema...', text_color='red')
            self.update_idletasks()


    def verifica_cartoes(self):

        cartoes = dados_card(self.user_id)
        lista_cartoes = []
        if cartoes:
            for cartao in cartoes:
                # Assumindo que a tupla do cartão é algo como (id, id_usuario, nome, limite, etc.)
                # O nome seria o terceiro elemento, por isso o índice [2]
                lista_cartoes.append((cartao[0], cartao[2]))
        else:
            return [("0", "Nenhum Cartão")]
        
        return lista_cartoes
    

    def limpar_campos(self):
        """Limpa todos os campos de entrada do formulário de despesas."""
        
        # Limpa CTkEntry's
        self.local.delete(0, ctk.END)
        self.valor_total.delete(0, ctk.END)
        self.descricao.delete(0, ctk.END)
        self.dia_vencimento.delete(0, ctk.END)
        
        # Reseta CTkOptionMenu's para seus valores padrão
        self.menu_parcelas.set("N° Parcelas")
        self.categoria.set("Categoria")
        self.car_cred.set("Selecione um Cartão")
        
        """
        # Reseta o menu de Cartões (para o primeiro item da lista)
        lista_nomes = [cartao[1] for cartao in self.lista_cartoes_id_nome] 
        if lista_nomes:
            self.car_cred.set(lista_nomes[0])
        """
                
        

class Car_cred(ctk.CTkToplevel):

    def __init__(self,  master=None, user_id=None, login_instance=None):
        super().__init__(master)

        self.user_id = user_id

        self.title("Registrar Novas Receitas")
        self.geometry("450x600")
        self.transient(master)
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










if __name__ == "__main__":
    # Inicia a primeira tela (tela de login)
    login_app = Login()
    login_app.mainloop()