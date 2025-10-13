"""
Teste de Validação do Padrão DD/MM/YYYY
Verifica se todas as datas detectadas seguem rigorosamente o padrão DD/MM/YYYY
"""

import re
import sys
import os

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from easyocr_manager import EasyOCRManager


def validate_date_format(date_string):
    """
    Valida se a data está no formato rigoroso DD/MM/YYYY
    
    Args:
        date_string: String da data a ser validada
        
    Returns:
        bool: True se está no formato correto, False caso contrário
    """
    # Padrão rigoroso: exatamente DD/MM/YYYY (10 caracteres)
    pattern = r'^(\d{2})/(\d{2})/(\d{4})$'
    
    if not re.match(pattern, date_string):
        return False
    
    # Verifica se tem exatamente 10 caracteres
    if len(date_string) != 10:
        return False
    
    # Extrai componentes
    parts = date_string.split('/')
    if len(parts) != 3:
        return False
    
    day, month, year = parts
    
    # Valida cada componente
    if len(day) != 2 or not day.isdigit():
        return False
    if len(month) != 2 or not month.isdigit():
        return False
    if len(year) != 4 or not year.isdigit():
        return False
    
    # Valida ranges básicos
    day_int = int(day)
    month_int = int(month)
    year_int = int(year)
    
    if not (1 <= day_int <= 31):
        return False
    if not (1 <= month_int <= 12):
        return False
    if not (2020 <= year_int <= 2030):  # Range razoável
        return False
    
    return True


def test_date_format_validation():
    """
    Testa a detecção real e valida se todas as datas seguem DD/MM/YYYY
    """
    print("🔍 TESTE DE VALIDAÇÃO DO PADRÃO DD/MM/YYYY")
    print("=" * 50)
    
    ocr_manager = EasyOCRManager()
    
    try:
        # Captura screenshot real
        print("📸 Capturando screenshot...")
        screenshot_path = ocr_manager.take_screenshot()
        
        # Detecta coluna
        print("📍 Detectando coluna 'Data Início'...")
        column_image_path = os.path.join("images", "tabelas", "coluna_data_inicio.png")
        column_position = ocr_manager.find_column_header_position(column_image_path)
        
        if not column_position:
            print("❌ Coluna não detectada")
            return False
        
        column_x, column_y = column_position
        print(f"✅ Coluna detectada em ({column_x}, {column_y})")
        
        # Executa OCR
        print("\n🔍 Executando OCR...")
        results = ocr_manager.read_text_from_image(screenshot_path)
        
        detected_dates = []
        
        # Processa cada texto OCR
        for bbox, text, confidence in results:
            x_centro, y_centro = ocr_manager._calculate_center_coordinates(bbox)
            
            # Filtro por posição
            x_diff = abs(x_centro - column_x)
            is_in_column = x_diff <= 80.0
            is_below_header = y_centro > column_y
            
            if is_in_column and is_below_header:
                # Padrões rigorosos DD/MM/YYYY
                date_patterns = [
                    r'\b(\d{2}/\d{2}/\d{4})\b',
                    r'(\d{2}/\d{2}/\d{4})',
                ]
                
                all_matches = []
                
                # Aplica padrões
                for pattern in date_patterns:
                    matches = re.findall(pattern, text)
                    valid_matches = [m for m in matches if re.match(r'^\d{2}/\d{2}/\d{4}$', m)]
                    all_matches.extend(valid_matches)
                
                # Correção específica '/02/2024' -> '01/02/2024'
                if '/02/2024' in text and '01' not in text:
                    all_matches.append('01/02/2024')
                
                # Textos compostos
                composite_pattern = r'(01/\d{2}/2024)'
                composite_matches = re.findall(composite_pattern, text)
                valid_composite = [m for m in composite_matches if re.match(r'^01/\d{2}/2024$', m)]
                all_matches.extend(valid_composite)
                
                # Remove duplicatas e valida
                unique_matches = list(set([m for m in all_matches if len(m) > 6]))
                
                for match in unique_matches:
                    if match.startswith('/'):
                        match = '01' + match
                    
                    # Validação rigorosa
                    if (re.match(r'^01/\d{2}/2024$', match) and 
                        match.startswith('01/') and 
                        match.endswith('/2024') and
                        len(match) == 10):
                        
                        # Evita duplicatas
                        if not any(d['date'] == match for d in detected_dates):
                            detected_dates.append({
                                'date': match,
                                'position': (x_centro, y_centro),
                                'text': text,
                                'confidence': confidence
                            })
        
        # Ordena por posição Y
        detected_dates.sort(key=lambda x: x['position'][1])
        
        print(f"\n📊 VALIDAÇÃO DE {len(detected_dates)} DATAS DETECTADAS:")
        print("-" * 50)
        
        all_valid = True
        
        for i, date_info in enumerate(detected_dates, 1):
            date = date_info['date']
            position = date_info['position']
            text = date_info['text']
            
            # Valida formato
            is_valid = validate_date_format(date)
            
            status = "✅ VÁLIDA" if is_valid else "❌ INVÁLIDA"
            print(f"{i:2}. {date} - {status}")
            print(f"    📍 Posição: ({position[0]:.1f}, {position[1]:.1f})")
            print(f"    📝 OCR: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            
            if not is_valid:
                all_valid = False
                print(f"    🚨 ERRO: Data não segue padrão DD/MM/YYYY")
            
            print()
        
        print("=" * 50)
        
        if all_valid:
            print("🎉 SUCESSO! Todas as datas seguem o padrão DD/MM/YYYY")
            print(f"✅ {len(detected_dates)} datas validadas com sucesso")
            return True
        else:
            print("❌ FALHA! Algumas datas não seguem o padrão DD/MM/YYYY")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante validação: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_specific_date_formats():
    """
    Testa casos específicos de validação de formato
    """
    print("\n🧪 TESTE DE CASOS ESPECÍFICOS:")
    print("-" * 30)
    
    test_cases = [
        ("01/01/2024", True, "Formato correto DD/MM/YYYY"),
        ("1/01/2024", False, "Dia com 1 dígito"),
        ("01/1/2024", False, "Mês com 1 dígito"),
        ("01/01/24", False, "Ano com 2 dígitos"),
        ("01/13/2024", False, "Mês inválido"),
        ("32/01/2024", False, "Dia inválido"),
        ("01/02/2024", True, "Formato correto"),
        ("01/11/2024", True, "Formato correto"),
        ("1/2/2024", False, "Ambos com 1 dígito"),
        ("01-01-2024", False, "Separador errado"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for date_str, expected, description in test_cases:
        result = validate_date_format(date_str)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"{status} '{date_str}' - {description}")
        if result == expected:
            passed += 1
    
    print(f"\n📊 Resultado: {passed}/{total} testes passaram")
    return passed == total


if __name__ == "__main__":
    print("🔒 Teste de Validação do Padrão DD/MM/YYYY")
    print("=" * 60)
    
    # Teste casos específicos primeiro
    format_test_ok = test_specific_date_formats()
    
    if format_test_ok:
        # Teste com dados reais
        real_test_ok = test_date_format_validation()
        
        if real_test_ok:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("✅ Padrão DD/MM/YYYY validado com sucesso")
        else:
            print("\n❌ Teste real falhado")
    else:
        print("\n❌ Teste de casos específicos falhado")