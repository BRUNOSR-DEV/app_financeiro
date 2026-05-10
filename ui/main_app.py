
from datetime import datetime
from dateutil.relativedelta import relativedelta
import locale
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

from models.conecte_bd import (
     pega_usuario, pega_id, dados_cartoes, pega_despesas_avulsas, dados_receitas, pega_assinaturas_avulsas, atualizar_renda
     )

from utils.helper import(
    gerar_opcoes_meses, mysql_para_obj, formatar_moeda, centralizar_janela, check_entry_num, preparar_dados_completos_cartao
)

from utils.audio_helper import tocar_notificacao 

from ui.crud_app import (
    Faturas, Receitas, Despesas, Car_cred, Assinaturas, Simulacao
)

from utils.typedDict import(
    Dados_usuarios_db, Dados_receitas_db, Dados_despesas_db, Dados_cartoes_db, Dados_assinaturas_db, Pega_despesas_avulsas_bd, Pega_assinaturas_avulças_db
    )
from typing import List

from ui.detalhar import(
    Listar_desp_tabela, Listar_cat_grafico
)


import customtkinter as ctk
ctk.set_appearance_mode('dark')

from decimal import Decimal
from collections import defaultdict 


class Main_app(ctk.CTk):

    def __init__(self, logged_in_username=None):
        super().__init__()

        self.usuario_logado = logged_in_username
        self.title("Controle Financeiro")
        centralizar_janela(self, 1300, 800)

        self.container_principal = ctk.CTkFrame(self, fg_color="transparent")
        self.container_principal.pack(fill="both", expand=True)

        # Registra a função validadora no sistema do Tkinter
        # O '%P' significa que o Tkinter vai passar o texto "Proposto" para a função
        self.vcmd_num = (self.register(check_entry_num), '%P')

        # Carrega os dados e monta a tela pela PRIMEIRA vez
        self.buscar_dados_banco()
        self.montar_dashboard()

        self.configure(fg_color="#212121")

        self.tt_dividas = 0


    def buscar_dados_banco(self):
        """ Função exclusiva para buscar/calcular dados. """
        self.user_id = pega_id(self.usuario_logado)
        self.dados_usuario: List[Dados_usuarios_db] = pega_usuario(self.user_id)
        self.dados_receitas: List[Dados_receitas_db] = dados_receitas(self.user_id)

        self.valor_renda = self.dados_usuario.get('sal_fixo', 0.0) 

        self.data_atual = datetime.now()
        self.mes_atual = self.data_atual.month
        self.prox_mes =  (self.data_atual + relativedelta(months=1)).month
        self.seg_prox_mes =  (self.data_atual + relativedelta(months=2)).month
        self.ter_prox_mes =  (self.data_atual + relativedelta(months=3)).month
        self.quart_prox_mes =  (self.data_atual + relativedelta(months=4)).month
        self.quint_prox_mes =  (self.data_atual + relativedelta(months=5)).month

        opcoes = gerar_opcoes_meses()
        self.mes_atual_str = opcoes.get(self.mes_atual)
        self.prox_mes_str = opcoes.get(self.prox_mes)
        self.seg_prox_mes_str = opcoes.get(self.seg_prox_mes)
        self.ter_prox_mes_str = opcoes.get(self.ter_prox_mes)
        self.quart_prox_mes_str = opcoes.get(self.quart_prox_mes)
        self.quint_prox_mes_str = opcoes.get(self.quint_prox_mes)

        self.nomes_datas = [self.mes_atual_str, self.prox_mes_str, self.seg_prox_mes_str, self.ter_prox_mes_str, self.quart_prox_mes_str, self.quint_prox_mes_str]

        self.dados_cartoes: List[Dados_cartoes_db] = dados_cartoes(self.user_id)
        self.nomes_cartoes = [c.get('nome_cartao') for c in self.dados_cartoes]

        self.despesas_avulsas: List[Pega_despesas_avulsas_bd] = pega_despesas_avulsas(self.user_id)
        self.assinaturas_avulsas: List[Pega_assinaturas_avulças_db] = pega_assinaturas_avulsas(self.user_id)

        #chamada de dados 'despesas' e 'assinaturas' nos cartoes de self.dados_cartoes
        self.dados_desp_ass_card = preparar_dados_completos_cartao(self.user_id, self.dados_cartoes)

    def montar_dashboard(self):
        """ Função exclusiva para desenhar a interface. """
        
        for widget in self.container_principal.winfo_children():
            widget.destroy()


        self.container_principal.grid_rowconfigure(0, weight=1) 
        self.container_principal.grid_rowconfigure(1, weight=1) 
        self.container_principal.grid_columnconfigure(0, weight=1)

        # ---------------
        # TOP SECTION 
        # ---------------
        self.top_section_frame = ctk.CTkFrame(self.container_principal, fg_color="transparent")
        self.top_section_frame.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ew")
        
        self.top_section_frame.grid_columnconfigure(0, weight=0) # Bem-vindo
        self.top_section_frame.grid_columnconfigure(1, weight=1) # Renda Fixa (EXPANDE e empurra o resto pra direita)
        self.top_section_frame.grid_columnconfigure((2, 3, 4, 5, 6), weight=0) # Outros botões fixos

        texto_boas_vindas = f"Bem-vindo, {self.dados_usuario.get('nome_completo')}!" if self.usuario_logado else "Bem-vindo!"
        self.nomeusuario_label = ctk.CTkLabel(self.top_section_frame, text=texto_boas_vindas, font=ctk.CTkFont(size=18, weight="bold"))
        self.nomeusuario_label.grid(row=0, column=0, padx=5, pady=(0, 10), sticky="w")

        # --- DISPLAY DE RENDA FIXA ---
        self.frame_renda = ctk.CTkFrame(self.top_section_frame, fg_color="transparent", width=150, height=100, corner_radius=15, border_width=3)
        self.frame_renda.grid(row=0, column=1, padx=10, pady=(0, 10), sticky="w") # Fica do lado do nome
        
        self.label_renda = ctk.CTkLabel(self.frame_renda, text=f"Renda Fixa: {formatar_moeda(self.valor_renda)}", text_color="#27ae60", font=ctk.CTkFont(size=18,weight="bold"))
        self.label_renda.pack(side="left", padx=(0, 10))
        
        self.btn_edit_renda = ctk.CTkButton(self.frame_renda, text="📝", width=30, height=30, fg_color="transparent", border_width=1, command=self.abrir_modal_renda)
        self.btn_edit_renda.pack(side="left")
        # --- END Renda fixa -----
        
        # ----- Top section botões func ---------
        self.btn_simulacao = ctk.CTkButton(self.top_section_frame, text='Simulação', command=self.abrir_simulacao, fg_color="#F87979", hover_color="#823737")
        self.btn_simulacao.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        self.mes_vigente_label = ctk.CTkLabel(self.top_section_frame, text=f"Mês: ", font=ctk.CTkFont(size=16, weight="bold"))
        self.mes_vigente_label.grid(row=0, column=3, padx=10, pady=10, sticky="w")

        self.menu_mes = ctk.CTkOptionMenu(self.top_section_frame, values=self.nomes_datas, command=self.trocar_mes, fg_color="#676666")
        self.menu_mes.grid(row=0, column=4, padx=10, pady=5, sticky="w")

        self.btn_att_app = ctk.CTkButton(self.top_section_frame, text="Atualizar", command=self.att_app, fg_color="#18123F", hover_color="#0A0720")
        self.btn_att_app.grid(row=0, column=5, padx=10, sticky="ew")
           
        self.botao_sair = ctk.CTkButton(self.top_section_frame, text="Sair", command=self.voltar_Plogin, fg_color="#840000", hover_color="#350100")
        self.botao_sair.grid(row=0, column=6, padx=(30, 0), sticky="ew") 
        # ----END Secton botões func ---------

        
        # ---- FRAME DE BOTÕES DE CADASTRO ----
        self.cadastro_frame = ctk.CTkFrame(self.top_section_frame, fg_color="transparent")
        self.cadastro_frame.grid(row=1, column=0, columnspan=6, padx=10, pady=(0, 10), sticky="ew")
        self.cadastro_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1) 

        self.btn_receitas = ctk.CTkButton(self.cadastro_frame, text="Receitas", command=self.abrir_receitas, fg_color="#676666", hover_color="#005E02")
        self.btn_receitas.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.btn_despesas = ctk.CTkButton(self.cadastro_frame, text="Despesas", command=self.abrir_despesas, fg_color="#676666", hover_color="#670000")
        self.btn_despesas.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.btn_cc = ctk.CTkButton(self.cadastro_frame, text="Cartões de Crédito",  command=self.abrir_cc, fg_color="#676666", hover_color="#B56300")
        self.btn_cc.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

        self.btn_assin = ctk.CTkButton(self.cadastro_frame, text="Assinaturas", command=self.abrir_assinaturas, fg_color="#676666", hover_color="#140062")
        self.btn_assin.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        self.label_cc = ctk.CTkLabel(self.cadastro_frame, text="Selecione o Cartão:")
        self.label_cc.grid(row=0, column=4, padx=10, pady=5)

        self.menu_cartoes = ctk.CTkOptionMenu(self.cadastro_frame, values=self.nomes_cartoes, fg_color="#B76500")
        self.menu_cartoes.grid(row=1, column=4, padx=10, pady=5,  sticky="ew")

        self.det_despesas_cc = ctk.CTkButton(self.cadastro_frame, text="Detalhar", command=self.abrir_det_cc, fg_color="#B76500", hover_color="#472201")
        self.det_despesas_cc.grid(row=1, column=5, padx=2, pady=2, sticky="ew")
        #---- End frame botões -----

        # ---------------
        # MAIN CONTENT 
        # ---------------
        self.main_content_frame = ctk.CTkFrame(self.container_principal, fg_color="transparent")
        self.main_content_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.main_content_frame.grid_columnconfigure(0, weight=2) #tabela
        self.main_content_frame.grid_columnconfigure(1, weight=1) #gráfico
        self.main_content_frame.grid_rowconfigure(0, weight=1)

        # FRAME TABELA - Chamando do detalhar
        

        self.frame_tabela = Listar_desp_tabela(parent=self.main_content_frame, id_user=self.user_id, despesas_avulsas= self.despesas_avulsas, assinaturas_avulsas=self.assinaturas_avulsas, dados_cartoes=self.dados_cartoes, dados_prontos= self.dados_desp_ass_card)

        self.frame_tabela.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        ret = self.frame_tabela.renderizar()


        # FRAME GRÁFICO - Chamando do detalhar
        self.frame_grafico = Listar_cat_grafico(parent=self.main_content_frame, id_user=self.user_id, despesas_avulsas= self.despesas_avulsas, assinaturas_avulsas=self.assinaturas_avulsas, dados_cartoes=self.dados_cartoes, dados_prontos= self.dados_desp_ass_card)

        self.frame_grafico.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.frame_grafico.renderizar()


        # FRAME SALDO
        self.frame_resumo = ctk.CTkFrame(self.top_section_frame, width=200, height=100, corner_radius=15, border_width=2 )
        self.frame_resumo.grid(row=1, column=6, padx=20, pady=10, sticky="e")

        self.label_titulo_resumo = ctk.CTkLabel(self.frame_resumo, text="SALDO DO MÊS", font=ctk.CTkFont(size=12, weight="bold"))
        self.label_titulo_resumo.pack(pady=(10, 0))

        self.label_valor_saldo = ctk.CTkLabel(self.frame_resumo, text="R$ 0,00", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_valor_saldo.pack(pady=(0, 10), padx=20)

        # Chama a função de cores usando o valor retornado
        self.atualizar_cores_saldo(self.valor_renda, ret)
        # ----- END Frame Saldo ----------


# ------------------- Lógica de atualização de dados ----------------------
    def trocar_mes(self, escolha=None):

        tocar_notificacao('open_w', True)
        
        if self.mes_atual_str == escolha:
            controle_mes = self.mes_atual

            ttf_mes = self.frame_tabela.renderizar(escolha=escolha)
            self.frame_grafico.renderizar()

        elif self.prox_mes_str == escolha:
            controle_mes = self.prox_mes

            ttf_mes = self.frame_tabela.renderizar(controle_mes, escolha=escolha)
            self.frame_grafico.renderizar(controle_mes)

        elif self.seg_prox_mes_str == escolha:
            controle_mes = self.seg_prox_mes

            ttf_mes = self.frame_tabela.renderizar(controle_mes, escolha=escolha)
            self.frame_grafico.renderizar(controle_mes)

        elif self.ter_prox_mes_str == escolha:
            controle_mes = self.ter_prox_mes

            ttf_mes = self.frame_tabela.renderizar(controle_mes, escolha=escolha)
            self.frame_grafico.renderizar(controle_mes)

        elif self.quart_prox_mes_str == escolha:
            controle_mes = self.quart_prox_mes

            ttf_mes = self.frame_tabela.renderizar(controle_mes, escolha=escolha)
            self.frame_grafico.renderizar(controle_mes)

        elif self.quint_prox_mes_str == escolha:
            controle_mes = self.quint_prox_mes

            ttf_mes = self.frame_tabela.renderizar(controle_mes, escolha=escolha)
            self.frame_grafico.renderizar(controle_mes)
        
        else:
            controle_mes = self.mes_atual
            ttf_mes = self.frame_tabela.renderizar(escolha=escolha)
            self.frame_grafico.renderizar()

        self.atualizar_cores_saldo(self.dados_usuario.get('sal_fixo'), ttf_mes, controle_mes)



    def att_app(self):
        """ O botão Atualizar  """
        
        self.config(cursor="watch")
        self.update() 

        #Puxa do banco e remonta a tela
        self.buscar_dados_banco()
        self.montar_dashboard()

        #tocar_notificacao('open', True)
        self.config(cursor="")
        print("Dashboard atualizado in-place com sucesso! 🚀")

        dados_att = {
            'receitas': self.dados_receitas,
            'despesas_avulsas': self.despesas_avulsas
        }
        return dados_att


    
    def atualizar_cores_saldo(self, sal_fixo=Decimal('0.0'), despesa=Decimal('0.0'), controle_mes=None):

        if controle_mes is None:
            controle_mes = datetime.now().month

        receitas = self.dados_receitas
        receitas_fornecidas = Decimal('0.0')

        mes_vigente = self.data_atual.month
        prox_mes = (self.data_atual + relativedelta(months=1)).month
        seg_prox_mes = (self.data_atual + relativedelta(months=2)).month


        data_prox_mes =  (self.data_atual + relativedelta(months=1))
        data_seg_prox_mes =  (self.data_atual + relativedelta(months=2))
        

        for dado in receitas:
            data_obj = mysql_para_obj(dado.get('data'))
            valor = Decimal(str(dado.get('valor_recebido')))

            if controle_mes == mes_vigente: #mes_atual
                if self.data_atual.month == data_obj.month and self.data_atual.year == data_obj.year:
                    receitas_fornecidas += valor

            elif controle_mes == prox_mes: #prox_mes
                if data_prox_mes.month == data_obj.month and data_prox_mes.year == data_obj.year:
                    receitas_fornecidas += valor

            elif controle_mes == seg_prox_mes: #seg_prox_mes
                if data_seg_prox_mes.month == data_obj.month and data_seg_prox_mes.year == data_obj.year:
                    receitas_fornecidas += valor



        receita_total = (Decimal(str(sal_fixo)) + receitas_fornecidas)

        if despesa:
            saldo =  receita_total - Decimal(str(despesa))


            if saldo > (receita_total * Decimal(str(0.30))): #se saldo é maior que 30% do que ele ganhou no mês.
                cor_status = "#2ecc71" # Verde (Sucesso)
            elif saldo >= 0:
                cor_status = "#f1c40f" # Amarelo (No limite)
            else:
                cor_status = "#e74c3c" # Vermelho (Prejuízo)

            # Aplica a cor na borda do Frame e no texto do Saldo
            self.frame_resumo.configure(border_color=cor_status)
            self.label_valor_saldo.configure(text=f"{formatar_moeda(saldo)}", text_color=cor_status)


    def salvar_renda(self):

        nova_renda = self.entry_nova_renda.get().strip()

        try:
            nova_renda = float(nova_renda.replace(',', '.'))

            sucesso = atualizar_renda(self.user_id, nova_renda)

            if sucesso:
                print('Renda atualizada com sucesso!')
                tocar_notificacao("dv_sucesso", True)

                self.modal_renda.destroy()

                self.att_app()
            else:
                print('Não foi possível atualizar renda fixa')

        except Exception as e:
            print(f'Erro Inesperado: {e}')
            tocar_notificacao('dv_erro', True)
        

# ------------- Fecha janela e volta para login -------------
    def voltar_Plogin(self):
        """ Método para voltar para a tela de login (botão 'Sair')"""

        tocar_notificacao('closed', True)

        self.nomeusuario_label.configure(text=f'Até a próxima {self.usuario_logado} !', text_color='red')
        self.update_idletasks()

        
        self.quer_voltar_login = True
        
        # Em vez de destroy() direto, usamos o after para dar 
        # tempo das animações de clique e sons terminarem.
        self.after(500, self.quit_and_destroy)


    def quit_and_destroy(self):
        self.quit()  
        self.destroy()


# ------------- Detalhamento -------------------

    #classe ---- Faturas -------
    def abrir_det_cc(self):

        nome_selecionado = self.menu_cartoes.get()
        id_card = None

        for i in self.dados_cartoes:
            if i.get('nome_cartao') == nome_selecionado:
                id_card = i.get('id_cartao')

        if id_card:
            tocar_notificacao('open_w', True)

            register_window = Faturas(self, self.user_id, id_card, nome_card=nome_selecionado, dados_card=self.dados_cartoes, dados_prontos= self.dados_desp_ass_card)

            self.wait_window(register_window)
        else:
            print("Erro: Cartão não encontrado")


    def abrir_modal_renda(self):

        self.modal_renda = ctk.CTkToplevel(self)
        self.modal_renda.title("Editar Renda Fixa")    
        centralizar_janela(self.modal_renda, 300, 200) 
        self.modal_renda.grab_set() 
        
        tocar_notificacao('open_w', True)

        ctk.CTkLabel(self.modal_renda, text="Digite a nova Renda Fixa (R$):", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 10))
    
        self.entry_nova_renda = ctk.CTkEntry(
            self.modal_renda, 
            placeholder_text="Ex: 2500.00", 
            justify="center",
            validate='key',
            validatecommand= self.vcmd_num
            )
        self.entry_nova_renda.pack(pady=10)
        
        # Botão Salvar
        btn_salvar = ctk.CTkButton(self.modal_renda, text="Salvar Modificação", fg_color="#27ae60", hover_color="#1e8449", command=self.salvar_renda)
        btn_salvar.pack(pady=(10, 20))


