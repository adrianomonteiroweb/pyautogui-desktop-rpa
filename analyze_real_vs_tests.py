"""
Script de Análise Real vs Testes
Compara os resultados reais com os resultados dos testes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from easyocr_manager import EasyOCRManager


def analyze_real_vs_tests():
    """
    Analisa as diferenças entre execução real e testes
    """
    print("🔍 ANÁLISE REAL vs TESTES")
    print("=" * 50)
    
    ocr_manager = EasyOCRManager()
    
    print("\n📸 Capturando screenshot atual...")
    screenshot_path = ocr_manager.take_screenshot()
    
    print("\n🧪 Executando detecção otimizada...")
    detected_dates = ocr_manager.extract_data_inicio_dates_optimized(screenshot_path)
    
    print(f"\n📊 RESULTADO ATUAL:")
    print(f"   ✅ Datas detectadas: {len(detected_dates)}")
    
    if detected_dates:
        print("\n📅 DATAS ENCONTRADAS:")
        for i, date_info in enumerate(detected_dates, 1):
            date = date_info['date']
            x, y = date_info['position']
            date_type = date_info['type']
            confidence = date_info['confidence']
            text = date_info['text']
            
            print(f"  {i:2d}. {date} → ({x:.1f}, {y:.1f}) [{date_type}] (conf: {confidence:.2f})")
            print(f"      OCR: '{text}'")
    
    # Datas esperadas pelos testes
    expected_dates = [f"01/{m:02d}/2024" for m in range(1, 12)]  # 01/01 até 01/11
    found_dates = [d['date'] for d in detected_dates]
    
    print(f"\n🎯 COMPARAÇÃO COM TESTES:")
    print(f"   📋 Esperado pelos testes: {len(expected_dates)} datas")
    print(f"   ✅ Encontrado na execução: {len(found_dates)} datas")
    
    missing_dates = [d for d in expected_dates if d not in found_dates]
    extra_dates = [d for d in found_dates if d not in expected_dates]
    
    if missing_dates:
        print(f"\n❌ DATAS FALTANDO (esperadas pelos testes):")
        for date in missing_dates:
            print(f"   - {date}")
    
    if extra_dates:
        print(f"\n➕ DATAS EXTRAS (não esperadas pelos testes):")
        for date in extra_dates:
            print(f"   + {date}")
    
    # Debug completo de todas as datas na tela
    print(f"\n🔍 DEBUG - TODAS AS DATAS DETECTADAS NA TELA:")
    results = ocr_manager.read_text_from_image(screenshot_path)
    
    for bbox, text, confidence in results:
        # Procura por qualquer padrão que pareça uma data
        if any(char.isdigit() for char in text) and ('/' in text or text.count('/') >= 1):
            x_centro, y_centro = ocr_manager._calculate_center_coordinates(bbox)
            print(f"  📅 '{text}' | Pos: ({x_centro:.1f}, {y_centro:.1f}) | Conf: {confidence:.2f}")
    
    print(f"\n📝 POSSÍVEIS CAUSAS DAS DIFERENÇAS:")
    print("   1. Conteúdo da tela mudou desde os testes")
    print("   2. Algumas datas podem estar em formato diferente")
    print("   3. OCR pode estar lendo textos de forma diferente")
    print("   4. Posições das datas podem ter mudado")
    
    return detected_dates


def suggest_improvements():
    """
    Sugere melhorias baseadas na análise
    """
    print(f"\n💡 SUGESTÕES DE MELHORIA:")
    print("   1. Verificar se todas as datas esperadas estão visíveis na tela")
    print("   2. Validar se a coluna 'Data Início' foi encontrada corretamente")
    print("   3. Considerar ajustar padrões de regex se necessário")
    print("   4. Verificar se a tolerância de posição precisa ser ajustada")


if __name__ == "__main__":
    try:
        detected = analyze_real_vs_tests()
        suggest_improvements()
        
        print(f"\n" + "=" * 50)
        print(f"✅ Análise concluída!")
        
    except Exception as e:
        print(f"❌ Erro na análise: {e}")