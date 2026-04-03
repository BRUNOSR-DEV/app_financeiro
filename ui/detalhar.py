
from models.conecte_bd import (
    pega_despesas_cartao, dados_assinaturas_cartao, dados_receita, deletar_receita, dados_assinaturas_full, deletar_assinatura
     )

from utils.helper import(
    gerar_opcoes_meses, mysql_para_obj, formatar_moeda, data_para_exibicao, controle_data_parc_cc, centralizar_janela
)

from utils.audio_helper import tocar_notificacao 


from dateutil.relativedelta import relativedelta
from datetime import datetime

import customtkinter as ctk
ctk.set_appearance_mode('dark')

from CTkToolTip import *

from decimal import Decimal



class Listar_receitas(ctk.CTkFrame):

    def __init__(self,  parent=None, user_id=None, controle_dados= None, trocar_mes=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.user_id = user_id
        self.controle_dados = controle_dados
        self.trocar_mes = trocar_mes

         # --------------- Configuração da Frames/'labels' -----------------------
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


            for i, dado in enumerate(self.dados_receitas, start=1):
                #dado é o dict de uma receita
                valor = dado.get('valor_recebido')
                descricao = dado.get('descricao')
                data = dado.get('data')

                ctk.CTkLabel(self.lista_frame, text=str(i), font=('Ariel', 14)).grid(row=i, column=0, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=formatar_moeda(valor), text_color="#27ae60", font=('Ariel', 14)).grid(row=i, column=1, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=descricao, font=('Ariel', 14)).grid(row=i, column=2, padx=3, pady=1, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=data_para_exibicao(data), font=('Ariel', 14)).grid(row=i, column=3, padx=5, pady=2, sticky="e")

                btn_edit = ctk.CTkButton(self.lista_frame, text="📝", width=30, fg_color="transparent", hover_color="#34495e",
                                     command=lambda d=dado: self.confirmar_update(d))
                btn_edit.grid(row=i, column=4, padx=2)
                CTkToolTip(btn_edit, message="Editar Registro")

                btn_del = ctk.CTkButton(self.lista_frame, text="X", width=30, fg_color="#c0392b", hover_color="#e74c3c",
                                    command=lambda dados=dado: self.confirmar_delete(dados))
                btn_del.grid(row=i, column=5, padx=5)
                CTkToolTip(btn_del, 
                            message="Excluir Registro", 
                            delay=0.5,      # Tempo em segundos para aparecer
                            alpha=0.9,      # Transparência
                            bg_color="red" 
                            )


        self.lista_frame.grid_columnconfigure((4, 5), weight=0)


    def confirmar_update(self, dict_dados):

        print("Estou no'confirmar_update' mandando dados dict para crud_app")

        if dict_dados:
            self.controle_dados(dict_dados)
        else:
            self.controle_dados(None)



    def confirmar_delete(self, dados):
        
        popup = ctk.CTkToplevel(self)
        popup.title("Confirmação")
        centralizar_janela(popup, 300, 150)

        popup.grab_set()

        popup.grid_columnconfigure((0, 1), weight=1)

        label = ctk.CTkLabel(popup, text="Tem certeza que deseja\nexcluir esta receita?", font=("Arial", 14))
        label.grid(row=0, column=0, columnspan=2, pady=20)

        btn_cancelar = ctk.CTkButton(popup, text="Cancelar", fg_color="gray", hover_color="#555555",
                                 command=popup.destroy)
        btn_cancelar.grid(row=1, column=0, padx=10, pady=10)

        btn_confirmar = ctk.CTkButton(popup, text="Sim, excluir", fg_color="#c0392b", hover_color="#e74c3c",
                                  command=lambda: self.executar_delete(dados, popup))
        btn_confirmar.grid(row=1, column=1, padx=10, pady=10)


    def executar_delete(self, dados, popup):
        
        id_rec = dados.get('id_receita')
        int_mes = mysql_para_obj(dados.get('data')).month
        descricao = dados.get('descricao')

        sucesso = deletar_receita(id_rec)

        if sucesso:

            print(f"ID {id_rec} receita: '{descricao}'. Mandado pro espaço 🌌​")
            tocar_notificacao("sucesso")

            self.listar()

            self.trocar_mes(escolha=gerar_opcoes_meses().get(int_mes))

            popup.destroy()

        else:
            print("Erro ao deletar")
            tocar_notificacao("erro")

            


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

    def __init__(self, parent=None, user_id=None, dados_cartoes=None, controle_dados=None, trocar_mes=None):
        super().__init__(parent)

        self.user_id = user_id
        self.dados_cartoes = dados_cartoes 
        self.controle_dados = controle_dados
        self.trocar_mes = trocar_mes


        # --------------- Configuração da Frames/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.lista_frame = ctk.CTkScrollableFrame(self, label_text="Assinaturas Cadastradas")
        self.lista_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.lista_frame.grid_columnconfigure((0, 1, 2, 4, 5, 6, 7), weight=0) # Index, Valor e Data fixos
        self.lista_frame.grid_columnconfigure(3, weight=1) #Descriçao estica


        #cabeçalho
        ctk.CTkLabel(self.lista_frame, text='#', font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text='Nome', font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Valor", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Descrição", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Data Aquisisão", font=ctk.CTkFont(weight="bold")).grid(row=0, column=4, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Data P/Pagamento", font=ctk.CTkFont(weight="bold")).grid(row=0, column=5, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Categoria", font=ctk.CTkFont(weight="bold")).grid(row=0, column=6, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.lista_frame, text="Cartão Utilizado", font=ctk.CTkFont(weight="bold")).grid(row=0, column=7, padx=5, pady=5, sticky="w")

        self.listar()


    def listar(self):

        for widget in self.lista_frame.winfo_children():
            if int(widget.grid_info().get("row", 0)) > 0:
                widget.destroy()

        self.dados_assinaturas = dados_assinaturas_full(self.user_id)

        if self.dados_assinaturas:
            
            nome_card = None
                #id_ass, nome, valor, descricao, data_aquisicao, data_prim_pag, categoria, id_cc
            for i, dado in enumerate(self.dados_assinaturas, start=1):

                nome = dado.get('nome')
                valor = dado.get('valor')
                desc = dado.get('descricao')
                data_aq = dado.get('data_aquisicao')
                data_pp = dado.get('data_prim_pag')
                cat = dado.get('categoria')

                if self.dados_cartoes:
                    for cartao in self.dados_cartoes:
                        if cartao.get('id_cartao') == dado.get('id_cc'):
                            nome_card = cartao.get('nome_cartao')

                ctk.CTkLabel(self.lista_frame, text=str(i), font=('Ariel', 14)).grid(row=i, column=0, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=nome, font=('Ariel', 14)).grid(row=i, column=1, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=str(valor), text_color="#27ae60", font=('Ariel', 14)).grid(row=i, column=2, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=desc, font=('Ariel', 14)).grid(row=i, column=3, padx=3, pady=1, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=data_aq, font=('Ariel', 14)).grid(row=i, column=4, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=data_pp, font=('Ariel', 14)).grid(row=i, column=5, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=cat, font=('Ariel', 14)).grid(row=i, column=6, padx=5, pady=2, sticky="w")
                ctk.CTkLabel(self.lista_frame, text=nome_card, font=('Ariel', 14)).grid(row=i, column=7, padx=5, pady=2, sticky="w")

                btn_edit = ctk.CTkButton(self.lista_frame, text="📝", width=30, fg_color="transparent", hover_color="#34495e",
                                     command=lambda dados=dado: self.confirmar_update(dados))
                btn_edit.grid(row=i, column=8, padx=2)
                CTkToolTip(btn_edit, message="Editar Registro")

                btn_del = ctk.CTkButton(self.lista_frame, text="X", width=30, fg_color="#c0392b", hover_color="#e74c3c",
                                    command=lambda dados=dado: self.confirmar_delete(dados))
                btn_del.grid(row=i, column=9, padx=5)
                CTkToolTip(btn_del, 
                            message="Excluir Registro", 
                            delay=0.5,      # Tempo em segundos para aparecer
                            alpha=0.9,      # Transparência
                            bg_color="red" 
                            )


    def confirmar_update(self, dados):
        print("Estou no'confirmar_update' mandando dados (dict) para crud_app")

        if dados:
            self.controle_dados(dados)
        else:
            self.controle_dados(None)


    def confirmar_delete(self, dados):

        popup = ctk.CTkToplevel(self)
        popup.title("Confirmação")
        centralizar_janela(popup, 300, 150)

        popup.grab_set()

        popup.grid_columnconfigure((0, 1), weight=1)

        label = ctk.CTkLabel(popup, text="Tem certeza que deseja\nexcluir esta assinatura?", font=("Arial", 14))
        label.grid(row=0, column=0, columnspan=2, pady=20)

        btn_cancelar = ctk.CTkButton(popup, text="Cancelar", fg_color="gray", hover_color="#555555",
                                 command=popup.destroy)
        btn_cancelar.grid(row=1, column=0, padx=10, pady=10)

        btn_confirmar = ctk.CTkButton(popup, text="Sim, excluir!", fg_color="#c0392b", hover_color="#e74c3c",
                                  command=lambda: self.executar_delete(dados, popup))
        btn_confirmar.grid(row=1, column=1, padx=10, pady=10)


    def executar_delete(self, dados, popup):
        
        id_ass = dados.get('id_ass')
        data_pp = dados.get('data_aquisicao')

        if data_pp:
            int_mes = mysql_para_obj(data_pp).month
        else:
            int_mes = datetime.now().date().month
        
        descricao = dados.get('descricao')

        sucesso = deletar_assinatura(id_ass)

        if sucesso:

            print(f"ID {id_ass} receita: '{descricao}'. Mandado pro espaço 🌌​")
            tocar_notificacao('dv_delete', True)

            self.listar()

            self.trocar_mes(escolha=gerar_opcoes_meses().get(int_mes))

            popup.destroy()

        else:
            print("Erro ao deletar")
            tocar_notificacao("dv_erro", True)

#-----------------  Detalhes da fatura dos cartões -----------------------------------------

class Listar_faturas_cartao(ctk.CTkFrame):
    
    def __init__(self, parent, id_user, id_card, nome_card, callback=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # ---------------- Gerencimento de self ---------------------
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
        

        # --------------- Configuração da Frames/'labels' -----------------------
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1) 

    
        self.label_titulo = ctk.CTkLabel(self, text=f"Fatura: {nome_card}", font=("Arial", 22, "bold"))
        self.label_titulo.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        self.main_content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

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
            



        self.tabela_frame.grid_columnconfigure(0, weight=2)
        self.tabela_frame.grid_columnconfigure((1, 2, 3), weight=1)



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

        self.tabela_frame_prox.grid_columnconfigure(0, weight=2) 
        self.tabela_frame_prox.grid_columnconfigure((1, 2, 3), weight=1)


