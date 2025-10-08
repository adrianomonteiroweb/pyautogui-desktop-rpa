import time

from date_formatter import DateFormatter
from json_manager import JSONManager
from rpa import RPA, RPAResult
from csv_manager import ler_arquivo_csv
from files_manager import FilesManager

def main():
    rpa = RPA()
    
    try:
        json_manager = JSONManager()
        tipos = json_manager.get_params().get("types")

        for key in filter(lambda x: x[1] is True, tipos.items()):
            print(f"Iniciando busca do tipo: {key[0]}")

            empresas = ler_arquivo_csv("empresas")

            if not empresas:
                print("❌ Falha ao ler o arquivo de empresas.")
                return
            
            print(f"Encontradas {len(empresas)} empresas no arquivo CSV.")

            for empresa in empresas:
                init_result = rpa.init()

                if init_result != RPAResult.SUCCESS:
                    print(f"❌ Falha na inicialização: {init_result.value if init_result else 'Resultado nulo'}")
                    return
            
                login_result = rpa.login_por_certificado()

                if login_result != RPAResult.SUCCESS:
                    print(f"❌ Falha no login: {login_result.value if login_result else 'Resultado nulo'}")
                    return
            
                empresa_result = rpa.typeCNPJ(empresa['cnpj'])

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
        print(f"❌ Erro inesperado durante a execução: {str(e)}")
        time.sleep(30)  # Pausa para permitir leitura do erro
    
    finally:
        rpa.close()


if __name__ == "__main__":
    main()
