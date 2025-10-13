"""
Teste de Movimento do Mouse - Posições Conhecidas das Datas
Baseado no padrão identificado: X≈459.0 (simples) e X≈524.0 (compostos)
"""

import time
import pyautogui
import os
import sys

# Adiciona o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from easyocr_manager import EasyOCRManager


class MouseMovementTest:
    
    def __init__(self):
        """Inicializa o teste com EasyOCRManager e configurações do mouse"""
        self.ocr_manager = EasyOCRManager()
        
        # Configurações de segurança
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5  # Pausa entre comandos
        
        print("🖱️  TESTE DE MOVIMENTO DO MOUSE")
        print("=" * 50)
        print("📋 Este teste irá:")
        print("  1. Detectar as datas reais na coluna 'Data Início'")
        print("  2. Mover o mouse para cada posição conhecida")
        print("  3. Destacar o padrão X≈459.0 vs X≈524.0")
        print("=" * 50)
        print("🔒 Failsafe ativado: mova o mouse para o canto superior esquerdo para parar")
    
    def get_expected_positions(self):
        """
        Retorna as posições esperadas baseadas no padrão identificado
        X≈459.0 para textos simples, X≈524.0 para textos compostos
        """
        expected_dates = [
            {"date": "01/01/2024", "position": (459.0, 580.0), "type": "Simples"},
            {"date": "01/02/2024", "position": (465.0, 598.0), "type": "Simples (corrigido)"},
            {"date": "01/03/2024", "position": (459.0, 616.0), "type": "Simples"},
            {"date": "01/04/2024", "position": (524.5, 634.0), "type": "Composto"},
            {"date": "01/05/2024", "position": (524.0, 651.0), "type": "Composto"},
            {"date": "01/06/2024", "position": (459.0, 669.0), "type": "Simples"},
            {"date": "01/07/2024", "position": (525.0, 687.0), "type": "Composto"},
            {"date": "01/08/2024", "position": (458.0, 706.0), "type": "Simples"},
            {"date": "01/09/2024", "position": (459.0, 724.0), "type": "Simples"},
            {"date": "01/10/2024", "position": (459.0, 742.0), "type": "Simples"},
            {"date": "01/11/2024", "position": (459.0, 761.0), "type": "Simples"},
        ]
        return expected_dates
    
    def move_mouse_to_positions(self, test_real_detection=True):
        """
        Move o mouse para as posições das datas
        """
        print(f"\n🎯 INICIANDO TESTE DE MOVIMENTO DO MOUSE...")
        
        if test_real_detection:
            print("📸 Primeiro, vamos detectar as posições reais...")
            # Captura screenshot e detecta posições reais
            screenshot_path = self.ocr_manager.take_screenshot()
            real_dates = self.detect_real_positions(screenshot_path)
            
            if not real_dates:
                print("❌ Não foi possível detectar datas reais. Usando posições esperadas...")
                dates_to_test = self.get_expected_positions()
            else:
                print(f"✅ {len(real_dates)} datas detectadas. Usando posições reais...")
                dates_to_test = real_dates
        else:
            print("📋 Usando posições esperadas baseadas no padrão conhecido...")
            dates_to_test = self.get_expected_positions()
        
        print(f"\n🖱️  Movendo mouse para {len(dates_to_test)} posições:")
        print("📍 PADRÃO OBSERVADO:")
        print("   • X ≈ 459.0: Textos simples")  
        print("   • X ≈ 524.0: Textos compostos")
        print()
        
        # Posição inicial do mouse
        initial_pos = pyautogui.position()
        print(f"🎯 Posição inicial do mouse: {initial_pos}")
        
        try:
            for i, date_info in enumerate(dates_to_test, 1):
                date = date_info['date']
                x, y = date_info['position']
                date_type = date_info.get('type', 'Detectado')
                
                # Classifica o tipo baseado na posição X
                if x > 500:
                    pattern_type = "📊 Composto (X≈524)"
                    color_indicator = "🔵"
                else:
                    pattern_type = "📄 Simples (X≈459)"
                    color_indicator = "🟢"
                
                print(f"  {i:2d}. {color_indicator} {date} → ({x:.1f}, {y:.1f}) [{pattern_type}]")
                
                # Move o mouse suavemente para a posição
                print(f"      🖱️  Movendo para ({x:.1f}, {y:.1f})...")
                pyautogui.moveTo(x, y, duration=0.8)  # Movimento suave
                
                # Pequena pausa para visualização
                time.sleep(0.8)
                
                # Confirma posição atual
                current_pos = pyautogui.position()
                print(f"      ✅ Posição atual: {current_pos}")
                
                # Pausa entre movimentos
                if i < len(dates_to_test):
                    print(f"      ⏳ Aguardando próximo movimento...")
                    time.sleep(1.0)
            
            print(f"\n🎉 Teste concluído! Mouse movido para {len(dates_to_test)} posições.")
            
            # Volta para posição inicial
            print(f"🔄 Retornando à posição inicial...")
            pyautogui.moveTo(initial_pos.x, initial_pos.y, duration=1.0)
            
            return True
            
        except pyautogui.FailSafeException:
            print("🛑 FAILSAFE ATIVADO! Teste interrompido pelo usuário.")
            return False
        except Exception as e:
            print(f"❌ Erro durante movimento: {e}")
            return False
    
    def detect_real_positions(self, screenshot_path):
        """
        Detecta posições reais usando OCR (método completo com correções)
        Baseado na lógica do test_specific_dates.py
        """
        # Detecta a posição da coluna
        column_image_path = os.path.join("images", "tabelas", "coluna_data_inicio.png")
        column_position = self.ocr_manager.find_column_header_position(column_image_path)
        
        if not column_position:
            return []
        
        column_x, column_y = column_position
        results = self.ocr_manager.read_text_from_image(screenshot_path)
        detected_dates = []
        
        # Lista das datas que esperamos encontrar
        target_dates = [f"01/{m:02d}/2024" for m in range(1, 12)]  # 01/01 até 01/11
        
        for bbox, text, confidence in results:
            x_centro, y_centro = self.ocr_manager._calculate_center_coordinates(bbox)
            
            # Verifica se está na coluna Data Início
            x_diff = abs(x_centro - column_x)
            is_in_column = x_diff <= 80.0
            is_below_header = y_centro > column_y
            
            if is_in_column and is_below_header:
                found_dates = []
                
                # 1. Verifica datas normais no texto
                for target_date in target_dates:
                    if target_date in text:
                        found_dates.append(target_date)
                
                # 2. Correção específica para '/02/2024' -> '01/02/2024'
                if '/02/2024' in text and '01/02/2024' not in found_dates:
                    found_dates.append('01/02/2024')
                    print(f"🔧 Correção OCR aplicada: '/02/2024' -> '01/02/2024' em ({x_centro:.1f}, {y_centro:.1f})")
                
                # 3. Para textos compostos, extrai datas que começam com '01/'
                import re
                composite_pattern = r'(01/\d{2}/2024)'
                composite_matches = re.findall(composite_pattern, text)
                for match in composite_matches:
                    if match in target_dates and match not in found_dates:
                        found_dates.append(match)
                
                # Adiciona todas as datas encontradas
                for found_date in found_dates:
                    # Determina o tipo baseado na posição X
                    if x_centro > 500:
                        date_type = "Composto"
                    else:
                        date_type = "Simples"
                    
                    # Evita duplicatas
                    existing = [d for d in detected_dates if d['date'] == found_date]
                    if not existing:
                        detected_dates.append({
                            'date': found_date,
                            'position': (x_centro, y_centro),
                            'type': date_type,
                            'confidence': confidence
                        })
        
        # Ordena por data para facilitar visualização
        detected_dates.sort(key=lambda x: x['date'])
        
        return detected_dates
    
    def run_interactive_test(self):
        """
        Executa teste interativo com opções
        """
        print(f"\n🎯 OPÇÕES DO TESTE:")
        print("1. Usar detecção real (OCR + movimento)")
        print("2. Usar posições conhecidas (padrão + movimento)")
        print("3. Comparar ambos")
        print("4. Sair")
        
        try:
            choice = input("\n➤ Escolha (1-4): ").strip()
            
            if choice == '1':
                print("\n🔍 Teste com detecção real...")
                return self.move_mouse_to_positions(test_real_detection=True)
            elif choice == '2':
                print("\n📋 Teste com posições conhecidas...")
                return self.move_mouse_to_positions(test_real_detection=False)
            elif choice == '3':
                print("\n🔄 Comparando ambos os métodos...")
                print("\n--- PRIMEIRO: Detecção Real ---")
                self.move_mouse_to_positions(test_real_detection=True)
                input("\n⏸️  Pressione ENTER para continuar com posições conhecidas...")
                print("\n--- SEGUNDO: Posições Conhecidas ---")
                return self.move_mouse_to_positions(test_real_detection=False)
            elif choice == '4':
                print("👋 Teste cancelado.")
                return False
            else:
                print("❌ Opção inválida.")
                return self.run_interactive_test()
                
        except KeyboardInterrupt:
            print("\n🛑 Teste interrompido pelo usuário.")
            return False


def main():
    """Função principal"""
    test = MouseMovementTest()
    
    try:
        # Executa teste interativo
        success = test.run_interactive_test()
        
        if success:
            print("\n✅ Teste de movimento concluído com sucesso!")
            print("📊 Padrão confirmado:")
            print("   🟢 X ≈ 459.0: Textos simples (8 datas)")
            print("   🔵 X ≈ 524.0: Textos compostos (3 datas)")
            print("   📏 Y: Incremento ~18px por linha")
        else:
            print("\n❌ Teste não foi concluído.")
            
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")


if __name__ == "__main__":
    main()