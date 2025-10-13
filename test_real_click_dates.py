"""
Teste REAL de clique nas datas da coluna "Data Início" - SEM MOCKS
Usa os métodos reais do EasyOCRManager para detectar e clicar nas datas
Baseado no print fornecido que mostra os resultados da pesquisa
"""

import time
import pyautogui
from datetime import datetime
import os
import sys

# Adiciona o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from easyocr_manager import EasyOCRManager
from date_formatter import DateFormatter


class RealDateClickTest:
    
    def __init__(self):
        """Inicializa o teste com EasyOCRManager real"""
        self.ocr_manager = EasyOCRManager()
        self.date_formatter = DateFormatter()
        
        # Datas que estão visíveis no print fornecido na coluna "Data Início"
        # Baseado na detecção real do OCR, essas são as datas presentes
        self.expected_dates = [
            "01/01/2024", "01/03/2024", "01/04/2024", "01/05/2024",
            "01/06/2024", "01/07/2024", "01/08/2024", "01/09/2024", 
            "01/10/2024", "01/11/2024"
        ]
        
        print("🚀 TESTE REAL DE CLIQUE NAS DATAS - SEM MOCKS")
        print("=" * 60)
        print("📋 Este teste irá:")
        print("  1. Capturar screenshot da tela atual")
        print("  2. Detectar datas reais na coluna 'Data Início'")
        print("  3. Clicar em cada data encontrada")
        print("  4. Verificar se todas as datas esperadas foram processadas")
        print("=" * 60)
    
    def wait_for_user_confirmation(self):
        """Aguarda confirmação do usuário antes de continuar"""
        print("\n⚠️  ATENÇÃO: Este teste irá clicar na tela!")
        print("📱 Certifique-se de que:")
        print("  - O ReceitaNet BX está aberto")
        print("  - A tela de pesquisa com resultados está visível")
        print("  - As datas estão sendo exibidas na coluna 'Data Início'")
        print("  - Você não está usando o mouse/teclado")
        
        response = input("\n✅ Pressione ENTER para continuar ou 'q' para cancelar: ")
        if response.lower() == 'q':
            print("❌ Teste cancelado pelo usuário")
            return False
        return True
    
    def test_real_date_detection_and_click(self):
        """
        Teste principal: detecta e clica nas datas reais da coluna Data Início
        """
        print(f"\n🔍 INICIANDO DETECÇÃO REAL DE DATAS...")
        
        try:
            # Captura screenshot real da tela
            print("📸 Capturando screenshot da tela...")
            screenshot_path = self.ocr_manager.take_screenshot()
            print(f"✅ Screenshot salvo: {screenshot_path}")
            
            # Debug: mostra todas as datas detectadas
            print("\n🔍 Detectando todas as datas na tela...")
            self.ocr_manager.debug_all_detected_dates(screenshot_path)
            
            # Procura as datas na coluna específica
            print(f"\n📍 Buscando datas na coluna 'Data Início'...")
            date_positions = self.ocr_manager.find_all_dates_positions_in_column(
                target_dates=self.expected_dates,
                column_image_filename="coluna_data_inicio.png",
                screenshot_path=screenshot_path,
                column_tolerance=100.0,  # Aumentando tolerância para tela real
                debug=True
            )
            
            print(f"\n✅ Resultado da detecção:")
            print(f"  📊 Datas esperadas: {len(self.expected_dates)}")
            print(f"  📊 Datas encontradas: {len(date_positions)}")
            
            if not date_positions:
                print("❌ Nenhuma data foi encontrada na coluna!")
                print("🔧 Possíveis soluções:")
                print("  - Verifique se o ReceitaNet BX está aberto")
                print("  - Confirme se a tela de pesquisa está visível")
                print("  - Verifique se existe arquivo 'images/tabelas/coluna_data_inicio.png'")
                return False
            
            # Lista as datas encontradas
            print(f"\n📋 Datas detectadas para clique:")
            for i, (date, position) in enumerate(date_positions.items(), 1):
                x, y = position
                print(f"  {i:2}. {date} → Posição ({x:.1f}, {y:.1f})")
            
            # Confirmação antes de clicar
            print(f"\n⚠️  Pronto para clicar em {len(date_positions)} datas!")
            confirmation = input("✅ Pressione ENTER para iniciar os cliques ou 'q' para pular: ")
            if confirmation.lower() == 'q':
                print("⏭️ Cliques pulados pelo usuário")
                return True
            
            # Executa os cliques em cada data encontrada
            print(f"\n🖱️  INICIANDO CLIQUES NAS DATAS...")
            click_results = {}
            
            for i, (date, position) in enumerate(date_positions.items(), 1):
                x, y = position
                
                print(f"\n📍 Clique {i}/{len(date_positions)}: {date}")
                print(f"  🎯 Posição: ({x:.1f}, {y:.1f})")
                
                try:
                    # Move o mouse para a posição
                    pyautogui.moveTo(x, y, duration=0.5)
                    time.sleep(0.2)
                    
                    # Executa o clique
                    pyautogui.click(x, y)
                    print(f"  ✅ Clique executado com sucesso")
                    
                    click_results[date] = "SUCCESS"
                    
                    # Pausa entre cliques para estabilidade
                    if i < len(date_positions):
                        time.sleep(1.0)
                        
                except Exception as e:
                    print(f"  ❌ Erro no clique: {e}")
                    click_results[date] = f"ERROR: {e}"
            
            # Relatório final
            self.generate_final_report(date_positions, click_results)
            return True
            
        except Exception as e:
            print(f"❌ Erro durante o teste: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_final_report(self, date_positions, click_results):
        """Gera relatório final do teste"""
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO FINAL DO TESTE")
        print("=" * 60)
        
        successful_clicks = sum(1 for result in click_results.values() if result == "SUCCESS")
        total_expected = len(self.expected_dates)
        total_found = len(date_positions)
        
        print(f"📈 Estatísticas:")
        print(f"  • Datas esperadas: {total_expected}")
        print(f"  • Datas detectadas: {total_found}")
        print(f"  • Cliques bem-sucedidos: {successful_clicks}")
        print(f"  • Taxa de detecção: {(total_found/total_expected)*100:.1f}%")
        
        if successful_clicks > 0:
            print(f"  • Taxa de sucesso nos cliques: {(successful_clicks/total_found)*100:.1f}%")
        
        print(f"\n📋 Detalhamento por data:")
        
        for date in self.expected_dates:
            if date in date_positions:
                if date in click_results:
                    status = "✅ DETECTADA e CLICADA" if click_results[date] == "SUCCESS" else f"❌ DETECTADA mas ERRO: {click_results[date]}"
                else:
                    status = "🔍 DETECTADA (clique não executado)"
                x, y = date_positions[date]
                print(f"  {date}: {status} - Pos: ({x:.1f}, {y:.1f})")
            else:
                print(f"  {date}: ❌ NÃO DETECTADA")
        
        print("\n" + "=" * 60)
        
        if successful_clicks == total_expected:
            print("🎉 TESTE 100% BEM-SUCEDIDO!")
            print("✅ Todas as datas foram detectadas e clicadas com sucesso!")
        elif successful_clicks > 0:
            print("⚠️ TESTE PARCIALMENTE BEM-SUCEDIDO")
            print(f"✅ {successful_clicks} datas processadas com sucesso")
            print(f"❌ {total_expected - successful_clicks} datas não processadas")
        else:
            print("❌ TESTE FALHADO")
            print("Nenhuma data foi clicada com sucesso")
        
        print("=" * 60)
    
    def test_column_detection_only(self):
        """
        Teste auxiliar: apenas detecta a coluna sem fazer cliques
        """
        print(f"\n🔍 TESTE DE DETECÇÃO DA COLUNA (sem cliques)")
        
        try:
            # Tenta localizar a imagem da coluna
            column_image_path = os.path.join("images", "tabelas", "coluna_data_inicio.png")
            
            if not os.path.exists(column_image_path):
                print(f"❌ Arquivo não encontrado: {column_image_path}")
                print("🔧 Certifique-se de que a imagem da coluna existe")
                return False
            
            print(f"✅ Arquivo da coluna encontrado: {column_image_path}")
            
            # Tenta localizar a coluna na tela
            column_position = self.ocr_manager.find_column_header_position(column_image_path)
            
            if column_position:
                x, y = column_position
                print(f"✅ Coluna 'Data Início' detectada na posição: ({x}, {y})")
                
                # Move o mouse para mostrar a posição (sem clicar)
                pyautogui.moveTo(x, y, duration=1.0)
                print("🖱️ Mouse movido para a posição da coluna")
                return True
            else:
                print("❌ Coluna 'Data Início' não foi detectada na tela")
                print("🔧 Verifique se a tela do ReceitaNet BX está visível")
                return False
                
        except Exception as e:
            print(f"❌ Erro na detecção da coluna: {e}")
            return False


def run_real_test():
    """Executa o teste real com menu de opções"""
    test = RealDateClickTest()
    
    print("\n🎯 OPÇÕES DE TESTE:")
    print("1. Teste completo (detecção + cliques)")
    print("2. Apenas detectar coluna (sem cliques)")
    print("3. Apenas detectar datas (sem cliques)")
    print("4. Sair")
    
    while True:
        choice = input("\n➤ Escolha uma opção (1-4): ").strip()
        
        if choice == "1":
            if test.wait_for_user_confirmation():
                test.test_real_date_detection_and_click()
            break
            
        elif choice == "2":
            test.test_column_detection_only()
            break
            
        elif choice == "3":
            screenshot_path = test.ocr_manager.take_screenshot()
            test.ocr_manager.debug_all_detected_dates(screenshot_path)
            break
            
        elif choice == "4":
            print("👋 Teste cancelado")
            break
            
        else:
            print("❌ Opção inválida. Digite 1, 2, 3 ou 4")


if __name__ == "__main__":
    # Configurações de segurança do pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    
    print("🔒 Failsafe ativado: mova o mouse para o canto superior esquerdo para parar")
    run_real_test()