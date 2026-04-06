

from datetime import datetime
from dateutil.relativedelta import relativedelta
import locale
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

from models.conecte_bd import (
     dados_user, pega_id, dados_card,pega_despesas_cartao, pega_despesas, dados_receita, dados_assinaturas_avulsas, dados_assinaturas_cartao
     )

from utils.helper import(
    gerar_opcoes_meses, controle_data_parc, mysql_para_obj, formatar_moeda, data_para_exibicao, controle_data_parc_cc, centralizar_janela
)

from utils.audio_helper import tocar_notificacao 
from ui.crud_app import (
    Faturas, Receitas, Despesas, Car_cred, Assinaturas
)


#gráficos
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import customtkinter as ctk
ctk.set_appearance_mode('dark')

from decimal import Decimal
from collections import defaultdict 


class Main_app(ctk.CTk):

    def __init__(self, logged_in_username=None):
        super().__init__()

        self.usuario_logado = logged_in_username
        self.title("Controle Financeiro")
        centralizar_janela(self, 1500, 800)

        self.container_principal = ctk.CTkFrame(self, fg_color="transparent")
        self.container_principal.pack(fill="both", expand=True)

        # Carrega os dados e monta a tela pela PRIMEIRA vez
        self.buscar_dados_banco()
        self.montar_dashboard()


    def buscar_dados_banco(self):
        """ Função exclusiva para buscar/calcular dados. """
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
        self.top_section_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.top_section_frame.grid_columnconfigure(0, weight=0)
        self.top_section_frame.grid_columnconfigure(1, weight=1) # Empurra o botão pra direita

        texto_boas_vindas = f"Bem-vindo, {self.dados_usuario.get('nome_completo')}!" if self.usuario_logado else "Bem-vindo!"
        self.nomeusuario_label = ctk.CTkLabel(self.top_section_frame, text=texto_boas_vindas, font=ctk.CTkFont(size=16, weight="bold"))
        self.nomeusuario_label.grid(row=0, column=0, pady=(0, 10), sticky="w")
            
        self.btn_att_app = ctk.CTkButton(self.top_section_frame, text="Atualizar", command=self.att_app, width=80, fg_color="#0400FF", hover_color="#024389")
        self.btn_att_app.grid(row=0, column=1, sticky="e")
        
        self.mes_vigente_label = ctk.CTkLabel(self.top_section_frame, text=f"Mês : ", font=ctk.CTkFont(size=16, weight="bold"))
        self.mes_vigente_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")

        self.menu_mes = ctk.CTkOptionMenu(self.top_section_frame, values=self.nomes_datas, command=self.trocar_mes)
        self.menu_mes.grid(row=0, column=3, padx=10, pady=5)
            
        self.botao_sair = ctk.CTkButton(self.top_section_frame, text="Sair", command=self.voltar_Plogin, width=80, fg_color="#FF0000", hover_color="#810000")
        self.botao_sair.grid(row=0, column=4, sticky="e") 
        
        # FRAME DE BOTÕES DE CADASTRO
        self.cadastro_frame = ctk.CTkFrame(self.top_section_frame, fg_color="transparent")
        self.cadastro_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")
        self.cadastro_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1) 

        self.btn_receitas = ctk.CTkButton(self.cadastro_frame, text="Gerenciar Receitas", command=self.abrir_receitas)
        self.btn_receitas.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.btn_despesas = ctk.CTkButton(self.cadastro_frame, text="Gerenciar Despesas", command=self.abrir_despesas)
        self.btn_despesas.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.btn_cc = ctk.CTkButton(self.cadastro_frame, text="Gerenciar C.Crédito", command=self.abrir_cc)
        self.btn_cc.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

        self.btn_assin = ctk.CTkButton(self.cadastro_frame, text="Gerenciar Assinaturas", command=self.abrir_assinaturas)
        self.btn_assin.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        self.label_cc = ctk.CTkLabel(self.cadastro_frame, text="Selecione o Cartão:")
        self.label_cc.grid(row=0, column=4, padx=10, pady=5)

        self.menu_cartoes = ctk.CTkOptionMenu(self.cadastro_frame, values=self.nomes_cartoes, width=80, fg_color="#FF8000")
        self.menu_cartoes.grid(row=1, column=4, padx=10, pady=5)

        self.det_despesas_cc = ctk.CTkButton(self.cadastro_frame, text="Detalhar", command=self.abrir_det_cc, width=80, fg_color="#FF8000", hover_color="#813C00")
        self.det_despesas_cc.grid(row=1, column=5, padx=2, pady=2, sticky="ew")


        # ---------------
        # MAIN CONTENT 
        # ---------------
        self.main_content_frame = ctk.CTkFrame(self.container_principal, fg_color="transparent")
        self.main_content_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.main_content_frame.grid_columnconfigure(0, weight=2) 
        self.main_content_frame.grid_columnconfigure(1, weight=1) 
        self.main_content_frame.grid_rowconfigure(0, weight=1)

        # FRAME TABELA
        self.tabela_frame = ctk.CTkScrollableFrame(self.main_content_frame, label_text=f"Pagamentos Detalhados: {self.mes_atual_str} / {self.data_atual.year}")
        self.tabela_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew") 

        total_dividas = self.preencher_total_dividas(self.user_id) # Executa e guarda o valor

        # FRAME GRÁFICO
        self.grafico_frame = ctk.CTkFrame(self.main_content_frame)
        self.grafico_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.grafico_frame.grid_columnconfigure(0, weight=2)
        self.grafico_frame.grid_rowconfigure(1, weight=1)

        self.gerar_grafico_mensal()

        # FRAME SALDO
        self.frame_resumo = ctk.CTkFrame(self.top_section_frame, width=250, height=100, corner_radius=15, border_width=2 )
        self.frame_resumo.grid(row=1, column=6, padx=20, pady=10, sticky="n")

        self.label_titulo_resumo = ctk.CTkLabel(self.frame_resumo, text="SALDO DO MÊS", font=ctk.CTkFont(size=12, weight="bold"))
        self.label_titulo_resumo.pack(pady=(10, 0))

        self.label_valor_saldo = ctk.CTkLabel(self.frame_resumo, text="R$ 0,00", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_valor_saldo.pack(pady=(0, 10), padx=20)

        # Chama a função de cores usando o valor retornado
        self.atualizar_cores_saldo(self.dados_usuario.get('sal_fixo'), total_dividas)


# ------------------- Lógica de atualização de dados ----------------------

    def trocar_mes(self, escolha=None):

        tocar_notificacao('open_w', True)
        
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
            
        else:
            controle_mes = 1
            att_mes = self.preencher_total_dividas(self.user_id)
            self.gerar_grafico_mensal()

        self.atualizar_cores_saldo(self.dados_usuario.get('sal_fixo'), att_mes, controle_mes)

        self.tabela_frame._label.configure(text=f"Pagamentos Detalhados: {escolha} / {self.data_atual.year}")


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


    def atualizar_cores_saldo(self, sal_fixo, despesa, controle_mes=1):

        receitas = dados_receita(self.user_id)
        receitas_fornecidas = Decimal('0.0')

        prox_mes =  (self.data_atual + relativedelta(months=1))
        seg_prox_mes =  (self.data_atual + relativedelta(months=2))
        

        for dado in receitas:
            data_obj = mysql_para_obj(dado.get('data'))
            valor = Decimal(str(dado.get('valor_recebido')))

            if controle_mes == 1: #mes_atual
                if self.data_atual.month == data_obj.month and self.data_atual.year == data_obj.year:
                    receitas_fornecidas += valor

            elif controle_mes == 2: #prox_mes
                if prox_mes.month == data_obj.month and prox_mes.year == data_obj.year:
                    receitas_fornecidas += valor

            elif controle_mes == 3: #seg_prox_mes
                if seg_prox_mes.month == data_obj.month and seg_prox_mes.year == data_obj.year:
                    receitas_fornecidas += valor



        receita_total = (Decimal(str(sal_fixo)) + receitas_fornecidas)
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


# ------------- chamada de classes detalhar_app -------------------
    def abrir_det_cc(self):

        nome_selecionado = self.menu_cartoes.get()
        id_card = None

        for i in self.dados_cartoes:
            if i.get('nome_cartao') == nome_selecionado:
                id_card = i.get('id_cartao')

        if id_card:
            tocar_notificacao('open_w', True)

            register_window = Faturas(self, self.user_id, id_card, nome_card=nome_selecionado, callback=self.trocar_mes)

            self.wait_window(register_window)
        else:
            print("Erro: Cartão não encontrado")


# ---------- chamada de classes forms --------------------
    def abrir_receitas(self):

        tocar_notificacao('open_w', True)
        register_window = Receitas(self, self.user_id, trocar_mes = self.trocar_mes)

        self.wait_window(register_window) 


    def abrir_cc(self):

        tocar_notificacao('open_w', True)
        register_window = Car_cred(self, self.user_id, nomes_cards=self.nomes_cartoes, att_app=self.att_app)

        self.wait_window(register_window)


    def abrir_despesas(self):

        tocar_notificacao('open_w', True)
        register_window = Despesas(self, self.user_id, self.dados_cartoes, trocar_mes=self.trocar_mes, att_app=self.att_app)

        self.wait_window(register_window)
    

    def abrir_assinaturas(self):

        tocar_notificacao('open_w', True)
        register_window = Assinaturas(self, self.user_id, self.dados_cartoes, trocar_mes=self.trocar_mes)

        self.wait_window(register_window)




# -------------- gráfico e tabela -----------------------

    def gerar_grafico_mensal(self, controle_mes= 1):

        print(f"Calculando dados : Está {controle_mes}")

        for widget in self.grafico_frame.winfo_children():
            widget.destroy()

        assin = dados_assinaturas_avulsas(self.user_id)

        gastos_por_categoria = defaultdict(Decimal)
        total_previsto = Decimal('0.0')
    
        # Pegamos os dados necessários
        id_cartoes = [d.get('id_cartao') for d in self.dados_cartoes]
        desp_avulsas = pega_despesas(self.user_id)
        

        #DESPESAS DE CARTÃO
        for id_cc in id_cartoes:

            desp_cc = pega_despesas_cartao(self.user_id, id_cc)
            assin_card = dados_assinaturas_cartao(self.user_id, id_cc)

            for ass in assin_card:
                dia_f = ass.get('dia_fechamento_cc')
                dia_v = ass.get('dia_vencimento_cc')
                data_aquisicao = ass.get('data_aquisicao')

                resultado = controle_data_parc_cc(data_aquisicao, dia_f, dia_v, controle_mes= controle_mes)
                _, entra_na_fatura, _ = resultado

                if entra_na_fatura:
                    valor = Decimal(str(ass.get('valor')))
                    # SOMA NO DICIONÁRIO USANDO A CATEGORIA
                    categoria = ass.get('categoria', 'Outros')
                    gastos_por_categoria[categoria] += valor
                    total_previsto += valor
        
            for desp in desp_cc:
                data_compra = mysql_para_obj(desp.get('data_compra'))
                dia_venc = desp.get('vencimento_fatura')
                fechamento = desp.get('fechamento_fatura')
                parcelas = desp.get('parcelas')

                # Verifica se entra na fatura atual
                resultado = controle_data_parc_cc(data_compra, fechamento, dia_venc, parcelas, controle_mes= controle_mes)
                _, entra_na_fatura, _ = resultado

                if entra_na_fatura:
                    valor_mensal = Decimal(str(desp.get('valor_total'))) / parcelas
                    # SOMA NO DICIONÁRIO USANDO A CATEGORIA
                    categoria = desp.get('categoria', 'Outros')
                    gastos_por_categoria[categoria] += valor_mensal
                    total_previsto += valor_mensal



        # parte avulsas
        for desp in desp_avulsas:
            primeira_parc = mysql_para_obj(desp.get('primeira_parc'))
            parcelas = desp.get('parcelas')
            dia_venc = desp.get('dia_vencimento')
        
            # Usando sua função de controle para avulsas
            resultado = controle_data_parc(primeira_parc, dia_venc , parcelas, controle_mes = controle_mes)
            _, entra_no_mes, _ = resultado

            if entra_no_mes:
                valor_mensal = Decimal(str(desp.get('valor_total'))) / parcelas
                categoria = desp.get('categoria', 'Outros')
                gastos_por_categoria[categoria] += valor_mensal
                total_previsto += valor_mensal

                
        for ass in assin:

            data_pp = mysql_para_obj(ass.get('data_pp'))
            dia_venc = ass.get('dia_vencimento')
            valor = ass.get('valor')

            resultado = controle_data_parc(data_pp, dia_venc, controle_mes = controle_mes)
            _, entra_no_mes, _ = resultado

            if entra_no_mes:
                total_previsto += valor
                categoria = desp.get('categoria', 'Outros')
                gastos_por_categoria[categoria] += valor
            
        #Verifica se tem algo para mostrar
        if total_previsto == Decimal('0.0'):
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
        ax.set_title(f"Distribuição de Gastos\nTotal: {formatar_moeda(total_previsto)}", color='white', fontsize=12)

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
        assin = dados_assinaturas_avulsas(id_user) 

        total_avulsas = Decimal('0.0')
        total_cards = Decimal('0.0')
        #Lógica para montar lista com o total de cada cartão

        lista_faturas_resumo = []
        if cartoes:
            for cartao in cartoes:
                nome_cartao = cartao.get('nome_cartao')
                id_cartao = cartao.get('id_cartao') 
            
                despesas_do_cartao = pega_despesas_cartao(id_user, id_cartao)
                assin_card = dados_assinaturas_cartao(id_user, id_cartao)
            
                total_deste_cartao = Decimal('0.0')
                data_vencimento_fatura = None

                if assin_card:
                    for ass in assin_card:

                        dia_f = ass.get('dia_fechamento_cc')
                        dia_v = ass.get('dia_vencimento_cc')
                        data_aquisicao = ass.get('data_aquisicao')

                        resultado = controle_data_parc_cc(data_aquisicao, dia_f, dia_v, controle_mes= controle_mes)
                        _, entra_na_fatura, _ = resultado

                        if entra_na_fatura:
                            valor = Decimal(str(ass.get('valor')))
                            total_deste_cartao += valor

                if despesas_do_cartao:

                    for desp in despesas_do_cartao:

                        data_compra = mysql_para_obj(desp.get('data_compra'))
                        dia_venc = desp.get('vencimento_fatura')
                        fechamento = desp.get('fechamento_fatura')
                        parcelas = desp.get('parcelas')


                        resultado = controle_data_parc_cc(data_compra, fechamento, dia_venc, parcelas, controle_mes= controle_mes)
                        _, entra_na_fatura, controle_data = resultado

                        if entra_na_fatura:
                            valor_mensal = Decimal(str(desp.get('valor_total'))) / parcelas
                            total_deste_cartao += valor_mensal
                            data_vencimento_fatura = controle_data 

                        

                # Se o cartão tem fatura para pagar, guardamos na lista
                if total_deste_cartao > Decimal('0.0'):
                    lista_faturas_resumo.append({
                        'local': f"Fatura - {nome_cartao}",
                        'valor': total_deste_cartao,
                        'vencimento': data_vencimento_fatura
                    })

    
        # Se tiver despesas avulsas OU tiver faturas de cartão, a gente desenha a tabela
        if despesas or lista_faturas_resumo or assin:
        
            # Cabeçalho
            ctk.CTkLabel(self.tabela_frame, text="Local/Nome", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self.tabela_frame, text="Parcelas", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self.tabela_frame, text="Mensalidade/Valor", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5, sticky="e")
            ctk.CTkLabel(self.tabela_frame, text="Vencimento", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5, sticky="w")

            linha = 1



            total_ass_avulcas = Decimal('0.0')

            if assin: 
                
                for ass in assin:

                        data_pp = mysql_para_obj(ass.get('data_pp'))
                        dia_venc = ass.get('dia_vencimento')
                        nome = ass.get('nome')
                        valor = ass.get('valor')

                        resultado = controle_data_parc(data_pp, dia_venc, total_parcelas=None, controle_mes = controle_mes )
                        str_sit, entra_no_mes, data_vencimento = resultado

                        if entra_no_mes:

                            total_ass_avulcas += Decimal(str(valor))

                            ctk.CTkLabel(self.tabela_frame, text=nome).grid(row=linha, column=0, padx=5, pady=2, sticky="w")
                            ctk.CTkLabel(self.tabela_frame, text=str_sit).grid(row=linha, column=1, padx=3, pady=1, sticky="w")
                            ctk.CTkLabel(self.tabela_frame, text=formatar_moeda(valor), justify=ctk.LEFT, text_color="red").grid(row=linha, column=2, padx=5, pady=2, sticky="e")
                            ctk.CTkLabel(self.tabela_frame, text=data_para_exibicao(data_vencimento)).grid(row=linha, column=3, padx=5, pady=2, sticky="w")


                        linha += 1


            if despesas:

                for _, dados in enumerate(despesas):
                    primeira_parc = mysql_para_obj(dados.get('primeira_parc'))
                    dia_venc = primeira_parc.day
                
                    resultado_avulso = controle_data_parc(primeira_parc, dia_venc, dados.get('parcelas'), controle_mes= controle_mes)

                    str_parcela, control_parc, data_vencimento = resultado_avulso

                    dia_venc = int(primeira_parc.day)

                    if data_vencimento:
                        data_fatura = data_vencimento
                    else:
                        data_fatura = datetime.now().replace(day=dia_venc)

                    if control_parc:
                        valor_mensal = Decimal(str(dados.get('valor_total'))) / dados.get('parcelas')
                    
                        ctk.CTkLabel(self.tabela_frame, text=dados.get('local')).grid(row=linha, column=0, padx=5, pady=2, sticky="w")
                        ctk.CTkLabel(self.tabela_frame, text=str_parcela).grid(row=linha, column=1, padx=3, pady=1, sticky="w")
                        ctk.CTkLabel(self.tabela_frame, text=formatar_moeda(valor_mensal), justify=ctk.LEFT, text_color="green").grid(row=linha, column=2, padx=5, pady=2, sticky="e")
                        ctk.CTkLabel(self.tabela_frame, text=data_para_exibicao(data_fatura)).grid(row=linha, column=3, padx=5, pady=2, sticky="w")

                        total_avulsas += valor_mensal
                    
                        linha += 1
          
            # Desenha o Resumo das Faturas dos Cartões
            for fatura in lista_faturas_resumo:

                ctk.CTkLabel(self.tabela_frame, text=fatura['local']).grid(row=linha, column=0, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.tabela_frame, text="-").grid(row=linha, column=1, padx=3, pady=1, sticky="w") 
                ctk.CTkLabel(self.tabela_frame, text=formatar_moeda(fatura['valor']), justify=ctk.LEFT, text_color="orange").grid(row=linha, column=2, padx=5, pady=2, sticky="e")
            
                # Formata a data se ela não vier vazia
                venc_str = data_para_exibicao(fatura['vencimento']) if fatura['vencimento'] else "N/A"
                ctk.CTkLabel(self.tabela_frame, text=venc_str).grid(row=linha, column=3, padx=5, pady=2, sticky="w")

                total_cards += fatura['valor']

                linha += 1

            ctk.CTkLabel(
                self.tabela_frame, 
                text="TOTAL DESPESAS:", 
                font=ctk.CTkFont(weight="bold", size=14)
            ).grid(row=linha, column=0, columnspan=2, padx=5, pady=(20, 5), sticky="e")

            ctk.CTkLabel(
                self.tabela_frame, 
                text=formatar_moeda((total_avulsas + total_cards + total_ass_avulcas)), 
                font=ctk.CTkFont(weight="bold", size=14), 
                text_color="red" 
            ).grid(row=linha, column=2, padx=5, pady=(20, 5), sticky="e")

            self.tabela_frame.grid_columnconfigure(2, weight=1)

            return (total_avulsas + total_cards + total_ass_avulcas)

        else:
            ctk.CTkLabel(self.tabela_frame, text="Nenhum pagamento previsto.").grid(row=0, column=0, padx=10, pady=10)
            self.tabela_frame.grid_columnconfigure(2, weight=1)


    