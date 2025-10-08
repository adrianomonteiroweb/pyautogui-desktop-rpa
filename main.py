import time
from rpa import RPA, RPAResult
from csv_manager import ler_arquivo_csv

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
            
            print("\n🎉 Automação concluída com sucesso!")

    except Exception as e:
        print(f"❌ Erro inesperado durante a execução: {str(e)}")
        time.sleep(30)  # Pausa para permitir leitura do erro
    
    finally:
        rpa.close()


if __name__ == "__main__":
    main()
