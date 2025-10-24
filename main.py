from json_manager import JSONManager
from text_formatter import TextFormatter

from csv_manager import ler_arquivo_csv
from utils import for_each
from receitanetbx_bot import executar_receitanetbx

def main():
    empresas_result = ler_arquivo_csv("empresas")

    if not empresas_result or not empresas_result.get('dados'):
        print("Nenhuma empresa encontrada no CSV.")
        return
    
    empresas = empresas_result['dados']
    
    json_manager = JSONManager()
    cnpj = json_manager.get_params().get("cnpj")

    text_formatter = TextFormatter()

    empresas_filtradas = list(filter(lambda e: e['cnpj'] == text_formatter.getOnlyNumbers(cnpj), empresas)) or empresas
        
    print(f"✅ Encontradas {len(empresas_filtradas)} empresas.")
    
    def get_empresa_name(empresa):
        return f"{empresa['nome']} - CNPJ: {empresa['cnpj']}"
    
    for_each(
        items=empresas_filtradas,
        process_func=executar_receitanetbx,
        max_retries=0,
        retry_delay=2,
        item_name_func=get_empresa_name
    )
    
    print("\n🎉 Processamento de todas as empresas concluído!")


if __name__ == "__main__":
    main()
