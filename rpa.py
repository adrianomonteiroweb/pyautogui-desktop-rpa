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
        cert_wait_result = self._wait_for_image(f"{certificado}.png", "certificados", timeout=120)
        
        if cert_wait_result != RPAResult.SUCCESS:
            return cert_wait_result
            
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
        time.sleep(1)

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
    
    def _searchSPED(self) -> RPAResult:
        self._selectOption("combo_arquivo.png", "opcao_escrituracao.png", "comboboxes/arquivo")
        self._selectOption("combo_pesquisa.png", "opcao_periodo_escrituracao.png", "comboboxes/pesquisa")

        json_manager = JSONManager()
        period = json_manager.get_params().get("period")
        start_date = DateFormatter.iso_to_ddmmyyyy(period["start_date"])
        end_date = DateFormatter.iso_to_ddmmyyyy(period["end_date"])

        print(f"Buscando arquivos no período entre {start_date} e {end_date}...")
        PyAutoGui.write(start_date, interval=0.1)
        PyAutoGui.press("Tab")
        PyAutoGui.write(end_date, interval=0.1)
        PyAutoGui.press("Enter")

        self._single_click_image("pesquisar.png", "botoes")

        return self._dispatch_message_if_exists()
        
    def _dispatch_message_if_exists(self) -> RPAResult:
        time.sleep(5)
        result = self._wait_for_image("modal_sem_resultados.png", "modais", timeout=1)

        if result == RPAResult.SUCCESS:
            message = "⚠ Nenhum arquivo foi encontrado para o critério de pesquisa solicitado."
            print(message)
            time.sleep(1)
            self._double_click_image("ok.png", "botoes", silent=True)
            PyAutoGui.press("Enter")
            # Lança exceção com mensagem "Unfinish" para o loop entender que deve pular
            raise Exception("Unfinish: " + message)
        else:
            # Verifica se existe o modal de nenhum arquivo encontrado
            result_nenhum_arquivo = self._wait_for_image("modal_nenhum_arquivo_encontrado.png", "modais", timeout=10)
            
            if result_nenhum_arquivo == RPAResult.SUCCESS:
                message = "⚠ Nenhum arquivo encontrado correspondente a busca."
                print(message)
                time.sleep(1)
                self._double_click_image("ok.png", "botoes", silent=True)
                PyAutoGui.press("Enter")
                # Lança exceção com mensagem "Unfinish" para o loop entender que deve pular
                raise Exception("Unfinish: " + message)
            else:
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
    
    def _searchSPEDContabil(self) -> RPAResult:
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

        return self._dispatch_message_if_exists()
        
    def search(self, tipo) -> RPAResult:
        self._double_click_image("maximizar.png", "botoes")
        time.sleep(2)

        if tipo == "sped_contribuicoes":
            print("\nPesquisando arquivos de SPED Contribuições...")
            self._double_click_image("lupa.png", "botoes")

            self._selectOption("combo_sistema.png", "opcao_sped_contribuicoes.png", "comboboxes/sistema")

            return self._searchSPED()
        elif tipo == "sped_ecf":
            print("\nPesquisando arquivos de SPED ECF...")
            self._double_click_image("lupa.png", "botoes")

            self._selectOption("combo_sistema.png", "opcao_sped_ecf.png", "comboboxes/sistema")

            return self._searchSPED()
        elif tipo == "sped_fiscal":
            return self._searchSPEDFiscal()
        elif tipo == "sped_contabil":
            return self._searchSPEDContabil()
        else:
            print(f"⚠ Tipo de pesquisa não reconhecido: {tipo}")
            return RPAResult.IMAGE_NOT_FOUND

    def request_files(self, range_dates) -> RPAResult:
        print("\nSelecionando arquivos...")
        
        if range_dates:
            # Inicializa o EasyOCR Manager
            ocr_manager = EasyOCRManager()
            
            # Clica na coluna de data início para ordenar
            self._single_click_image("coluna_data_inicio.png", "tabelas")
            time.sleep(1)
            self._single_click_image("coluna_transmissao.png", "tabelas")
            time.sleep(1)
            
            # Processa cada data na lista
            for i, date in enumerate(range_dates):
                # Usa EasyOCR para encontrar e clicar na data
                success = ocr_manager.click_best_date_match(date)
                
                if success:
                    self._single_click_image("checkbox_linha_selecionada.png", "checkboxes")
                else:
                    print(f"Não encontrado arquivo no período: {date}")
                    
                # Aguarda 3 segundos antes da próxima data (exceto na última)
                if i < len(range_dates) - 1:
                    time.sleep(1)
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
