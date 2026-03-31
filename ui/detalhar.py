
from models.conecte_bd import (
    pega_despesas_cartao, dados_assinaturas_cartao, dados_receita
     )

from utils.helper import(
    gerar_opcoes_meses, mysql_para_obj, formatar_moeda, data_para_exibicao, controle_data_parc_cc
)


from dateutil.relativedelta import relativedelta
from datetime import datetime

import customtkinter as ctk
ctk.set_appearance_mode('dark')

from decimal import Decimal



class Listar_receitas(ctk.CTkFrame):

    def __init__(self,  parent=None, user_id=None, callback = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.callback = callback


         # --------------- Configuração da janela/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.lista_frame = ctk.CTkScrollableFrame(self, label_text="Receitas Cadastradas")
        self.lista_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.lista_frame.grid_columnconfigure((0, 1, 3), weight=0) # Index, Valor e Data fixos
        self.lista_frame.grid_columnconfigure(2, weight=1) #Descriçao estica

        #ctk.CTkLabel(self.lista_frame, text="Receitas Cadastradas", font=("Arial", 18, "bold")).grid(row=0, column=0, padx=10, pady=10)

        #cabeçalho
        ctk.CTkLabel(self.lista_frame, text='#', font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Valor", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Descrição", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Data Recebimento", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        



        self.listar()

       
    def listar(self):

        for widget in self.lista_frame.winfo_children():
            if int(widget.grid_info().get("row", 0)) > 0:
                widget.destroy()

        self.dados_receitas = dados_receita(self.user_id)

        if self.dados_receitas:


            for i ,dado in enumerate(self.dados_receitas, start=1):
                
                valor = dado.get('valor_recebido')
                descricao = dado.get('descricao')
                data = dado.get('data')

                ctk.CTkLabel(self.lista_frame, text=str(i)).grid(row=i, column=0, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=formatar_moeda(valor), text_color="#27ae60").grid(row=i, column=1, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=descricao).grid(row=i, column=2, padx=3, pady=1, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=data_para_exibicao(data)).grid(row=i, column=3, padx=5, pady=2, sticky="e")

                btn_edit = ctk.CTkButton(self.lista_frame, text="📝", width=30, fg_color="transparent", hover_color="#34495e",
                                     command=lambda d=dado: self.confirmar_update(d))
                btn_edit.grid(row=i, column=4, padx=2)

                btn_del = ctk.CTkButton(self.lista_frame, text="X", width=30, fg_color="#c0392b", hover_color="#e74c3c",
                                    command=lambda id_rec=dado.get('id_receita'): self.confirmar_delete(id_rec))
                btn_del.grid(row=i, column=5, padx=5)


        self.lista_frame.grid_columnconfigure((4, 5), weight=0)


    def confirmar_update(self, dict_dados):

        print("Estou no'confirmar_update' mandando dados dict para crud_app")

        if dict_dados:
            self.callback(dict_dados)
        else:
            self.callback(None)


    def confirmar_delete(self, id_rec):
        pass
        

class Listar_despesas(ctk.CTkFrame):

    def __init__(self,  parent=None, user_id=None, dados_cartoes =None, callback=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.dados_cartoes = dados_cartoes
        self.callback = callback





class Listar_car_cred(ctk.CTkFrame):

    def __init__(self,  parent=None, user_id=None, nomes_cards =None, callback = None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.callback = callback
        self.nomes_cards = nomes_cards


class Listar_assinaturas(ctk.CTkFrame):

    def __init__(self, parent=None, user_id=None, dados_cartoes=None, callback=None):
        super().__init__(parent)


        self.callback = callback
        self.user_id = user_id
        self.dados_cartoes = dados_cartoes 






#-----------------  Detalhes da fatura dos cartões -----------------------------------------

class Faturas_cartao(ctk.CTkToplevel):
    
    def __init__(self, parent, id_user, id_card, nome_card, callback=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.title(f"Detalhes: {nome_card}")
        self.geometry("1000x800")
        self.transient(parent)
        
        # Garante que a janela fique na frente
        self.attributes("-topmost", True) 

        self.calback = callback

        self.data_atual = datetime.now().date()
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
        self.grid_rowconfigure(1, weight=1) 

        self.label_titulo = ctk.CTkLabel(self, text=f"Fatura: {nome_card}", font=("Arial", 22, "bold"))
        self.label_titulo.grid(row=0, column=0, pady=20)
        

        self.main_content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

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
        assin = dados_assinaturas_cartao(id_user, id_card)

        data_teste = mysql_para_obj('2026-06-02')

        total_fatura = Decimal('0.0')
        total_assin = Decimal('0.0')


        if dados_desp_card or assin:

                        # Cabeçalho
            ctk.CTkLabel(self.tabela_frame, text="Local.", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self.tabela_frame, text="Parcelas", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5, sticky="e")
            ctk.CTkLabel(self.tabela_frame, text="Valor", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self.tabela_frame, text="Vencimento", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5, sticky="w")

            linha = 1

            for ass in assin:

                data_aquisicao = ass.get('data_aquisicao')
                nome = ass.get('nome')
                valor = ass.get('valor')
                dia_f = ass.get('dia_fechamento_cc')
                dia_v = ass.get('dia_vencimento_cc')

                resultado = controle_data_parc_cc(data_aquisicao, dia_f, dia_v, controle_mes = controle_mes )
                str_sit, entra_no_mes, data_vencimento = resultado

                if entra_no_mes:

                    total_assin += Decimal(str(valor))

                    ctk.CTkLabel(self.tabela_frame, text=nome).grid(row=linha, column=0, padx=5, pady=2, sticky="w")
                    ctk.CTkLabel(self.tabela_frame, text=str_sit).grid(row=linha, column=1, padx=3, pady=1, sticky="w")
                    ctk.CTkLabel(self.tabela_frame, text=formatar_moeda(valor), justify=ctk.LEFT, text_color="red").grid(row=linha, column=2, padx=5, pady=2, sticky="e")
                    ctk.CTkLabel(self.tabela_frame, text=data_para_exibicao(data_vencimento)).grid(row=linha, column=3, padx=5, pady=2, sticky="w")


                    linha += 1

            for _, dado  in enumerate(dados_desp_card):
                
                data_compra = mysql_para_obj(dado.get('data_compra'))
                fecha_fatura = dado.get('fechamento_fatura')
                dia_venc = dado.get('vencimento_fatura')
                parcelas = dado.get('parcelas')


                resultado = controle_data_parc_cc(data_compra, fecha_fatura ,dia_venc, parcelas, controle_mes=controle_mes)

                str_parc, control_parc, controle_data = resultado


                if control_parc:
                    
                    valor_mensal = Decimal(str(dado.get('valor_total'))) / dado.get('parcelas')
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
                text=formatar_moeda(total_fatura + total_assin), 
                font=ctk.CTkFont(weight="bold", size=14), 
                text_color="red" 
            ).grid(row=linha, column=2, padx=5, pady=(20, 5), sticky="e")
            



        self.tabela_frame.grid_columnconfigure(2, weight=1)



    def tabela_prox(self, id_user, id_card, controle_mes = 2):

        for widget in self.tabela_frame_prox.winfo_children():
            widget.destroy()

        dados_desp_card = pega_despesas_cartao(id_user, id_card)
        assin = dados_assinaturas_cartao(id_user, id_card)

        data_teste = mysql_para_obj('2026-06-02')

        total_fatura = Decimal('0.0')
        total_assin = Decimal('0.0')

        data_atual = data_atual = datetime.now().date()
        

        if dados_desp_card or assin:

                        # Cabeçalho
            ctk.CTkLabel(self.tabela_frame_prox, text="Local.", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self.tabela_frame_prox, text="Parcelas", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5, sticky="e")
            ctk.CTkLabel(self.tabela_frame_prox, text="Valor", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
            ctk.CTkLabel(self.tabela_frame_prox, text="Vencimento", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5, sticky="w")

            linha = 1


            for ass in assin:

                data_aquisicao = ass.get('data_aquisicao')
                nome = ass.get('nome')
                valor = ass.get('valor')
                
                dia_f = ass.get('dia_fechamento_cc')
                dia_v = ass.get('dia_vencimento_cc')

                resultado = controle_data_parc_cc(data_aquisicao, dia_f, dia_v, controle_mes = controle_mes )

                str_sit, entra_no_mes, data_vencimento = resultado

                if entra_no_mes:

                    total_assin += Decimal(str(valor))

                    ctk.CTkLabel(self.tabela_frame_prox, text=nome).grid(row=linha, column=0, padx=5, pady=2, sticky="w")
                    ctk.CTkLabel(self.tabela_frame_prox, text=str_sit).grid(row=linha, column=1, padx=3, pady=1, sticky="w")
                    ctk.CTkLabel(self.tabela_frame_prox, text=formatar_moeda(valor), justify=ctk.LEFT, text_color="red").grid(row=linha, column=2, padx=5, pady=2, sticky="e")
                    ctk.CTkLabel(self.tabela_frame_prox, text=data_para_exibicao(data_vencimento)).grid(row=linha, column=3, padx=5, pady=2, sticky="w")


                    linha += 1

            for _, dado  in enumerate(dados_desp_card):
                
                data_compra = mysql_para_obj(dado.get('data_compra'))
                fecha_fatura = dado.get('fechamento_fatura')
                parcelas = dado.get('parcelas')
                dia_venc = dado.get('vencimento_fatura')

                resultado = controle_data_parc_cc(data_compra, fecha_fatura, dia_venc, parcelas, controle_mes= controle_mes)

                str_parc, control_parc, controle_data = resultado

                if control_parc:
                    
                    valor_mensal = Decimal(str(dado.get('valor_total'))) / dado.get('parcelas')
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
                text=formatar_moeda(total_fatura + total_assin), 
                font=ctk.CTkFont(weight="bold", size=14), 
                text_color="red" 
            ).grid(row=linha, column=2, padx=5, pady=(20, 5), sticky="e")

        self.tabela_frame.grid_columnconfigure(2, weight=1)


