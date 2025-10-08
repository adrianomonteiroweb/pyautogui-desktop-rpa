import time

from rpa import RPA, RPAResult
from csv_manager import ler_arquivo_csv
from files_manager import FilesManager

def main():
    rpa = RPA()
    
    try:
        empresas = ler_arquivo_csv("empresas")

        if not empresas:
            print("❌ Falha ao ler o arquivo de empresas.")
            return
        
        print(f"Encontradas {len(empresas)} empresas no arquivo CSV.")

        for empresa in empresas:
            init_result = rpa.init()

            if init_result != RPAResult.SUCCESS:
                print(f"❌ Falha na inicialização: {init_result.value}")
                return
        
            login_result = rpa.login_por_certificado()

            if login_result != RPAResult.SUCCESS:
                print(f"❌ Falha no login: {login_result}")
                return
        
            empresa_result = rpa.typeCNPJ(empresa['cnpj'])

            if empresa_result != RPAResult.SUCCESS:
                print(f"❌ Falha na seleção da empresa: {empresa_result.value}")
                return
            
            search_result = rpa.search()

            if search_result != RPAResult.SUCCESS:
                print(f"❌ Falha na pesquisa: {search_result.value}")
                return

            request_result = rpa.request_files()

            if request_result != RPAResult.SUCCESS:
                print(f"❌ Falha na solicitação dos arquivos: {request_result.value}")
                return
            
            downloads_result = rpa.download_files()

            if downloads_result != RPAResult.SUCCESS:
                print(f"❌ Falha no download dos arquivos: {downloads_result.value}")
                return
            
            print("Movendo arquivos baixados...")
            files_manager = FilesManager()
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
