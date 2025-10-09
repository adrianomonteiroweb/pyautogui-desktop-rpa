import time
import uuid

from date_formatter import DateFormatter
from json_manager import JSONManager
from rpa import RPA, RPAResult
from files_manager import FilesManager
from text_formatter import TextFormatter

from csv_manager import ler_arquivo_csv

def for_each_with_retry(items, process_func, max_retries=2, retry_delay=300, item_name_func=None):
    """
    Estrutura de repetição genérica com:
    - Retry automático em caso de erro
    - Skip em caso de resultado 'Unfinish'
    - ID único para evitar reprocessamento
    
    Args:
        items: Lista de items para processar
        process_func: Função que processa cada item
        max_retries: Número máximo de tentativas (padrão: 2)
        retry_delay: Tempo de espera entre tentativas em segundos (padrão: 300)
        item_name_func: Função para extrair nome do item para logs (opcional)
    """
    processed_ids = set()
    
    for item in items:
        # Gera ID único se não existir
        if not isinstance(item, dict):
            item = {"data": item, "id": str(uuid.uuid4())}
        elif 'id' not in item:
            item['id'] = str(uuid.uuid4())
        
        item_id = item['id']
        
        # Nome do item para logs
        if item_name_func:
            item_name = item_name_func(item)
        elif isinstance(item, dict) and 'nome' in item:
            item_name = item['nome']
        elif isinstance(item, dict) and 'name' in item:
            item_name = item['name']
        else:
            item_name = str(item_id)[:8]
        
        # Pula se já foi processado nesta execução
        if item_id in processed_ids:
            print(f"⏭️ Pulando item {item_name} - já processado nesta execução")
            continue
            
        processed_ids.add(item_id)
        
        attempts = 0

        while attempts <= max_retries:
            try:
                print(f"🔄 Tentativa {attempts + 1} para item: {item_name}")
                
                result = process_func(item, attempts == 0)
                
                if result == "Unfinish":
                    print(f"⏭️ Item {item_name} retornou 'Unfinish' - pulando para próximo")
                    break
                elif result == "Success":
                    print(f"✅ Item {item_name} processado com sucesso")
                    break
                else:
                    print(f"✅ Item {item_name} concluído")
                    break
                    
            except Exception as e:
                # Verifica se é uma exceção "Unfinish"
                if str(e).startswith("Unfinish:"):
                    message = str(e).replace("Unfinish: ", "")
                    print(f"⏭️ {message} - pulando para próximo item")
                    break
                
                attempts += 1

                print(f"❌ Erro na tentativa {attempts} para item {item_name}: {e}")
                
                if attempts > max_retries:
                    print(f"❌ Esgotadas as tentativas para item {item_name} após {max_retries + 1} tentativas")
                    break
                else:
                    print(f"🔄 Tentando novamente em {retry_delay} segundos...")
                    time.sleep(retry_delay)

