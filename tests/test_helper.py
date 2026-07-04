import unittest
from datetime import date
from utils.helper import controle_data_parc_cc

class TestControleDataParcCC(unittest.TestCase):

    def setUp(self):
        """Prepara datas base fixas para os testes simulando o tempo de forma estática."""
        #data atual em 15/05/2026 para todos os testes terem a mesma base temporal

        self.data_atual_mock = date(2026, 5, 15)
        self.mes_vigente = 5


    def test_assinatura_ativa_no_mes_vigente(self):
        """Assinatura deve ser exibida como 'Mensal' e True no mês atual."""

        # Arrange
        data_compra = date(2026, 5, 20)
        
        # Act
        label, visivel, _ = controle_data_parc_cc(
            data_compra_obj=data_compra,
            dia_fechamento=25,
            dia_vencimento=5,
            total_parcelas=None,  # None indica Assinatura
            controle_mes=self.mes_vigente,
            data_atual=self.data_atual_mock
        )

        # Assert
        self.assertEqual(label, "Mensal")
        self.assertTrue(visivel, "A assinatura deveria estar visível no mês vigente.")


    def test_assinatura_nao_deve_aparecer_no_passado(self):
        """Se o filtro estiver em um mês anterior à assinatura, ela fica oculta."""

        # Arrange
        data_compra = date(2026, 8, 10) # Compra em agosto = Projeção de compra para o futuro
        mes_anterior = 6 # Filtro em Junho = passando para controle_mes o retorno é false, pq a compra está no futuro
        
        # Act
        _, visivel, _ = controle_data_parc_cc(
            data_compra_obj=data_compra,
            dia_fechamento=25,
            dia_vencimento=5,
            total_parcelas=None,
            controle_mes=mes_anterior,
            data_atual=self.data_atual_mock
        )

        # Assert
        self.assertFalse(visivel, "A assinatura não deve aparecer em meses anteriores à contratação.")


    def test_compra_apos_fechamento_pula_fatura(self):
        """Compra no dia 27 com fechamento no dia 25 deve pular para a fatura seguinte."""

        # Arrange
        data_compra = date(2026, 6, 27) # Após o fechamento (25)
        # Se virou a fatura, a primeira cobrança deve ser em Julho (se o vencimento for menor que fechamento)
        # Vamos testar se ela calcula a parcela certa para o controle_mes de Junho (prox_mes)
        
        # Act
        label, visivel, _ = controle_data_parc_cc(
            data_compra_obj=data_compra,
            dia_fechamento=25,
            dia_vencimento=5,
            total_parcelas=3,
            controle_mes=6, # Junho
            data_atual=self.data_atual_mock
        )

        # Assert
        # Como fechamento é 25 e vencimento é 5 (menor), ela aplica o pulo de meses na regra de negócio.
        # Se a lógica indicar que em Junho ela ainda está a vencer ("0/3"):
        self.assertEqual(label, "0/3 (A vencer)")
        self.assertFalse(visivel)


    def test_parcela_quitada_oculta_na_ui(self):
        """Se o filtro do mês for além do total de parcelas, exibe Quitado e oculta."""

        # Arrange
        data_compra = date(2026, 1, 10) # Compra antiga em Janeiro
        
        # Act
        label, visivel, _ = controle_data_parc_cc(
            data_compra_obj=data_compra,
            dia_fechamento=25,
            dia_vencimento=5,
            total_parcelas=2, # Termina em Março
            controle_mes=6,   # Filtro ativo em Junho (Já quitou faz tempo)
            data_atual=self.data_atual_mock
        )

        # Assert
        self.assertEqual(label, "2/2 (Quitado)")
        self.assertFalse(visivel, "Parcelas quitadas não devem impactar visualmente o mês selecionado.")

