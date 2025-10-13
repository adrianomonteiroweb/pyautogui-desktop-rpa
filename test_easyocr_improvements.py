"""
Teste de Validação das Melhorias no EasyOCRManager
Verifica se os métodos otimizados detectam corretamente as 11 datas da coluna Data Início
"""

import sys
import os

# Adiciona o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from easyocr_manager import EasyOCRManager


def test_optimized_extraction():
    """
    Testa o método otimizado extract_data_inicio_dates_optimized
    """
    print("🧪 TESTE DE VALIDAÇÃO - MÉTODOS OTIMIZADOS DO EASYOCRMANAGER")
    print("=" * 70)
    
    # Inicializa o manager
    ocr_manager = EasyOCRManager()
    
    print("\n🔍 Teste 1: Extração Otimizada de Datas")
    print("-" * 40)
    
    try:
        # Usa o método otimizado baseado nos testes
        detected_dates = ocr_manager.extract_data_inicio_dates_optimized()
        
        print(f"\n📊 Resultado: {len(detected_dates)} datas detectadas")
        
        if detected_dates:
            print("\n✅ Datas encontradas:")
            for i, date_info in enumerate(detected_dates, 1):
                date = date_info['date']
                x, y = date_info['position']
                date_type = date_info['type']
                confidence = date_info['confidence']
                
                # Classifica o padrão baseado na posição X
                if x > 500:
                    pattern_indicator = "🔵"
                    pattern_desc = "Composto (X≈524)"
                else:
                    pattern_indicator = "🟢"
                    pattern_desc = "Simples (X≈459)"
                
                print(f"  {i:2d}. {pattern_indicator} {date} → ({x:.1f}, {y:.1f}) [{pattern_desc}] (conf: {confidence:.2f})")
        
        # Valida o resultado
        expected_dates = [f"01/{m:02d}/2024" for m in range(1, 12)]  # 01/01 até 01/11
        found_dates = [d['date'] for d in detected_dates]
        
        print(f"\n🎯 Validação:")
        print(f"   📋 Esperado: {len(expected_dates)} datas (01/01/2024 até 01/11/2024)")
        print(f"   ✅ Encontrado: {len(found_dates)} datas")
        
        missing_dates = [d for d in expected_dates if d not in found_dates]
        extra_dates = [d for d in found_dates if d not in expected_dates]
        
        if missing_dates:
            print(f"   ❌ Faltando: {missing_dates}")
        
        if extra_dates:
            print(f"   ⚠️  Extras: {extra_dates}")
        
        if len(found_dates) == 11 and not missing_dates:
            print(f"   🎉 SUCESSO: Todas as 11 datas detectadas corretamente!")
            return True
        else:
            print(f"   ❌ FALHA: Nem todas as datas foram detectadas")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de extração otimizada: {e}")
        return False


def test_optimized_click_detection():
    """
    Testa a detecção de clique otimizada (sem executar clique real)
    """
    print("\n🔍 Teste 2: Detecção de Clique Otimizada")
    print("-" * 40)
    
    ocr_manager = EasyOCRManager()
    
    # Testa algumas datas específicas
    test_dates = ['01/01/2024', '01/02/2024', '01/04/2024', '01/07/2024', '01/11/2024']
    
    success_count = 0
    
    for test_date in test_dates:
        try:
            print(f"\n🎯 Testando detecção de: {test_date}")
            
            # Usa o método otimizado para encontrar a data
            detected_dates = ocr_manager.extract_data_inicio_dates_optimized()
            
            # Procura pela data específica
            found_match = None
            for date_info in detected_dates:
                if date_info['date'] == test_date:
                    found_match = date_info
                    break
            
            if found_match:
                x, y = found_match['position']
                date_type = found_match['type']
                print(f"   ✅ Data encontrada em ({x:.1f}, {y:.1f}) [{date_type}]")
                success_count += 1
            else:
                print(f"   ❌ Data não encontrada")
                
        except Exception as e:
            print(f"   ❌ Erro na detecção: {e}")
    
    print(f"\n📊 Resultado do teste de clique:")
    print(f"   ✅ Sucessos: {success_count}/{len(test_dates)}")
    print(f"   📈 Taxa de sucesso: {(success_count/len(test_dates)*100):.1f}%")
    
    return success_count == len(test_dates)


def main():
    """
    Executa todos os testes de validação
    """
    print("🚀 Iniciando testes de validação das melhorias...")
    
    # Executa os testes
    test1_result = test_optimized_extraction()
    test2_result = test_optimized_click_detection()
    
    print("\n" + "=" * 70)
    print("📊 RESUMO FINAL DOS TESTES")
    print("=" * 70)
    print(f"🧪 Teste 1 - Extração Otimizada: {'✅ PASSOU' if test1_result else '❌ FALHOU'}")
    print(f"🧪 Teste 2 - Detecção de Clique: {'✅ PASSOU' if test2_result else '❌ FALHOU'}")
    
    overall_success = test1_result and test2_result
    
    if overall_success:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Os métodos do EasyOCRManager foram otimizados com sucesso!")
        print("🚀 Sistema pronto para cliques automáticos precisos!")
    else:
        print("\n❌ ALGUNS TESTES FALHARAM")
        print("⚠️  Verifique os métodos que precisam de ajustes")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()