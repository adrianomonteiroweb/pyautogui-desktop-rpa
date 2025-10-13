"""
Teste para verificar a busca de datas na coluna "Data Início"
Deve encontrar datas de 01/01/2024 até 01/11/2024 e NÃO encontrar 01/12/2024
Baseado no print fornecido que mostra os resultados da pesquisa
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
import os
import sys

# Adiciona o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from easyocr_manager import EasyOCRManager
from date_formatter import DateFormatter


class TestDateSearch(unittest.TestCase):
    
    def setUp(self):
        """Setup executado antes de cada teste"""
        self.ocr_manager = EasyOCRManager()
        self.date_formatter = DateFormatter()
        
        # Datas que DEVEM ser encontradas (01/01/2024 até 01/11/2024)
        self.expected_dates = [
            "01/01/2024", "01/02/2024", "01/03/2024", "01/04/2024",
            "01/05/2024", "01/06/2024", "01/07/2024", "01/08/2024", 
            "01/09/2024", "01/10/2024", "01/11/2024"
        ]
        
        # Data que NÃO DEVE ser encontrada
        self.missing_date = "01/12/2024"
        
        # Simula os dados encontrados no print anexado
        # Baseado na coluna "Data Início" visível na imagem
        self.mock_ocr_results = [
            # Formato: (bbox, texto, confidence)
            # Simulando as datas visíveis no print
            ([[100, 417], [200, 417], [200, 432], [100, 432]], "01/01/2024 00:00:00", 0.95),
            ([[100, 432], [200, 432], [200, 447], [100, 447]], "01/02/2024 00:00:00", 0.95),
            ([[100, 447], [200, 447], [200, 462], [100, 462]], "01/03/2024 00:00:00", 0.95),
            ([[100, 462], [200, 462], [200, 477], [100, 477]], "01/04/2024 00:00:00", 0.95),
            ([[100, 477], [200, 477], [200, 492], [100, 492]], "01/05/2024 00:00:00", 0.95),
            ([[100, 492], [200, 492], [200, 507], [100, 507]], "01/06/2024 00:00:00", 0.95),
            ([[100, 507], [200, 507], [200, 522], [100, 522]], "01/07/2024 00:00:00", 0.95),
            ([[100, 522], [200, 522], [200, 537], [100, 537]], "01/08/2024 00:00:00", 0.95),
            ([[100, 537], [200, 537], [200, 552], [100, 552]], "01/09/2024 00:00:00", 0.95),
            ([[100, 552], [200, 552], [200, 567], [100, 567]], "01/10/2024 00:00:00", 0.95),
            ([[100, 567], [200, 567], [200, 582], [100, 582]], "01/11/2024 00:00:00", 0.95),
            # Outras colunas que podem aparecer mas não são da coluna "Data Início"
            ([[300, 417], [400, 417], [400, 432], [300, 432]], "22/02/2024 00:00:00", 0.95),  # Data Fim
            ([[300, 432], [400, 432], [400, 447], [300, 447]], "29/02/2024 00:00:00", 0.95),  # Data Fim
        ]

    @patch.object(EasyOCRManager, 'take_screenshot')
    @patch.object(EasyOCRManager, 'read_text_from_image')
    @patch.object(EasyOCRManager, 'find_column_header_position')
    def test_find_expected_dates_in_column(self, mock_find_column, mock_read_text, mock_screenshot):
        """
        Teste principal: deve encontrar todas as datas de 01/01/2024 até 01/11/2024
        """
        # Mock do screenshot
        mock_screenshot.return_value = "fake_screenshot.png"
        
        # Mock da posição da coluna "Data Início" (x=150, y=400 baseado no layout)
        mock_find_column.return_value = (150, 400)
        
        # Mock dos resultados do OCR
        mock_read_text.return_value = self.mock_ocr_results
        
        # Executa a busca
        date_positions = self.ocr_manager.find_all_dates_positions_in_column(
            target_dates=self.expected_dates,
            column_image_filename="coluna_data_inicio.png",
            column_tolerance=80.0,
            debug=True
        )
        
        # Verifica se todas as datas esperadas foram encontradas
        print(f"\n🔍 Testando busca de {len(self.expected_dates)} datas...")
        
        for expected_date in self.expected_dates:
            self.assertIn(expected_date, date_positions, 
                         f"Data {expected_date} deveria ter sido encontrada na coluna 'Data Início'")
            
            x, y = date_positions[expected_date]
            print(f"✅ Data {expected_date} encontrada em posição ({x}, {y})")
        
        # Verifica que encontrou exatamente o número esperado de datas
        self.assertEqual(len(date_positions), len(self.expected_dates),
                        f"Deveria ter encontrado {len(self.expected_dates)} datas, mas encontrou {len(date_positions)}")
        
        print(f"🎉 Sucesso! Encontradas todas as {len(self.expected_dates)} datas esperadas")

    @patch.object(EasyOCRManager, 'take_screenshot')
    @patch.object(EasyOCRManager, 'read_text_from_image')
    @patch.object(EasyOCRManager, 'find_column_header_position')
    def test_missing_date_not_found(self, mock_find_column, mock_read_text, mock_screenshot):
        """
        Teste para verificar que a data 01/12/2024 NÃO é encontrada
        """
        # Mock do screenshot
        mock_screenshot.return_value = "fake_screenshot.png"
        
        # Mock da posição da coluna
        mock_find_column.return_value = (150, 400)
        
        # Mock dos resultados do OCR (sem a data 01/12/2024)
        mock_read_text.return_value = self.mock_ocr_results
        
        # Executa a busca apenas para a data que NÃO deve ser encontrada
        date_positions = self.ocr_manager.find_all_dates_positions_in_column(
            target_dates=[self.missing_date],
            column_image_filename="coluna_data_inicio.png",
            column_tolerance=80.0,
            debug=True
        )
        
        # Verifica que a data NÃO foi encontrada
        self.assertNotIn(self.missing_date, date_positions,
                        f"Data {self.missing_date} NÃO deveria ter sido encontrada")
        
        self.assertEqual(len(date_positions), 0,
                        f"Não deveria ter encontrado nenhuma data, mas encontrou {len(date_positions)}")
        
        print(f"✅ Correto! Data {self.missing_date} não foi encontrada (como esperado)")

    @patch.object(EasyOCRManager, 'take_screenshot')
    @patch.object(EasyOCRManager, 'read_text_from_image')
    @patch.object(EasyOCRManager, 'find_column_header_position')
    def test_complete_scenario(self, mock_find_column, mock_read_text, mock_screenshot):
        """
        Teste do cenário completo: busca todas as datas esperadas + a que não deve existir
        """
        # Mock setup
        mock_screenshot.return_value = "fake_screenshot.png"
        mock_find_column.return_value = (150, 400)
        mock_read_text.return_value = self.mock_ocr_results
        
        # Lista completa incluindo a data que NÃO deve ser encontrada
        all_test_dates = self.expected_dates + [self.missing_date]
        
        # Executa a busca
        date_positions = self.ocr_manager.find_all_dates_positions_in_column(
            target_dates=all_test_dates,
            column_image_filename="coluna_data_inicio.png",
            column_tolerance=80.0,
            debug=True
        )
        
        print(f"\n🔍 Teste completo: buscando {len(all_test_dates)} datas...")
        print(f"📊 Resultado: {len(date_positions)} datas encontradas")
        
        # Verifica que todas as datas esperadas foram encontradas
        found_expected = 0
        for expected_date in self.expected_dates:
            if expected_date in date_positions:
                found_expected += 1
                x, y = date_positions[expected_date]
                print(f"✅ {expected_date} - ENCONTRADA em ({x}, {y})")
            else:
                print(f"❌ {expected_date} - NÃO encontrada (ERRO!)")
        
        # Verifica que a data não esperada NÃO foi encontrada
        if self.missing_date not in date_positions:
            print(f"✅ {self.missing_date} - NÃO encontrada (CORRETO)")
        else:
            print(f"❌ {self.missing_date} - ENCONTRADA (ERRO!)")
        
        # Assertiva final
        self.assertEqual(found_expected, len(self.expected_dates),
                        f"Deveria ter encontrado {len(self.expected_dates)} datas, mas encontrou {found_expected}")
        
        self.assertNotIn(self.missing_date, date_positions,
                        f"Data {self.missing_date} não deveria ter sido encontrada")
        
        print(f"\n🎉 TESTE COMPLETO PASSOU!")
        print(f"✅ Encontradas: {len(self.expected_dates)} datas (01/01/2024 a 01/11/2024)")
        print(f"✅ Não encontrada: 1 data (01/12/2024)")

    def test_date_range_generation(self):
        """
        Teste auxiliar para verificar se a geração do range de datas está correta
        """
        # Testa se conseguimos gerar o range correto de datas
        start_date = date(2024, 1, 1)
        end_date = date(2024, 11, 1)
        
        generated_dates = []
        current_date = start_date
        
        while current_date <= end_date:
            formatted_date = current_date.strftime("%d/%m/%Y")
            generated_dates.append(formatted_date)
            # Próximo mês
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        # Verifica se gerou corretamente
        self.assertEqual(generated_dates, self.expected_dates,
                        "Geração do range de datas não está correta")
        
        print(f"✅ Range de datas gerado corretamente: {len(generated_dates)} datas")
        for i, date_str in enumerate(generated_dates, 1):
            print(f"  {i:2}. {date_str}")


def run_tests():
    """Executa todos os testes com relatório detalhado"""
    print("=" * 80)
    print("🧪 INICIANDO TESTES DE BUSCA DE DATAS NA COLUNA 'Data Início'")
    print("=" * 80)
    print("📋 Objetivo: Verificar se o sistema encontra datas de 01/01/2024 a 01/11/2024")
    print("📋 E NÃO encontra a data 01/12/2024")
    print("📋 Baseado no print da tela do sistema ReceitaNet BX")
    print("=" * 80)
    
    # Cria a suite de testes
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDateSearch)
    
    # Executa os testes com verbose
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    print("\n" + "=" * 80)
    if result.wasSuccessful():
        print("🎉 TODOS OS TESTES PASSARAM! ✅")
        print(f"✅ Testes executados: {result.testsRun}")
        print(f"✅ Sucessos: {result.testsRun - len(result.failures) - len(result.errors)}")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print(f"📊 Testes executados: {result.testsRun}")
        print(f"❌ Falhas: {len(result.failures)}")
        print(f"❌ Erros: {len(result.errors)}")
        
        if result.failures:
            print("\n🔍 DETALHES DAS FALHAS:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback}")
                
        if result.errors:
            print("\n🔍 DETALHES DOS ERROS:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback}")
    
    print("=" * 80)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)