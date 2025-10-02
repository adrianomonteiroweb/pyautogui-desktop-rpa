from rpa import RPA, RPAConfig, RPAResult


def main():
    config = RPAConfig(
        confidence=0.9,           # Confiança alta para ser mais preciso
        double_click_interval=0.1, # Intervalo entre os cliques do double click
        startup_delay=3,          # Tempo de espera antes de iniciar
        images_folder="images",   # Pasta onde estão as imagens
        preview_mode=False        # Desabilitado por padrão
    )
    
    # Inicializa o RPA
    rpa = RPA(config)
    
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
