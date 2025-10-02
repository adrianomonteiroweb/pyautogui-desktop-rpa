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
        print(f"❌ Falha no login: {login_result.value}")
        return
    
    empresa_result = rpa.selectEmpresa("06097786000193")

    if empresa_result != RPAResult.SUCCESS:
        print(f"❌ Falha na seleção da empresa: {empresa_result.value}")
        return
    
    print("\n🎉 Automação concluída com sucesso!")


if __name__ == "__main__":
    main()