# ---------------- simulação -----------------------
    def abrir_simulacao(self):

        tocar_notificacao('open_w', True)
        register_window = Simulacao(self, id_user=self.user_id, despesas_avulsas= self.despesas_avulsas, assinaturas_avulsas=self.assinaturas_avulsas, dados_cartoes=self.dados_cartoes, dados_usuario=self.dados_usuario, nomes_cartoes=self.nomes_cartoes, dados_prontos=self.dados_desp_ass_card)

        self.wait_window(register_window) 


# ---------- chamada de classes forms --------------------
    def abrir_receitas(self):

        tocar_notificacao('open_w', True)
        register_window = Receitas(self, self.user_id, dados_receitas=self.dados_receitas, att_app = self.att_app)

        self.wait_window(register_window) 


    def abrir_cc(self):

        tocar_notificacao('open_w', True)
        register_window = Car_cred(self, self.user_id, dados_cartoes=self.dados_cartoes, nomes_cards=self.nomes_cartoes, att_app=self.att_app)

        self.wait_window(register_window)


    def abrir_despesas(self):

        tocar_notificacao('open_w', True)
        register_window = Despesas(self, self.user_id, self.dados_cartoes, trocar_mes=self.trocar_mes, att_app=self.att_app)

        self.wait_window(register_window)
    

    def abrir_assinaturas(self):

        tocar_notificacao('open_w', True)
        register_window = Assinaturas(self, self.user_id, self.dados_cartoes, trocar_mes=self.trocar_mes)

        self.wait_window(register_window)



  