def process_empresa(empresa, first_time):
    """Função que processa cada empresa para todos os tipos habilitados"""

    rpa = RPA()
    
    try:
        json_manager = JSONManager()
        tipos = json_manager.get_params().get("types")
        tipos_habilitados = [key for key, value in tipos.items() if value is True]
        
        if not tipos_habilitados:
            print("❌ Nenhum tipo habilitado nos parâmetros para processamento.")
            return "Unfinish"
        
        init_result = rpa.init()

        if init_result != RPAResult.SUCCESS:
            print(f"❌ Falha na inicialização: {init_result.value if init_result else 'Resultado nulo'}")
            raise Exception(f"Falha na inicialização: {init_result.value}")
        
        # Troca perfil para a empresa
        empresa_result = rpa.trocarPerfil(empresa['cnpj'], first_time=first_time)

        if empresa_result != RPAResult.SUCCESS:
            print(f"❌ Falha na seleção da empresa: {empresa_result.value if empresa_result else 'Resultado nulo'}")
            raise Exception(f"Falha na seleção da empresa: {empresa_result.value}")
        
        # Processa todos os tipos habilitados para esta empresa
        for tipo in tipos_habilitados:
            print(f"  📋 Processando tipo: {tipo}")

            search_result = rpa.search(tipo=tipo)

            if search_result != RPAResult.SUCCESS:
                print(f"❌ Falha na pesquisa do tipo {tipo}: {search_result.value if search_result else 'Resultado nulo'}")
                continue  # Continua com outros tipos

            files_manager = FilesManager()
            
            period = json_manager.get_params().get("period")
            # Convert ISO dates to DD/MM/YYYY format for generate_monthly_start_dates
            start_date_iso = period["start_date"]  # e.g., "2025-01-01"
            end_date_iso = period["end_date"]      # e.g., "2025-12-31"
            
            # Convert ISO to DD/MM/YYYY format for the date generator
            from datetime import datetime
            start_date_formatted = datetime.strptime(start_date_iso, "%Y-%m-%d").strftime("%d/%m/%Y")
            end_date_formatted = datetime.strptime(end_date_iso, "%Y-%m-%d").strftime("%d/%m/%Y")

            # range_dates só deve ser igual a ele mesmo se tipo for diferente de "sped_fiscal"
            if tipo != "sped_fiscal":
                range_dates = DateFormatter.generate_monthly_start_dates(start_date_formatted, end_date_formatted, format_type="dd/mm/yyyy")
            else:
                range_dates = None

            request_result = rpa.request_files(range_dates=range_dates)

            if request_result != RPAResult.SUCCESS:
                print(f"❌ Falha na solicitação dos arquivos para tipo {tipo}: {request_result.value if request_result else 'Resultado nulo'}")
                # Se for um caso específico que deve pular, continue
                if "arquivo não encontrado" in str(request_result.value).lower():
                    print(f"  ⏭️ Nenhum arquivo encontrado para tipo {tipo} - continuando...")
                    continue
                raise Exception(f"Falha na solicitação dos arquivos: {request_result.value}")
            
            
            downloads_result = rpa.download_files()

            if downloads_result != RPAResult.SUCCESS:
                print(f"❌ Falha no download dos arquivos para tipo {tipo}: {downloads_result.value if downloads_result else 'Resultado nulo'}")
                raise Exception(f"Falha no download dos arquivos: {downloads_result.value}")
            
            print(f"  📁 Movendo arquivos do tipo {tipo}...")

            # Convert dates to DDMMYYYY format for file manager
            start_date_ddmmyyyy = DateFormatter.iso_to_ddmmyyyy(period["start_date"])
            end_date_ddmmyyyy = DateFormatter.iso_to_ddmmyyyy(period["end_date"])
            
            empresa_data = empresa.copy()
            empresa_data['data_inicial'] = start_date_ddmmyyyy
            empresa_data['data_final'] = end_date_ddmmyyyy
            empresa_data['tipo'] = tipo
            
            move_result = files_manager.move_files(data=empresa_data)
            
            if move_result["success"]:
                print(f"  ✅ {move_result['message']}")
            else:
                print(f"  ❌ Erro ao mover arquivos do tipo {tipo}: {move_result.get('error', 'Erro desconhecido')}")
        
        print("\n🎉 Automação concluída com sucesso!")
        return "Success"
        
    finally:
        rpa.close()
        time.sleep(2)

def main():
    print("📋 Carregando empresas do arquivo CSV...")

    empresas = ler_arquivo_csv("empresas")
    
    if not empresas:
        print("❌ Falha ao ler o arquivo de empresas.")
        return
    
    json_manager = JSONManager()
    cnpj = json_manager.get_params().get("cnpj")

    text_formatter = TextFormatter()

    empresas_filtradas = list(filter(lambda e: e['cnpj'] == text_formatter.getOnlyNumbers(cnpj), empresas)) or empresas
        
    print(f"✅ Encontradas {len(empresas_filtradas)} empresas.")
    
    # Função para extrair nome da empresa para logs
    def get_empresa_name(empresa):
        return f"{empresa['nome']} - CNPJ: {empresa['cnpj']}"
    
    # Processa cada empresa com retry automático (espera 5 minutos entre tentativas)
    for_each_with_retry(
        items=empresas_filtradas,
        process_func=process_empresa,
        max_retries=2,
        retry_delay=300,  # 5 minutos como no código original
        item_name_func=get_empresa_name
    )
    
    print("\n🎉 Processamento de todas as empresas concluído!")


if __name__ == "__main__":
    main()
