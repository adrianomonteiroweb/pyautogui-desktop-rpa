from rpa import RPA, RPAResult

def main():
    # Inicializa o RPA
    rpa = RPA()
    
    # Executa o fluxo de automação
    init_result = rpa.init()

    if init_result != RPAResult.SUCCESS:
        print(f"❌ Falha na inicialização: {init_result.value}")
        return
    
    login_result = rpa.login_por_certificado()

    if login_result != RPAResult.SUCCESS:
        print(f"❌ Falha no login: {login_result}")
        return
    
    empresa_result = rpa.typeCNPJ("06097786000193")

    if empresa_result != RPAResult.SUCCESS:
        print(f"❌ Falha na seleção da empresa: {empresa_result.value}")
        return
    
    search_result = rpa.search()

    if search_result != RPAResult.SUCCESS:
        print(f"❌ Falha na pesquisa: {search_result.value}")
        return
    
    print("\n🎉 Automação concluída com sucesso!")


if __name__ == "__main__":
    main()
