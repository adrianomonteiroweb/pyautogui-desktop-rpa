#!/usr/bin/env python3
"""
Teste rápido para verificar a função get_last_day_of_month
"""

from date_formatter import DateFormatter

def test_get_last_day_of_month():
    print("=== Teste da função get_last_day_of_month ===\n")
    
    # Casos de teste
    test_cases = [
        ("01/10/2025", "dd/mm/yyyy"),  # Outubro - 31 dias
        ("01/02/2024", "dd/mm/yyyy"),  # Fevereiro ano bissexto - 29 dias
        ("01/02/2025", "dd/mm/yyyy"),  # Fevereiro ano normal - 28 dias
        ("01/04/2025", "dd/mm/yyyy"),  # Abril - 30 dias
        ("15/12/2025", "dd/mm/yyyy"),  # Dezembro - qualquer dia do mês
        ("01122025", "ddmmyyyy"),      # Formato DDMMYYYY
        ("2025-01-01", "iso"),         # Formato ISO
    ]
    
    for date_input, format_type in test_cases:
        try:
            result = DateFormatter.get_last_day_of_month(date_input, format_type)
            print(f"Input: {date_input} ({format_type}) -> Output: {result}")
        except Exception as e:
            print(f"❌ Erro para {date_input}: {e}")
    
    print("\n=== Teste específico do cenário do main.py ===")
    
    # Teste específico para o cenário mencionado
    year_dates_example = ["01/01/2025", "01/02/2025", "01/03/2025", "01/10/2025"]
    last_month_start = year_dates_example[len(year_dates_example) - 1]  # "01/10/2025"
    
    print(f"year_dates exemplo: {year_dates_example}")
    print(f"Último elemento (data inicial do mês): {last_month_start}")
    
    end_date = DateFormatter.get_last_day_of_month(last_month_start, input_format="dd/mm/yyyy")
    print(f"Data final calculada: {end_date}")
    print(f"✅ Correto! {last_month_start} -> {end_date}")

if __name__ == "__main__":
    test_get_last_day_of_month()