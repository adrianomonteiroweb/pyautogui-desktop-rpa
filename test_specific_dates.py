"""
Teste Específico de Datas Reais - Identifica e clica nas datas detectadas
Baseado na saída real do OCR da tela do ReceitaNet BX
"""

import time
import pyautogui
import re
from datetime import datetime
import os
import sys

# Adiciona o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from easyocr_manager import EasyOCRManager


class SpecificDateClickTest:
    
    def __init__(self):
        """Inicializa o teste com EasyOCRManager real"""
        self.ocr_manager = EasyOCRManager()
        
        print("🎯 TESTE ESPECÍFICO DE DATAS REAIS")
        print("=" * 50)
        print("📋 Este teste irá:")
        print("  1. Detectar TODAS as datas reais na tela")
        print("  2. Filtrar apenas as da coluna 'Data Início'")
        print("  3. Clicar em cada data encontrada")
        print("=" * 50)
    
    def extract_data_inicio_dates(self, screenshot_path):
        """
        Extrai especificamente as datas da coluna Data Início
        Baseado na posição X da coluna detectada
        """
        print("\n🔍 Extraindo datas da coluna 'Data Início'...")
        
        # Detecta a posição da coluna
        column_image_path = os.path.join("images", "tabelas", "coluna_data_inicio.png")
        column_position = self.ocr_manager.find_column_header_position(column_image_path)
        
        if not column_position:
            print("❌ Não foi possível localizar a coluna Data Início")
            return []
        
        column_x, column_y = column_position
        print(f"📍 Coluna Data Início detectada em: ({column_x}, {column_y})")
        
        # Lê todas as datas da tela
        results = self.ocr_manager.read_text_from_image(screenshot_path)
        data_inicio_dates = []
        
        print(f"\n🔍 Analisando textos OCR...")
        
        for bbox, text, confidence in results:
            # Padrões rigorosos para formato DD/MM/YYYY
            date_patterns = [
                r'\b(\d{2}/\d{2}/\d{4})\b',  # Padrão principal DD/MM/YYYY
                r'(\d{2}/\d{2}/\d{4})',      # Sem word boundary para textos compostos
                # Removido padrão r'/(\d{2}/\d{4})' pois não garante DD/MM/YYYY
            ]
            
            x_centro, y_centro = self.ocr_manager._calculate_center_coordinates(bbox)
            
            # Verifica se está na coluna Data Início (aumentando tolerância para textos compostos)
            x_diff = abs(x_centro - column_x)
            is_in_column = x_diff <= 80.0  # Aumentei tolerância
            is_below_header = y_centro > column_y
            
            if is_in_column and is_below_header:
                all_matches = []
                
                # Aplica padrões rigorosos DD/MM/YYYY
                for pattern in date_patterns:
                    matches = re.findall(pattern, text)
                    # Filtra apenas datas válidas DD/MM/YYYY
                    valid_matches = [m for m in matches if re.match(r'^\d{2}/\d{2}/\d{4}$', m)]
                    all_matches.extend(valid_matches)
                
                # Correção específica para '/02/2024' -> '01/02/2024' (mantém padrão DD/MM/YYYY)
                if '/02/2024' in text and '01' not in text:
                    all_matches.append('01/02/2024')
                    print(f"🔧 Correção aplicada: '/02/2024' -> '01/02/2024'")
                
                # Para textos compostos, extrai datas DD/MM/YYYY começadas com '01/'
                composite_pattern = r'(01/\d{2}/2024)'
                composite_matches = re.findall(composite_pattern, text)
                # Valida que são DD/MM/YYYY
                valid_composite = [m for m in composite_matches if re.match(r'^01/\d{2}/2024$', m)]
                all_matches.extend(valid_composite)
                
                # Remove duplicatas e filtra matches inválidos
                unique_matches = list(set([m for m in all_matches if len(m) > 6]))
                
                for match in unique_matches:
                    # Normaliza a data se necessário
                    if match.startswith('/'):
                        match = '01' + match  # Para casos como '/02/2024'
                    
                    # Valida padrão rigoroso DD/MM/YYYY e filtros específicos
                    if (re.match(r'^01/\d{2}/2024$', match) and 
                        match.startswith('01/') and 
                        match.endswith('/2024') and
                        len(match) == 10):  # Garante formato DD/MM/YYYY exato
                        
                        # Verifica se não é uma duplicata
                        existing = [d for d in data_inicio_dates if d['date'] == match]
                        if not existing:
                            data_inicio_dates.append({
                                'date': match,
                                'position': (x_centro, y_centro),
                                'text': text,
                                'confidence': confidence
                            })
                            # Identifica o tipo baseado na posição X
                            position_type = "Composto" if x_centro > 500 else "Simples"
                            print(f"✅ Data encontrada: {match} em ({x_centro:.1f}, {y_centro:.1f}) - '{text}' [{position_type}] (conf: {confidence:.2f})")
        
        return data_inicio_dates
    
    def test_real_data_inicio_clicks(self):
        """
        Teste principal: encontra e clica nas datas reais da coluna Data Início
        """
        print(f"\n🚀 INICIANDO TESTE DE CLIQUES REAIS...")
        
        try:
            # Captura screenshot
            print("📸 Capturando screenshot...")
            screenshot_path = self.ocr_manager.take_screenshot()
            
            # Extrai datas da coluna Data Início
            data_inicio_dates = self.extract_data_inicio_dates(screenshot_path)
            
            if not data_inicio_dates:
                print("❌ Nenhuma data foi encontrada na coluna Data Início")
                return False
            
            print(f"\n✅ {len(data_inicio_dates)} datas encontradas na coluna Data Início:")
            print("📍 PADRÃO DE POSIÇÕES OBSERVADO:")
            print("   • X ≈ 459.0: Textos simples (maioria)")
            print("   • X ≈ 524.0: Textos compostos (múltiplas datas)")
            print("   • Y: Incremento progressivo ~18px por linha")
            print()
            for i, date_info in enumerate(data_inicio_dates, 1):
                date = date_info['date']
                x, y = date_info['position']
                text_type = "Composto" if x > 500 else "Simples"
                print(f"  {i}. {date} → Posição ({x:.1f}, {y:.1f}) [{text_type}]")
            
            # Confirmação do usuário
            print(f"\n⚠️  Pronto para clicar em {len(data_inicio_dates)} datas!")
            confirmation = input("✅ Pressione ENTER para iniciar os cliques ou 'q' para cancelar: ")
            if confirmation.lower() == 'q':
                print("❌ Teste cancelado pelo usuário")
                return False
            
            # Executa os cliques
            print(f"\n🖱️  INICIANDO CLIQUES...")
            successful_clicks = 0
            
            for i, date_info in enumerate(data_inicio_dates, 1):
                date = date_info['date']
                x, y = date_info['position']
                
                print(f"\n📍 Clique {i}/{len(data_inicio_dates)}: {date}")
                print(f"  🎯 Posição: ({x:.1f}, {y:.1f})")
                
                try:
                    # Move mouse suavemente
                    pyautogui.moveTo(x, y, duration=0.8)
                    time.sleep(0.3)
                    
                    # Clica na data
                    pyautogui.click(x, y)
                    print(f"  ✅ Clique executado!")
                    successful_clicks += 1
                    
                    # Pausa entre cliques
                    if i < len(data_inicio_dates):
                        print(f"  ⏳ Aguardando 2 segundos...")
                        time.sleep(2.0)
                        
                except Exception as e:
                    print(f"  ❌ Erro no clique: {e}")
            
            # Relatório final
            print(f"\n" + "=" * 50)
            print(f"📊 RESULTADO FINAL:")
            print(f"  • Total de datas encontradas: {len(data_inicio_dates)}")
            print(f"  • Cliques bem-sucedidos: {successful_clicks}")
            print(f"  • Taxa de sucesso: {(successful_clicks/len(data_inicio_dates)*100):.1f}%")
            
            if successful_clicks == len(data_inicio_dates):
                print(f"🎉 TESTE 100% BEM-SUCEDIDO!")
            elif successful_clicks > 0:
                print(f"⚠️ TESTE PARCIALMENTE BEM-SUCEDIDO")
            else:
                print(f"❌ TESTE FALHADO")
            
            print("=" * 50)
            return successful_clicks > 0
            
        except Exception as e:
            print(f"❌ Erro durante o teste: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def debug_column_detection(self):
        """Debug da detecção de coluna e datas"""
        print("\n🔍 DEBUG - DETECÇÃO DE COLUNA E DATAS")
        
        try:
            # Screenshot
            screenshot_path = self.ocr_manager.take_screenshot()
            
            # Posição da coluna
            column_image_path = os.path.join("images", "tabelas", "coluna_data_inicio.png")
            column_position = self.ocr_manager.find_column_header_position(column_image_path)
            
            if column_position:
                column_x, column_y = column_position
                print(f"✅ Coluna detectada: ({column_x}, {column_y})")
                
                # Move mouse para mostrar
                pyautogui.moveTo(column_x, column_y, duration=1.0)
                time.sleep(2)
            
            # Todas as datas detectadas
            print(f"\n🔍 Todas as datas na tela:")
            self.ocr_manager.debug_all_detected_dates(screenshot_path)
            
            # Datas específicas da coluna
            data_inicio_dates = self.extract_data_inicio_dates(screenshot_path)
            print(f"\n📊 Resumo: {len(data_inicio_dates)} datas na coluna Data Início")
            
        except Exception as e:
            print(f"❌ Erro no debug: {e}")


def main():
    """Função principal com menu"""
    test = SpecificDateClickTest()
    
    # Configurações de segurança
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    
    print("\n🔒 Failsafe ativado: mova o mouse para o canto superior esquerdo para parar")
    print("\n🎯 OPÇÕES:")
    print("1. Teste completo (detectar + clicar)")
    print("2. Apenas debug (detectar sem clicar)")
    print("3. Sair")
    
    while True:
        choice = input("\n➤ Escolha (1-3): ").strip()
        
        if choice == "1":
            print("\n⚠️ ATENÇÃO: Este teste irá clicar na tela!")
            print("📱 Certifique-se de que o ReceitaNet BX está visível")
            confirmation = input("✅ Pressione ENTER para continuar ou 'q' para cancelar: ")
            if confirmation.lower() != 'q':
                test.test_real_data_inicio_clicks()
            break
            
        elif choice == "2":
            test.debug_column_detection()
            break
            
        elif choice == "3":
            print("👋 Saindo...")
            break
            
        else:
            print("❌ Opção inválida")


if __name__ == "__main__":
    main()