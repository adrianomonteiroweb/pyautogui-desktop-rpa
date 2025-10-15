from datetime import date
import pyautogui as PyAutoGui
import time
import os
from typing import Tuple
from dataclasses import dataclass
from enum import Enum

from json_manager import JSONManager
from date_formatter import DateFormatter
from easyocr_manager import EasyOCRManager


class RPAResult(Enum):
    SUCCESS = "success"
    IMAGE_NOT_FOUND = "image_not_found"
    FILE_NOT_EXISTS = "file_not_exists"
    CLICK_FAILED = "click_failed"


@dataclass
class RPAConfig:
    confidence: float = 0.9
    double_click_interval: float = 0.1
    startup_delay: int = 3
    images_folder: str = "images"
    preview_mode: bool = False


class RPA:
    def __init__(self, config: RPAConfig = None):
        self.config = config or RPAConfig()
        self.desktop_rpa = None
        self._setup_pyautogui()
    
    def _setup_pyautogui(self) -> None:
        PyAutoGui.FAILSAFE = True
        PyAutoGui.PAUSE = 0.1
    
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
            # Tenta primeiro com confidence padrão
            all_locations = self._find_all_image_locations(image_path)
            
            # Se não encontrar, tenta com confidence menor
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
            # Tenta primeiro com confidence padrão
            all_locations = self._find_all_image_locations(image_path)
            
            # Se não encontrar, tenta com confidence menor
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
                
                # Se já passou da metade do tempo e ainda não tentou com menor confidence
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

    def _single_click_image_filter_positions(self, image_filename: str, min_x: int = None, max_x: int = None, 
                                           min_y: int = None, max_y: int = None, alias: str = "", 
                                           silent: bool = False) -> RPAResult:
        """
        Clica na primeira ocorrência da imagem que estiver dentro dos ranges de coordenadas especificados.
        
        Args:
            image_filename: Nome do arquivo de imagem
            min_x: Posição X mínima (None = sem limite mínimo)
            max_x: Posição X máxima (None = sem limite máximo)
            min_y: Posição Y mínima (None = sem limite mínimo)
            max_y: Posição Y máxima (None = sem limite máximo)
            alias: Pasta da imagem
            silent: Se True, suprime mensagens de debug
            
        Returns:
            RPAResult: Resultado da operação
        """
        image_path = self._get_image_path(alias, image_filename)

        if not self._validate_image_file(image_path):
            if not silent:
                print(f"✗ Arquivo de imagem não encontrado: {image_path}")
            return RPAResult.FILE_NOT_EXISTS

        try:
            # Busca todas as ocorrências da imagem
            all_locations = self._find_all_image_locations(image_path)
            
            # Se não encontrar com confidence padrão, tenta com menor
            if not all_locations and self.config.confidence > 0.6:
                if not silent:
                    print(f"⚠ Tentando com menor precisão para {image_filename}...")
                all_locations = self._find_all_image_locations(image_path, confidence=0.6)
            
            if not all_locations:
                if not silent:
                    print(f"✗ Não foi possível localizar {image_filename}")
                return RPAResult.IMAGE_NOT_FOUND
            
            # Filtra as localizações que estão dentro dos ranges especificados
            filtered_locations = []
            for location in all_locations:
                center = PyAutoGui.center(location)
                x, y = center
                
                # Verifica se está dentro dos limites X
                if min_x is not None and x < min_x:
                    continue
                if max_x is not None and x > max_x:
                    continue
                    
                # Verifica se está dentro dos limites Y
                if min_y is not None and y < min_y:
                    continue
                if max_y is not None and y > max_y:
                    continue
                
                filtered_locations.append((location, center))
            
            if not filtered_locations:
                if not silent:
                    filter_info = f"X: [{min_x or '∞'}-{max_x or '∞'}], Y: [{min_y or '∞'}-{max_y or '∞'}]"
                    print(f"✗ Nenhuma ocorrência de {image_filename} encontrada nos ranges especificados: {filter_info}")
                    print(f"  Ocorrências totais encontradas: {len(all_locations)}")
                    for i, location in enumerate(all_locations, 1):
                        center = PyAutoGui.center(location)
                        print(f"    {i}. Posição: {center}")
                return RPAResult.IMAGE_NOT_FOUND
            
            # Clica na primeira ocorrência dentro dos ranges
            location, center = filtered_locations[0]
            
            if not silent:
                filter_info = f"X: [{min_x or '∞'}-{max_x or '∞'}], Y: [{min_y or '∞'}-{max_y or '∞'}]"
                print(f"✅ Clicando em {image_filename} na posição {center} (dentro dos ranges {filter_info})")
                if len(filtered_locations) > 1:
                    print(f"  Outras {len(filtered_locations)-1} ocorrências encontradas nos ranges:")
                    for i, (_, other_center) in enumerate(filtered_locations[1:], 2):
                        print(f"    {i}. Posição: {other_center}")
            
            PyAutoGui.click(center)
            return RPAResult.SUCCESS
            
        except Exception as e:
            if not silent:
                print(f"✗ Erro ao tentar dar click único em {image_filename}: {e}")
            return RPAResult.CLICK_FAILED

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
        wait_result = self._wait_for_image("icon.png", "botoes", timeout=10)
        
        if wait_result == RPAResult.SUCCESS:
            return self._double_click_image("icon.png", "botoes")
        else:
            print(f"\n❌ ERRO: {wait_result.value}")
            return wait_result
        
    def close(self) -> None:
        time.sleep(5)
        print("\nFechando o ReceitanetBX...")
        
        # Tenta múltiplas estratégias para fechar o programa
        close_buttons = [
            ("sair.png", "botoes"),
            ("fechar.png", "botoes"),
            ("fechar2.png", "botoes"),
        ]
        
        for button_file, button_alias in close_buttons:
            result = self._single_click_image(button_file, button_alias, silent=True)
            
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
        botao_entrar = self._wait_for_image("entrar.png", "botoes", timeout=5)

        if botao_entrar != RPAResult.SUCCESS:
            self._double_click_image("icone_trocar_perfil.png", "botoes")

        self._selecionar_certificado()

        if first_time:
            self._single_click_image("combo_perfil_contribuinte.png", "comboboxes/perfil")
            self._single_click_image("opcao_procurador.png", "comboboxes/perfil")
        else:
            self._single_click_image("combo_perfil_procurador.png", "comboboxes/perfil")
            self._double_click_image("opcao_receita_federal.png", "comboboxes/perfil")
            time.sleep(1)
            self._single_click_image("combo_perfil_receita_federal.png", "comboboxes/perfil")
            self._single_click_image("opcao_procurador.png", "comboboxes/perfil")

        self._selectOption("combo_tipo_doc.png", "opcao_cnpj.png", "comboboxes/tipo_doc")
        self._single_click_image("cnpj_input.png", "inputs")
        
        PyAutoGui.write(cnpj, interval=0.1)

        # Tenta encontrar primeiro o botão "entrar"
        botao_entrar = self._wait_for_image("entrar.png", "botoes", timeout=5)

        if botao_entrar == RPAResult.SUCCESS:
            return self._single_click_image("entrar.png", "botoes")
        
        # Se não encontrou "entrar", tenta encontrar "trocar_perfil"
        botao_trocar_perfil = self._wait_for_image("trocar_perfil.png", "botoes", timeout=5)
        
        if botao_trocar_perfil == RPAResult.SUCCESS:
            return self._single_click_image("trocar_perfil.png", "botoes")
        
        # Se nenhuma das duas imagens foi encontrada, retorna erro
        print("✗ Nenhuma das imagens foi encontrada: entrar.png ou trocar_perfil.png")
        return RPAResult.IMAGE_NOT_FOUND

    def _searchSPED(self, start_date, end_date) -> RPAResult:
        self._selectOption("combo_arquivo.png", "opcao_escrituracao.png", "comboboxes/arquivo")
        self._selectOption("combo_pesquisa.png", "opcao_periodo_escrituracao.png", "comboboxes/pesquisa")

        print(f"Buscando arquivos no período entre {start_date} e {end_date}...")
        PyAutoGui.write(start_date, interval=0.1)
        PyAutoGui.press("Tab")
        PyAutoGui.write(end_date, interval=0.1)
        PyAutoGui.press("Enter")

        self._single_click_image("pesquisar.png", "botoes")

        return self._dispatch_message_if_exists()
        
    def _dispatch_message_if_exists(self) -> RPAResult:
        time.sleep(3)
        
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
            except:
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
                    PyAutoGui.press("Enter")
                    # Lança exceção com mensagem "Unfinish" para o loop entender que deve pular
                    raise Exception("Unfinish: " + message)
            except:
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

        return self._dispatch_message_if_exists()

    def _searchSPEDContabil(self, start_date, end_date) -> RPAResult:
        print("\nPesquisando arquivos de SPED Contábil...")
        self._double_click_image("lupa.png", "botoes")
       
        self._selectOption("combo_sistema.png", "opcao_sped_contabil.png", "comboboxes/sistema")
        self._selectOption("combo_arquivo.png", "opcao_escrituracao_contabil_digital.png", "comboboxes/arquivo")

        print(f"Período: {start_date} a {end_date}")
        PyAutoGui.write(start_date, interval=0.1)
        PyAutoGui.press("Tab")
        PyAutoGui.write(end_date, interval=0.1)
        PyAutoGui.press("Enter")

        self._single_click_image("pesquisar.png", "botoes")

        return self._dispatch_message_if_exists()

    def search(self, tipo, start_date, end_date, is_first_iteration=True) -> RPAResult:
        if is_first_iteration:
            self._double_click_image("maximizar.png", "botoes")
            time.sleep(2)

        if tipo == "sped_contribuicoes":
            print("\nPesquisando arquivos de SPED Contribuições...")
            self._double_click_image("lupa.png", "botoes")

            self._selectOption("combo_sistema.png", "opcao_sped_contribuicoes.png", "comboboxes/sistema")

            return self._searchSPED(start_date, end_date)
        elif tipo == "sped_ecf":
            print("\nPesquisando arquivos de SPED ECF...")
            self._double_click_image("lupa.png", "botoes")

            self._selectOption("combo_sistema.png", "opcao_sped_ecf.png", "comboboxes/sistema")

            return self._searchSPED(start_date, end_date)
        elif tipo == "sped_fiscal":
            return self._searchSPEDFiscal()
        elif tipo == "sped_contabil":
            return self._searchSPEDContabil(start_date, end_date)
        else:
            print(f"⚠ Tipo de pesquisa não reconhecido: {tipo}")
            return RPAResult.IMAGE_NOT_FOUND

    def _single_click_image_filtered_by_column(self, image_filename: str, alias: str = "", silent: bool = False) -> RPAResult:
        """
        Método simplificado que filtra por range de 47 pixels e posição Y > último click.
        Baseado na lógica do teste test_click_dates_01_to_11.py
        
        Args:
            image_filename: Nome do arquivo de imagem a ser clicado
            alias: Pasta da imagem
            silent: Se True, suprime mensagens de debug
            
        Returns:
            RPAResult: Resultado da operação
        """
        # Localiza a coluna de referência
        column_image_path = self._get_image_path("tabelas", "coluna_data_inicio.png")
        
        if not self._validate_image_file(column_image_path):
            if not silent:
                print(f"✗ Arquivo de referência não encontrado: {column_image_path}")

            return RPAResult.FILE_NOT_EXISTS
        
        try:
            # Busca a posição da coluna de referência
            column_locations = self._find_all_image_locations(column_image_path)
            
            if not column_locations:
                if not silent:
                    print("✗ Coluna de referência não encontrada na tela")

                return RPAResult.IMAGE_NOT_FOUND
            
            # Define o range de X (±47 pixels da coluna)
            column_center = PyAutoGui.center(column_locations[0])
            min_x = column_center.x - 47
            max_x = column_center.x + 47
            
            if not silent:
                print(f"🎯 Buscando {image_filename} no range X: [{min_x} - {max_x}], Y > {getattr(self, 'last_click_y', 0)}")
            
            # Busca a imagem da data
            image_path = self._get_image_path(alias, image_filename)
            
            if not self._validate_image_file(image_path):
                if not silent:
                    print(f"✗ Arquivo de imagem não encontrado: {image_path}")

                return RPAResult.FILE_NOT_EXISTS
            
            # Encontra todas as ocorrências da imagem
            all_locations = self._find_all_image_locations(image_path)
            
            if not all_locations:
                if not silent:
                    print(f"✗ Imagem {image_filename} não encontrada na tela")

                return RPAResult.IMAGE_NOT_FOUND
            
            # Filtra por range X e Y > último click
            valid_locations = []

            last_y = getattr(self, 'last_click_y', 0)
            
            for location in all_locations:
                center = PyAutoGui.center(location)

                if (min_x <= center.x <= max_x and center.y > last_y):
                    valid_locations.append((location, center))
            
            if not valid_locations:
                if not silent:
                    print(f"✗ Nenhuma ocorrência válida de {image_filename} encontrada")

                return RPAResult.IMAGE_NOT_FOUND
            
            # Ordena por Y (menor Y primeiro - mais acima na tela)
            valid_locations.sort(key=lambda item: item[1].y)
            
            # Seleciona a primeira posição válida (menor Y)
            selected_location, selected_center = valid_locations[0]
            
            if not silent:
                print(f"✅ Clicando em {image_filename} na posição {selected_center}")
            
            # Atualiza a posição Y do último click
            self.last_click_y = selected_center.y
            
            # Executa o clique
            PyAutoGui.click(selected_center)

            return RPAResult.SUCCESS
            
        except Exception as e:
            if not silent:
                print(f"✗ Erro ao clicar na data: {e}")
            return RPAResult.CLICK_FAILED



    def select_dates(self, range_dates) -> RPAResult:
        print("\nSelecionando arquivos...")
        
        if range_dates:
            self.last_click_y = 0
            
            self._single_click_image("coluna_data_inicio.png", "tabelas")
            time.sleep(1)
            self._single_click_image("coluna_transmissao.png", "tabelas")
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
                    time.sleep(1)
                    self._single_click_image("checkbox_linha_selecionada.png", "checkboxes")
                    time.sleep(1)

                    dates_clicked += 1

                    print(f"    ✅ Data {date} clicada com sucesso.")
                else:
                    print(f"    ⚠️ Data {date} não encontrada.")
            
            print(f"\n📊 {dates_clicked} datas clicadas com sucesso")
            time.sleep(60)
        else:
            self._single_click_image("checkbox_todos.png", "checkboxes")
            time.sleep(1)

        self._single_click_image("solicitar_arquivos.png", "botoes")

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
        self._single_click_image("ultima_solicitacao.png", "tabelas")
        time.sleep(2)
        self._single_click_image("checkbox_todos.png", "checkboxes")
        time.sleep(3)
        self._single_click_image("baixar.png", "botoes")
        time.sleep(3)

        downloads_concluidos = self._wait_for_image("fila_de_downloads.png", "tabelas", timeout=60 * 5)

        if downloads_concluidos == RPAResult.SUCCESS:
            print("🎉 Todos os arquivos foram baixados com sucesso!")
            return RPAResult.SUCCESS
        else:
            print(f"❌ Falha no download dos arquivos: {downloads_concluidos.value}")
            return downloads_concluidos
