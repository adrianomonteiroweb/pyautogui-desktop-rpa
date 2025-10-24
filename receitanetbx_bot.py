from date_formatter import DateFormatter
from json_manager import JSONManager
from rpa import RPA, RPAResult, RPAConfig
from files_manager import FilesManager

def executar_receitanetbx(empresa, first_time):
    config = RPAConfig(
        confidence=0.9,  # Confidence baixo para encontrar e abrir a aplicação
        preview_mode=False,  # False para produção
        images_folder="images"
    )

    rpa = RPA(config)
    
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
        
        empresa_result = rpa.trocarPerfil(empresa['cnpj'], first_time=first_time)

        if empresa_result != RPAResult.SUCCESS:
            print(f"❌ Falha na seleção da empresa: {empresa_result.value if empresa_result else 'Resultado nulo'}")
            raise Exception(f"Falha na seleção da empresa: {empresa_result.value}")
        
        date_formatter = DateFormatter()
        
        for tipo in tipos_habilitados:
            print(f"  📋 Processando tipo: {tipo}")

            files_manager = FilesManager()
            
            period = json_manager.get_params().get("period")
            start_date_iso = period["start_date"]
            end_date_iso = period["end_date"]
            
            from datetime import datetime
            start_date_formatted = datetime.strptime(start_date_iso, "%Y-%m-%d").strftime("%d/%m/%Y")
            end_date_formatted = datetime.strptime(end_date_iso, "%Y-%m-%d").strftime("%d/%m/%Y")

            if tipo != "sped_fiscal":
                range_dates = date_formatter.generate_monthly_start_dates(start_date_formatted, end_date_formatted, format_type="dd/mm/yyyy")
            else:
                yearly_dates = date_formatter.generate_yearly_start_dates(start_date_formatted, end_date_formatted, format_type="dd/mm/yyyy")
                range_dates = [yearly_dates]

            for i, year_dates in enumerate(range_dates):
                is_first_iteration = (i == 0)
                last_month_start = year_dates[year_dates.__len__() - 1]
                
                end_date = date_formatter.get_last_day_of_month(last_month_start, input_format="dd/mm/yyyy")

                from datetime import datetime
                data_atual = datetime.now().strftime("%d/%m/%Y")
                end_date_dt = datetime.strptime(end_date, "%d/%m/%Y")
                data_atual_dt = datetime.strptime(data_atual, "%d/%m/%Y")

                if end_date_dt > data_atual_dt:
                    end_date = data_atual

                start_date = year_dates[0]

                search_result = rpa.search(tipo=tipo, start_date=start_date, end_date=end_date, is_first_iteration=is_first_iteration)

                if search_result != RPAResult.SUCCESS:
                    print(f"❌ Falha na pesquisa do tipo {tipo}: {search_result.value if search_result else 'Resultado nulo'}")
                    continue

                if tipo == "sped_fiscal":
                    range_dates = None
                else:
                    range_dates = year_dates

                request_result = rpa.select_dates(range_dates)

                if request_result != RPAResult.SUCCESS:
                    print(f"❌ Falha na solicitação dos arquivos para tipo {tipo}: {request_result.value if request_result else 'Resultado nulo'}")

                    if "arquivo não encontrado" in str(request_result.value).lower():
                        print(f"  ⏭️ Nenhum arquivo encontrado para tipo {tipo} - continuando...")
                        continue

                    raise Exception(f"Falha na solicitação dos arquivos: {request_result.value}")
                
                downloads_result = rpa.download_files()

                if downloads_result != RPAResult.SUCCESS:
                    print(f"❌ Falha no download dos arquivos para tipo {tipo}: {downloads_result.value if downloads_result else 'Resultado nulo'}")
                    raise Exception(f"Falha no download dos arquivos: {downloads_result.value}")
                
                print(f"  📁 Movendo arquivos do tipo {tipo}...")

                empresa_data = empresa.copy()
                empresa_data['data_inicial'] = start_date.replace('/', '')
                empresa_data['data_final'] = end_date.replace('/', '')
                empresa_data['tipo'] = tipo
                
                move_result = files_manager.move_files(data=empresa_data)
                
                if move_result["success"]:
                    print(f"  ✅ {move_result['message']}")
                else:
                    print(f"  ❌ Erro ao mover arquivos do tipo {tipo}: {move_result.get('error', 'Erro desconhecido')}")

            print(f"\n🎉 Arquivos tipo: {tipo} baixados com sucesso!")
    finally:
        rpa.close()
