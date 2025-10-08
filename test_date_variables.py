#!/usr/bin/env python3
"""
Teste das variáveis de data no FilesManager
"""

from files_manager import FilesManager
from datetime import datetime

def test_date_variables():
    """Testa se as variáveis de data estão sendo adicionadas corretamente"""
    
    files_manager = FilesManager()
    
    # Teste com dados de empresa
    empresa_teste = {
        "cnpj": "12345678000195",
        "razao_social": "EMPRESA TESTE LTDA"
    }
    
    print("=== TESTE DAS VARIÁVEIS DE DATA ===\n")
    
    # Teste 1: Verificar se as variáveis são adicionadas no get_info
    print("1. Testando get_info():")
    info = files_manager.get_info(empresa_teste.copy())
    empresa_data = info.get('empresa_data', {})
    
    print(f"   - Dados da empresa: {empresa_data}")
    print(f"   - Tem _dia: {'_dia' in empresa_data}")
    print(f"   - Tem _mes: {'_mes' in empresa_data}")
    print(f"   - Tem _ano: {'_ano' in empresa_data}")
    
    if all(key in empresa_data for key in ['_dia', '_mes', '_ano']):
        print("   ✓ SUCESSO: Todas as variáveis de data foram adicionadas!")
    else:
        print("   ✗ ERRO: Alguma variável de data está faltando!")
    
    # Teste 2: Verificar se as variáveis são consistentes com a data atual
    print("\n2. Testando consistência com data atual:")
    now = datetime.now()
    
    print(f"   - Data atual: {now.day}/{now.month}/{now.year}")
    print(f"   - Variáveis: {empresa_data.get('_dia')}/{empresa_data.get('_mes')}/{empresa_data.get('_ano')}")
    
    if (empresa_data.get('_dia') == now.day and 
        empresa_data.get('_mes') == now.month and 
        empresa_data.get('_ano') == now.year):
        print("   ✓ SUCESSO: Variáveis de data estão corretas!")
    else:
        print("   ✗ ERRO: Variáveis de data não correspondem à data atual!")
    
    # Teste 3: Verificar se as variáveis originais da empresa são preservadas
    print("\n3. Testando preservação dos dados originais:")
    print(f"   - CNPJ original preservado: {'cnpj' in empresa_data}")
    print(f"   - Razão social preservada: {'razao_social' in empresa_data}")
    
    if empresa_data.get('cnpj') == empresa_teste['cnpj']:
        print("   ✓ SUCESSO: Dados originais preservados!")
    else:
        print("   ✗ ERRO: Dados originais foram alterados!")
    
    # Teste 4: Verificar se funciona com dicionário vazio
    print("\n4. Testando com dicionário vazio:")
    empresa_vazia = {}
    info_vazia = files_manager.get_info(empresa_vazia)
    empresa_data_vazia = info_vazia.get('empresa_data', {})
    
    if all(key in empresa_data_vazia for key in ['_dia', '_mes', '_ano']):
        print("   ✓ SUCESSO: Variáveis de data adicionadas mesmo com dicionário vazio!")
    else:
        print("   ✗ ERRO: Variáveis de data não foram adicionadas com dicionário vazio!")
    
    print("\n=== FIM DOS TESTES ===")

if __name__ == "__main__":
    test_date_variables()