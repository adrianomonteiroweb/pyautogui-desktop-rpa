import time

from date_formatter import DateFormatter
from json_manager import JSONManager
from rpa import RPA, RPAResult
from files_manager import FilesManager

from csv_manager import ler_arquivo_csv

def main():
    rpa = RPA()
    
    json_manager = JSONManager()
    tipos = json_manager.get_params().get("types")

    for key in filter(lambda x: x[1] is True, tipos.items()):
        print(f"Iniciando busca do tipo: {key[0]}")

        empresas = ler_arquivo_csv("empresas")

        if not empresas:
            print("❌ Falha ao ler o arquivo de empresas.")
            return
            
        print(f"Encontradas {len(empresas)} empresas no arquivo CSV.")

        try:
            init_result = rpa.init()

            if init_result != RPAResult.SUCCESS:
                print(f"❌ Falha na inicialização: {init_result.value if init_result else 'Resultado nulo'}")
                return
        
            for index, empresa in enumerate(empresas):
                    print(f"\nIniciando processo para a empresa: {empresa['nome']} - CNPJ: {empresa['cnpj']}")
                    empresa_result = rpa.trocarPerfil(empresa['cnpj'], first_time=(index == 0))

                    if empresa_result != RPAResult.SUCCESS:
                        print(f"❌ Falha na seleção da empresa: {empresa_result.value if empresa_result else 'Resultado nulo'}")
                        return
                    
                    search_result = rpa.search(tipo=key[0])
                    
                    if search_result != RPAResult.SUCCESS:
                        print(f"❌ Falha na pesquisa: {search_result.value if search_result else 'Resultado nulo'}")
                        return

                    request_result = rpa.request_files()

                    if request_result != RPAResult.SUCCESS:
                        print(f"❌ Falha na solicitação dos arquivos: {request_result.value if request_result else 'Resultado nulo'}")
                        return
                    
                    downloads_result = rpa.download_files()

                    if downloads_result != RPAResult.SUCCESS:
                        print(f"❌ Falha no download dos arquivos: {downloads_result.value if downloads_result else 'Resultado nulo'}")
                        return
                    
                    print("Movendo arquivos baixados...")
                    files_manager = FilesManager()

                    json_manager = JSONManager()
                    period = json_manager.get_params().get("period")
                    start_date = DateFormatter.iso_to_ddmmyyyy(period["start_date"])
                    end_date = DateFormatter.iso_to_ddmmyyyy(period["end_date"])

                    empresa['data_inicial'] = start_date
                    empresa['data_final'] = end_date
                    empresa['tipo'] = key[0]

                    move_result = files_manager.move_files(data=empresa)
                    
                    if move_result["success"]:
                        print(f"✅ {move_result['message']}")
                    else:
                        print(f"❌ Erro ao mover arquivos: {move_result.get('error', 'Erro desconhecido')}")

                    print("\n🎉 Automação concluída com sucesso!")

        except Exception as e:
            print(f"❌ Erro: {e}")
            time.sleep(60 * 5)  # Espera 5 minutos em caso de erro inesperado
        finally:
            rpa.close()
            time.sleep(2)  # Espera 2 segundos antes de iniciar a próxima iteração


if __name__ == "__main__":
    main()
