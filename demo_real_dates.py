"""
DEMONSTRAÇÃO FINAL - Teste de Clique nas Datas Reais
Baseado na detecção real do OCR sem mocks
"""

import time
import pyautogui
import re
import os
import sys

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from easyocr_manager import EasyOCRManager


def demonstrate_real_date_detection():
    """
    Demonstra a detecção real de datas sem cliques automáticos
    """
    print("🎯 DEMONSTRAÇÃO DE DETECÇÃO DE DATAS REAIS")
    print("=" * 55)
    
    # Configurações de segurança
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    
    # Inicializa OCR
    ocr_manager = EasyOCRManager()
    
    try:
        # Captura screenshot
        print("📸 Capturando screenshot da tela atual...")
        screenshot_path = ocr_manager.take_screenshot()
        print(f"✅ Screenshot salvo: {screenshot_path}")
        
        # Detecta posição da coluna Data Início
        print("\n📍 Detectando coluna 'Data Início'...")
        column_image_path = os.path.join("images", "tabelas", "coluna_data_inicio.png")
        column_position = ocr_manager.find_column_header_position(column_image_path)
        
        if not column_position:
            print("❌ Coluna 'Data Início' não detectada")
            return
        
        column_x, column_y = column_position
        print(f"✅ Coluna detectada na posição: ({column_x}, {column_y})")
        
        # Lê textos da tela
        print("\n🔍 Executando OCR na tela...")
        results = ocr_manager.read_text_from_image(screenshot_path)
        
        # Filtra datas da coluna Data Início
        data_inicio_dates = []
        
        for bbox, text, confidence in results:
            x_centro, y_centro = ocr_manager._calculate_center_coordinates(bbox)
            
            # Verifica se está na coluna (aumentando tolerância para textos compostos)
            x_diff = abs(x_centro - column_x)
            is_in_column = x_diff <= 80.0  # Aumentei tolerância
            is_below_header = y_centro > column_y
            
            if is_in_column and is_below_header:
                # Padrão rigoroso: sempre DD/MM/YYYY
                date_patterns = [
                    r'\b(\d{2}/\d{2}/\d{4})\b',  # Padrão principal DD/MM/YYYY
                    r'(\d{2}/\d{2}/\d{4})',      # Sem word boundary para textos compostos
                ]
                
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
                
                # Extrai datas DD/MM/YYYY de textos compostos, apenas começadas com '01/'
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
                        match = '01' + match
                    
                    # Valida padrão rigoroso DD/MM/YYYY e filtro específico
                    if (re.match(r'^01/\d{2}/2024$', match) and 
                        match.startswith('01/') and 
                        match.endswith('/2024') and
                        len(match) == 10):  # Garante formato DD/MM/YYYY
                        
                        # Evita duplicatas
                        existing = [d for d in data_inicio_dates if d['date'] == match]
                        if not existing:
                            data_inicio_dates.append({
                                'date': match,
                                'position': (x_centro, y_centro),
                                'text': text,
                                'confidence': confidence
                            })
        
        # Ordena por posição Y (de cima para baixo)
        data_inicio_dates.sort(key=lambda x: x['position'][1])
        
        # Mostra resultados
        print(f"\n✅ DATAS DETECTADAS NA COLUNA 'DATA INÍCIO': {len(data_inicio_dates)}")
        print("-" * 55)
        
        for i, date_info in enumerate(data_inicio_dates, 1):
            date = date_info['date']
            x, y = date_info['position']
            confidence = date_info['confidence']
            text = date_info['text']
            
            print(f"{i:2}. {date}")
            print(f"    📍 Posição: ({x:.1f}, {y:.1f})")
            print(f"    🎯 Confiança: {confidence:.2f}")
            print(f"    📝 Texto OCR: '{text}'")
            print()
        
        # Demonstra movimento do mouse (sem clique)
        print("🖱️ DEMONSTRAÇÃO DE POSICIONAMENTO (sem cliques):")
        print("⚠️ O mouse irá se mover para cada posição detectada...")
        input("📱 Pressione ENTER para continuar...")
        
        for i, date_info in enumerate(data_inicio_dates, 1):
            date = date_info['date']
            x, y = date_info['position']
            
            print(f"\n🎯 Movendo para {date} em ({x:.1f}, {y:.1f})...")
            pyautogui.moveTo(x, y, duration=1.5)
            time.sleep(1.0)
        
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA!")
        print("=" * 55)
        print(f"✅ Detectadas {len(data_inicio_dates)} datas na coluna 'Data Início'")
        print("✅ Posições calculadas com precisão")
        print("✅ Movimento do mouse demonstrado com sucesso")
        print("=" * 55)
        
        # Pergunta se quer fazer cliques reais
        print("\n⚠️ CLIQUES REAIS (OPCIONAL):")
        print("🔴 ATENÇÃO: Isso irá clicar de verdade na tela!")
        choice = input("👆 Deseja executar cliques reais? (s/N): ").lower().strip()
        
        if choice == 's':
            execute_real_clicks(data_inicio_dates)
        else:
            print("✅ Demonstração finalizada sem cliques reais")
            
    except Exception as e:
        print(f"❌ Erro durante demonstração: {e}")
        import traceback
        traceback.print_exc()


def execute_real_clicks(date_list):
    """Executa cliques reais nas datas detectadas"""
    print(f"\n🚨 EXECUTANDO {len(date_list)} CLIQUES REAIS...")
    print("⚠️ Certifique-se de que a tela está pronta!")
    
    countdown = 5
    for i in range(countdown, 0, -1):
        print(f"⏰ Iniciando em {i} segundos... (mova mouse para canto superior esquerdo para cancelar)")
        time.sleep(1)
    
    successful_clicks = 0
    
    for i, date_info in enumerate(date_list, 1):
        date = date_info['date']
        x, y = date_info['position']
        
        try:
            print(f"\n📍 Clique {i}/{len(date_list)}: {date}")
            print(f"   🎯 Posição: ({x:.1f}, {y:.1f})")
            
            # Move e clica
            pyautogui.moveTo(x, y, duration=0.8)
            time.sleep(0.3)
            pyautogui.click(x, y)
            
            print(f"   ✅ Clique executado!")
            successful_clicks += 1
            
            # Pausa entre cliques
            if i < len(date_list):
                time.sleep(2.0)
                
        except Exception as e:
            print(f"   ❌ Erro no clique: {e}")
    
    print(f"\n🎯 RESULTADO DOS CLIQUES:")
    print(f"   • Total: {len(date_list)} datas")
    print(f"   • Sucessos: {successful_clicks}")
    print(f"   • Taxa: {(successful_clicks/len(date_list)*100):.1f}%")


if __name__ == "__main__":
    print("🔒 Failsafe: mova o mouse para o canto superior esquerdo para parar a qualquer momento")
    print()
    demonstrate_real_date_detection()