import pyautogui as PyAutoGui
import time
import os
from dataclasses import dataclass
from enum import Enum

from json_manager import JSONManager
from date_formatter import DateFormatter

class RPAResult(Enum):
    SUCCESS = "success"
    IMAGE_NOT_FOUND = "image_not_found"
    FILE_NOT_EXISTS = "file_not_exists"
    CLICK_FAILED = "click_failed"


@dataclass
class RPAConfig:
    confidence: float = 0.95
    double_click_interval: float = 0.1
    startup_delay: int = 3
    images_folder: str = "images"
    preview_mode: bool = False


class RPA:
    def __init__(self, config: RPAConfig = None):
        self.config = config or RPAConfig()
        self.desktop_rpa = None
        self.last_click_y = None  # Controle de posição Y para filtros de coluna
        self._setup_pyautogui()
    
    def _setup_pyautogui(self) -> None:
        PyAutoGui.FAILSAFE = True
        PyAutoGui.PAUSE = 0.1
    
    def reset_click_position(self) -> None:
        """Reseta a posição Y do último clique para permitir nova busca desde o início"""
        self.last_click_y = None
    
    def set_confidence(self, confidence: float) -> None:
        """Altera o confidence dinamicamente durante a execução"""
        self.config.confidence = confidence
    
    def _get_image_path(self, alias, filename: str) -> str:
        if alias:
            return os.path.join(self.config.images_folder, alias, filename)
        else:
            return os.path.join(self.config.images_folder, filename)
    
    def _validate_image_file(self, image_path: str) -> bool:
        return os.path.exists(image_path)
    
    def _find_all_image_locations(self, image_path: str, confidence: float = None) -> list:
        try:
            conf = confidence if confidence is not None else self.config.confidence
            locations = list(PyAutoGui.locateAllOnScreen(image_path, confidence=conf))
            return locations
        except Exception as e:
            print(f"Erro ao procurar imagem: {e}")
            return []
    
    def _locate_and_double_click_image(self, image_path: str, description: str, silent: bool = False) -> RPAResult:
        try:
            all_locations = self._find_all_image_locations(image_path)
            
            if not all_locations and self.config.confidence > 0.6:
                if not silent:
                    print(f"⚠ Tentando com menor precisão para {description}...")
                all_locations = self._find_all_image_locations(image_path, confidence=0.6)
            
            if not all_locations:
                if not silent:
                    print(f"✗ Não foi possível localizar {description}")
                return RPAResult.IMAGE_NOT_FOUND
            
            if len(all_locations) == 1:
                location = all_locations[0]
                center = PyAutoGui.center(location)
                
                PyAutoGui.doubleClick(center, interval=self.config.double_click_interval)
                return RPAResult.SUCCESS
            
            else:
                if not silent:
                    print("  Múltiplas ocorrências encontradas:")
                    for i, location in enumerate(all_locations, 1):
                        center = PyAutoGui.center(location)
                        print(f"    {i}. Posição: {center}")
                
                location = all_locations[0]
                center = PyAutoGui.center(location)
                
                PyAutoGui.doubleClick(center, interval=self.config.double_click_interval)
                return RPAResult.SUCCESS
                
        except Exception as e:
            if not silent:
                print(f"✗ Erro ao tentar dar double click em {description}: {e}")
            return RPAResult.CLICK_FAILED

    def _locate_and_single_click_image(self, image_path: str, description: str, silent: bool = False) -> RPAResult:
        try:
            all_locations = self._find_all_image_locations(image_path)
            
            if not all_locations and self.config.confidence > 0.6:
                if not silent:
                    print(f"⚠ Tentando com menor precisão para {description}...")
                all_locations = self._find_all_image_locations(image_path, confidence=0.6)
            
            if not all_locations:
                if not silent:
                    print(f"✗ Não foi possível localizar {description}")
                return RPAResult.IMAGE_NOT_FOUND
            
            if len(all_locations) == 1:
                location = all_locations[0]
                center = PyAutoGui.center(location)
                
                PyAutoGui.click(center)
                return RPAResult.SUCCESS
            
            else:
                if not silent:
                    print("  Múltiplas ocorrências encontradas:")
                    for i, location in enumerate(all_locations, 1):
                        center = PyAutoGui.center(location)
                        print(f"    {i}. Posição: {center}")
                
                location = all_locations[0]
                center = PyAutoGui.center(location)
                
                PyAutoGui.click(center)
                return RPAResult.SUCCESS
                
        except Exception as e:
            if not silent:
                print(f"✗ Erro ao tentar dar click único em {description}: {e}")
            return RPAResult.CLICK_FAILED
    
    def _wait_with_countdown(self, seconds: int, message: str = "Iniciando...") -> None:
        for i in range(seconds, 0, -1):
            time.sleep(1)

    def _wait_for_image(self, image_filename: str, alias: str = "", timeout: int = 30, check_interval: float = 1.0) -> RPAResult:
        image_path = self._get_image_path(alias, image_filename)
        
        if not self._validate_image_file(image_path):
            print(f"✗ Arquivo de imagem não encontrado: {image_path}")
            return RPAResult.FILE_NOT_EXISTS
        
        elapsed_time = 0.0
        tried_lower_confidence = False
        
        while elapsed_time < timeout:
            try:
                confidence_to_use = self.config.confidence
                
                if elapsed_time > timeout / 2 and not tried_lower_confidence and self.config.confidence > 0.6:
                    confidence_to_use = 0.6
                    tried_lower_confidence = True
                
                location = PyAutoGui.locateOnScreen(image_path, confidence=confidence_to_use)
                
                if location is not None:
                    PyAutoGui.center(location)
                    return RPAResult.SUCCESS
                
                time.sleep(check_interval)
                elapsed_time += check_interval
                
            except Exception as e:
                time.sleep(check_interval)
                elapsed_time += check_interval
        
        print(f"✗ Timeout: Imagem {image_filename} não foi encontrada em {timeout} segundos")
        return RPAResult.IMAGE_NOT_FOUND
    
    def _single_click_image(self, image_filename: str, alias: str = "", silent: bool = False) -> RPAResult:
        image_path = self._get_image_path(alias, image_filename)

        if not self._validate_image_file(image_path):
            if not silent:
                print(f"✗ Arquivo de imagem não encontrado: {image_path}")
            return RPAResult.FILE_NOT_EXISTS
        
        result = self._locate_and_single_click_image(image_path, f"imagem ({image_filename})", silent)
        
        if not silent:
            if result == RPAResult.CLICK_FAILED:
                print("✗ Falha ao executar o click único")
            elif result == RPAResult.IMAGE_NOT_FOUND:
                print(f"⚠ Imagem {image_filename} não encontrada na tela")
        
        return result

    def _double_click_image(self, icon_filename: str = "icon.png", alias: str = "", silent: bool = False) -> RPAResult:
        if not silent:
            self._wait_with_countdown(self.config.startup_delay)
        
        image_path = self._get_image_path(alias, icon_filename)
        
        if not self._validate_image_file(image_path):
            if not silent:
                print(f"✗ Arquivo de imagem não encontrado: {image_path}")
            return RPAResult.FILE_NOT_EXISTS
        
        result = self._locate_and_double_click_image(image_path, f"ícone ({icon_filename})", silent)
        
        if not silent:
            if result == RPAResult.CLICK_FAILED:
                print("✗ Falha ao executar o double click")
            elif result == RPAResult.IMAGE_NOT_FOUND:
                print("⚠ Ícone não encontrado na tela")
        
        return result

    def _selectOption(self, combo_image: str, option_image: str, alias: str, attempts: int = 2) -> RPAResult:
        for attempt in range(attempts):
            
            combo_result = self._wait_for_image(combo_image, alias, timeout=10)

            if combo_result != RPAResult.SUCCESS:
                if attempt < attempts - 1:
                    time.sleep(1)
                    continue
                else:
                    return combo_result
            
            self._single_click_image(combo_image, alias)
            
            option_result = self._wait_for_image(option_image, alias, timeout=10)

            if option_result == RPAResult.SUCCESS:
                click_result = self._single_click_image(option_image, alias)
                
                if click_result == RPAResult.SUCCESS:
                    return RPAResult.SUCCESS    
            
            if attempt < attempts - 1:
                time.sleep(1)
        
        return RPAResult.IMAGE_NOT_FOUND
    
    def init(self) -> RPAResult:
        print("\nAbrindo o ReceitanetBX...")
        time.sleep(2)

        wait_result = self._wait_for_image("icon.png", "botoes", timeout=10)
        
        if wait_result == RPAResult.SUCCESS:
            return self._double_click_image("icon.png", "botoes")
        else:
            print(f"\n❌ ERRO: {wait_result.value}")
            return wait_result
        
    def close(self) -> None:
        self.set_confidence(0.9)

        time.sleep(5)
        
        print("\nFechando o ReceitanetBX...")

        close_buttons = [
            ("fechar.png", "botoes"),
            ("fechar2.png", "botoes"),
            ("sair.png", "botoes"),
        ]
        
        for button_file, button_alias in close_buttons:
            result = self._double_click_image(button_file, button_alias, silent=True)
            
            if result == RPAResult.SUCCESS:
                print(f"✅ ReceitanetBX fechado usando: {button_file}")
                return
        
        print("⚠ Não foi possível fechar o ReceitanetBX automaticamente")
        
    def _selecionar_certificado(self) -> RPAResult:

        json_manager = JSONManager()
        settings = json_manager.get_settings()
        certificado = settings.get("certificado", "cert.png")
        
        print(f"Selecionando certificado: {certificado}")
            
        return self._single_click_image(f"{certificado}.png", "certificados")
        
    def trocarPerfil(self, cnpj, first_time) -> RPAResult:
        self.set_confidence(0.9)

        botao_entrar = self._wait_for_image("entrar.png", "botoes", timeout=5)

        if botao_entrar != RPAResult.SUCCESS:
            self._double_click_image("icone_trocar_perfil.png", "botoes")

        self._selecionar_certificado()

        self._single_click_image("combo_perfil_contribuinte.png", "comboboxes/perfil")
        self._single_click_image("opcao_procurador.png", "comboboxes/perfil", silent=True)
        

        self._selectOption("combo_tipo_doc.png", "opcao_cnpj.png", "comboboxes/tipo_doc")
        self._single_click_image("cnpj_input.png", "inputs")
        
        PyAutoGui.write(cnpj, interval=0.1)

        botao_entrar = self._wait_for_image("entrar.png", "botoes", timeout=5)

        if botao_entrar == RPAResult.SUCCESS:
            return self._single_click_image("entrar.png", "botoes")
        
        botao_trocar_perfil = self._wait_for_image("trocar_perfil.png", "botoes", timeout=5)
        
        if botao_trocar_perfil == RPAResult.SUCCESS:
            return self._single_click_image("trocar_perfil.png", "botoes")
        
        print("✗ Nenhuma das imagens foi encontrada: entrar.png ou trocar_perfil.png")
        return RPAResult.IMAGE_NOT_FOUND

    def _searchSPED(self, start_date, end_date, is_first_iteration) -> RPAResult:
        if is_first_iteration:
            self._selectOption("combo_arquivo.png", "opcao_escrituracao.png", "comboboxes/arquivo")
            self._selectOption("combo_pesquisa.png", "opcao_periodo_escrituracao.png", "comboboxes/pesquisa")

        print(f"Buscando arquivos no período entre {start_date} e {end_date}...")

        start_date = start_date.replace("/", "")
        end_date = end_date.replace("/", "")

        self._single_click_image("input_data_inicio.png", "inputs")

        PyAutoGui.write(start_date, interval=0.1)
        PyAutoGui.press("Tab")
        PyAutoGui.write(end_date, interval=0.1)
        PyAutoGui.press("Enter")
        
        self._single_click_image("pesquisar.png", "botoes")

        try:
            return self._dispatch_message_if_exists()
        except Exception as e:
            if str(e).startswith("Unfinish:"):
                raise e
            return RPAResult.ERROR
        
    def _dispatch_message_if_exists(self) -> RPAResult:
        time.sleep(5)
        
        # Verifica modal_sem_resultados silenciosamente
        image_path = self._get_image_path("modais", "modal_sem_resultados.png")
        if self._validate_image_file(image_path):
            try:
                location = PyAutoGui.locateOnScreen(image_path, confidence=self.config.confidence)
                if location is not None:
                    message = "⚠ Nenhum arquivo foi encontrado para o critério de pesquisa solicitado."
                    print(message)
                    time.sleep(1)
                    self._double_click_image("ok.png", "botoes", silent=True)
                    PyAutoGui.press("Enter")
                    # Lança exceção com mensagem "Unfinish" para o loop entender que deve pular
                    raise Exception("Unfinish: " + message)
            except Exception as e:
                # Re-lança se for uma exceção Unfinish
                if "Unfinish:" in str(e):
                    raise e
                # Ignora outros erros (como erros de localização de imagem)
                pass

        # Verifica modal_nenhum_arquivo_encontrado silenciosamente
        image_path = self._get_image_path("modais", "modal_nenhum_arquivo_encontrado.png")
        if self._validate_image_file(image_path):
            try:
                location = PyAutoGui.locateOnScreen(image_path, confidence=self.config.confidence)
                if location is not None:
                    message = "⚠ Nenhum arquivo encontrado correspondente a busca."
                    print(message)
                    time.sleep(1)
                    self._double_click_image("ok.png", "botoes", silent=True)
                    self._double_click_image("fechar.png", "botoes", silent=True)
                    # Lança exceção com mensagem "Unfinish" para o loop entender que deve pular
                    raise Exception("Unfinish: " + message)
            except Exception as e:
                # Re-lança se for uma exceção Unfinish
                if "Unfinish:" in str(e):
                    raise e
                # Ignora outros erros (como erros de localização de imagem)
                pass

        # Verifica modal de erro de procuração eletrônica
        image_path = self._get_image_path("modais", "modal_nao_existe_procuracao.png")
        if self._validate_image_file(image_path):
            try:
                location = PyAutoGui.locateOnScreen(image_path, confidence=self.config.confidence)
                if location is not None:
                    message = "❌ Erro de procuração eletrônica detectado. Tentando novamente..."
                    print(message)
                    time.sleep(5)
                    self._double_click_image("ok.png", "botoes", silent=True)
                    PyAutoGui.press("Enter")
                    PyAutoGui.press("Esc")
                    # Lança exceção para que o for_each_with_retry tente novamente
                    raise Exception(f"Erro de procuração eletrônica: {message}")
            except Exception as e:
                # Se a exceção já foi nossa (do modal), re-lança para o retry
                if "Erro de procuração eletrônica" in str(e):
                    raise e
                # Se foi erro ao detectar o modal, ignora
                pass
                
        return RPAResult.SUCCESS
        
    def _searchSPEDFiscal(self) -> RPAResult:
        print("\nPesquisando arquivos de SPED Fiscal...")
        self._double_click_image("lupa.png", "botoes")
       
        self._selectOption("combo_sistema.png", "opcao_sped_fiscal.png", "comboboxes/sistema")
        self._selectOption("combo_arquivo.png", "opcao_escrituracao_fiscal_digital.png", "comboboxes/arquivo")

        self._single_click_image("checkbox.png", "checkboxes")

        PyAutoGui.press("Tab", presses=2, interval=0.2)

        json_manager = JSONManager()
        period = json_manager.get_params().get("period")
        start_date = DateFormatter.iso_to_ddmmyyyy(period["start_date"])
        end_date = DateFormatter.iso_to_ddmmyyyy(period["end_date"])

        print(f"Período: {start_date} a {end_date}")
        PyAutoGui.write(start_date, interval=0.1)
        PyAutoGui.press("Tab")
        PyAutoGui.write(end_date, interval=0.1)

        PyAutoGui.press("Tab")
        PyAutoGui.press("Space")

        self._single_click_image("pesquisar.png", "botoes")

        try:
            return self._dispatch_message_if_exists()
        except Exception as e:
            if str(e).startswith("Unfinish:"):
                raise e
            return RPAResult.ERROR

    def _searchSPEDContabil(self, start_date, end_date) -> RPAResult:
        print("\nPesquisando arquivos de SPED Contábil...")
        self._double_click_image("lupa.png", "botoes")
       
        self._selectOption("combo_sistema.png", "opcao_sped_contabil.png", "comboboxes/sistema")
        self._selectOption("combo_arquivo.png", "opcao_escrituracao_contabil_digital.png", "comboboxes/arquivo")

        json_manager = JSONManager()
        period = json_manager.get_params().get("period")
        start_date = DateFormatter.iso_to_ddmmyyyy(period["start_date"])
        end_date = DateFormatter.iso_to_ddmmyyyy(period["end_date"])

        print(f"Período: {start_date} a {end_date}")
        PyAutoGui.write(start_date, interval=0.1)
        PyAutoGui.press("Tab")
        PyAutoGui.write(end_date, interval=0.1)
        PyAutoGui.press("Enter")

        self._single_click_image("pesquisar.png", "botoes")

        try:
            return self._dispatch_message_if_exists()
        except Exception as e:
            if str(e).startswith("Unfinish:"):
                raise e
            return RPAResult.ERROR

    def search(self, tipo, start_date, end_date, is_first_iteration) -> RPAResult:
        self.set_confidence(0.9)
        
        if is_first_iteration:
            self._double_click_image("maximizar.png", "botoes")
            time.sleep(2)

        if tipo == "sped_contribuicoes":
            print("\nPesquisando arquivos de SPED Contribuições...")
            self._double_click_image("lupa.png", "botoes")

            if is_first_iteration:
                self._selectOption("combo_sistema.png", "opcao_sped_contribuicoes.png", "comboboxes/sistema")

            return self._searchSPED(start_date, end_date, is_first_iteration)
        elif tipo == "sped_ecf":
            print("\nPesquisando arquivos de SPED ECF...")
            self._double_click_image("lupa.png", "botoes")

            self._selectOption("combo_sistema.png", "opcao_sped_ecf.png", "comboboxes/sistema")

            return self._searchSPED(start_date, end_date, is_first_iteration)
        elif tipo == "sped_fiscal":
            return self._searchSPEDFiscal()
        elif tipo == "sped_contabil":
            return self._searchSPEDContabil(start_date, end_date)
        else:
            print(f"⚠ Tipo de pesquisa não reconhecido: {tipo}")
            return RPAResult.IMAGE_NOT_FOUND

    def _find_data_inicio_column(self, silent: bool = False) -> RPAResult:
        result = self._single_click_image("coluna_data_inicio.png", "tabelas", silent=True)
        
        if result == RPAResult.SUCCESS:
            if not silent:
                print("✅ Coluna 'Data Início' normal encontrada e clicada")
            return RPAResult.SUCCESS
        
        result = self._single_click_image("coluna_data_inicio_cortada.png", "tabelas", silent=True)
        
        if result == RPAResult.SUCCESS:
            if not silent:
                print("✅ Coluna 'Data Início' cortada encontrada e clicada")
            return RPAResult.SUCCESS
        
        if not silent:
            print("✗ Nenhuma versão da coluna 'Data Início' foi encontrada (nem normal nem cortada)")
        
        return RPAResult.IMAGE_NOT_FOUND

    def _single_click_image_filtered_by_column(self, image_filename: str, alias: str = "", silent: bool = False) -> RPAResult:
        max_y_range = 36
        
        column_image_path = self._get_image_path("tabelas", "coluna_data_inicio.png")
        column_image_path_cortada = self._get_image_path("tabelas", "coluna_data_inicio_cortada.png")
        
        if not self._validate_image_file(column_image_path) and not self._validate_image_file(column_image_path_cortada):
            if not silent:
                print(f"✗ Nenhum arquivo de referência encontrado: {column_image_path} ou {column_image_path_cortada}")
            return RPAResult.FILE_NOT_EXISTS
        
        try:
            column_locations = self._find_all_image_locations(column_image_path)
            
            if not column_locations and self._validate_image_file(column_image_path_cortada):
                if not silent:
                    print("⚠ Coluna normal não encontrada, tentando versão cortada...")
                column_locations = self._find_all_image_locations(column_image_path_cortada)
            
            if not column_locations:
                if not silent:
                    print("✗ Coluna de referência não encontrada na tela (nem normal nem cortada)")
                return RPAResult.IMAGE_NOT_FOUND
            
            column_center = PyAutoGui.center(column_locations[0])
            min_x = column_center.x - 47
            max_x = column_center.x + 47
            
            last_click_y = getattr(self, 'last_click_y', None)
            
            if last_click_y is None:
                min_y = None
                max_y = None
                if not silent:
                    print(f"🎯 Buscando {image_filename} no range X: [{min_x} - {max_x}], Y: sem filtro (primeira busca)")
            else:
                min_y = last_click_y + 1
                max_y = last_click_y + max_y_range
                if not silent:
                    print(f"🎯 Buscando {image_filename} no range X: [{min_x} - {max_x}], Y: [{min_y} - {max_y}]")
            
            image_path = self._get_image_path(alias, image_filename)
            
            if not self._validate_image_file(image_path):
                if not silent:
                    print(f"✗ Arquivo de imagem não encontrado: {image_path}")
                return RPAResult.FILE_NOT_EXISTS
            
            all_locations = self._find_all_image_locations(image_path)
            
            if not all_locations:
                if not silent:
                    print(f"✗ Imagem {image_filename} não encontrada na tela")
                return RPAResult.IMAGE_NOT_FOUND
            
            valid_locations = []
            for location in all_locations:
                center = PyAutoGui.center(location)
                x_valid = min_x <= center.x <= max_x
                
                if min_y is None and max_y is None:
                    y_valid = True
                else:
                    y_valid = min_y <= center.y <= max_y
                
                if x_valid and y_valid:
                    valid_locations.append((location, center))
            
            if not valid_locations:
                if min_y is not None and max_y is not None:
                    if not silent:
                        print(f"✗ Nenhuma ocorrência válida de {image_filename} encontrada no range Y: [{min_y} - {max_y}]")
                        
                        expanded_max_y = last_click_y + (max_y_range * 2)
                        print(f"🔍 Tentando range expandido Y: [{min_y} - {expanded_max_y}]")
                    
                    expanded_valid_locations = []
                    for location in all_locations:
                        center = PyAutoGui.center(location)
                        if (min_x <= center.x <= max_x and min_y <= center.y <= (last_click_y + (max_y_range * 2))):
                            expanded_valid_locations.append((location, center))
                    
                    if not expanded_valid_locations:
                        if not silent:
                            print(f"✗ Nenhuma ocorrência encontrada mesmo com range expandido")
                        return RPAResult.IMAGE_NOT_FOUND
                    else:
                        valid_locations = expanded_valid_locations
                        if not silent:
                            print(f"✅ Encontrada ocorrência no range expandido")
                else:
                    if not silent:
                        print(f"✗ Nenhuma ocorrência válida de {image_filename} encontrada no range X")
                    return RPAResult.IMAGE_NOT_FOUND
            
            valid_locations.sort(key=lambda item: item[1].y)
            
            if not silent:
                print(f"LOCATIONS: {len(valid_locations)}")
                print(f"VALID LOCATIONS: {valid_locations}")
            
            selected_location, selected_center = valid_locations[0]
            
            if not silent:
                print(f"SELECTED LOCATION: {selected_location}, CENTER: {selected_center}")
                print(f"✅ Clicando em {image_filename} na posição {selected_center}")
            
            self.last_click_y = selected_center.y
            
            PyAutoGui.click(selected_center)
            return RPAResult.SUCCESS
            
        except Exception as e:
            if not silent:
                print(f"✗ Erro ao clicar na data: {e}")
            return RPAResult.CLICK_FAILED

    def select_dates(self, range_dates) -> RPAResult:
        self.set_confidence(0.98)

        print("\nSelecionando arquivos...")
        
        if range_dates:
            self.reset_click_position()
            
            self._find_data_inicio_column(silent=True)
            
            time.sleep(1)
            
            print(f"\n🎯 Clicando em {len(range_dates)} datas solicitadas...")
            
            dates_clicked = 0

            for date in range_dates:
                if dates_clicked >= len(range_dates):
                    break

                print(f"  📅 Clicando na data: {date}")

                month = int(date.split("/")[1])
                period_file = f"01.{month:02d}.png"

                result = self._single_click_image_filtered_by_column(period_file, "tabelas", silent=True)

                if result == RPAResult.SUCCESS:
                    self._single_click_image("checkbox_linha_selecionada.png", "checkboxes")
                    dates_clicked += 1
                    print(f"    ✅ Data {date} clicada com sucesso.")
                    
                    if dates_clicked % 5 == 0:
                        for _ in range(15):
                            PyAutoGui.press("down")
                            time.sleep(0.1)
                        
                        self.reset_click_position()
                        print(f"    🔄 Posição Y resetada para buscar novas datas visíveis")
                else:
                    print(f"    ⚠️ Data {date} não encontrada.")
        else:
            self._single_click_image("checkbox_todos.png", "checkboxes")
            time.sleep(1)

        self._single_click_image("solicitar_arquivos.png", "botoes", silent=True)

        confirm_result = self._wait_for_image("modal_sucesso.png", "modais")

        if confirm_result == RPAResult.SUCCESS:
            time.sleep(2)
            PyAutoGui.press("enter")
            return RPAResult.SUCCESS
        else:
            return confirm_result
        
    def download_files(self) -> RPAResult:
        print("\nBaixando arquivos...")

        self._single_click_image("acompanhamento.png", "botoes")
        time.sleep(1)

        self._single_click_image("tab_ver_pedidos.png", "tabs")
        time.sleep(1)

        self._single_click_image("ultima_solicitacao.png", "tabelas")
        time.sleep(3)
        self._single_click_image("checkbox_todos.png", "checkboxes")
        time.sleep(3)
        self._single_click_image("baixar.png", "botoes")

        downloads_concluidos = self._wait_for_image("fila_de_downloads.png", "tabelas", timeout=60 * 5)

        if downloads_concluidos == RPAResult.SUCCESS:
            print("🎉 Todos os arquivos foram baixados com sucesso!")
            return RPAResult.SUCCESS
        else:
            print(f"❌ Falha no download dos arquivos: {downloads_concluidos.value}")
            return downloads_concluidos
