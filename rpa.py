import pyautogui as PyAutoGui
import time
import os
from typing import Tuple
from dataclasses import dataclass
from enum import Enum

from json_manager import JSONManager


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
    
    def _find_all_image_locations(self, image_path: str) -> list:
        try:
            locations = list(PyAutoGui.locateAllOnScreen(image_path, confidence=self.config.confidence))
            return locations
        except Exception as e:
            print(f"Erro ao procurar imagem: {e}")
            return []
    
    def _locate_and_double_click_image(self, image_path: str, description: str) -> RPAResult:
        try:
            all_locations = self._find_all_image_locations(image_path)
            
            if not all_locations:
                print(f"✗ Não foi possível localizar {description}")
                return RPAResult.IMAGE_NOT_FOUND
            
            if len(all_locations) == 1:
                location = all_locations[0]
                center = PyAutoGui.center(location)
                
                PyAutoGui.doubleClick(center, interval=self.config.double_click_interval)
                return RPAResult.SUCCESS
            
            else:
                print("  Múltiplas ocorrências encontradas:")
                for i, location in enumerate(all_locations, 1):
                    center = PyAutoGui.center(location)
                    print(f"    {i}. Posição: {center}")
                
                location = all_locations[0]
                center = PyAutoGui.center(location)
                
                PyAutoGui.doubleClick(center, interval=self.config.double_click_interval)
                return RPAResult.SUCCESS
                
        except Exception as e:
            print(f"✗ Erro ao tentar dar double click em {description}: {e}")
            return RPAResult.CLICK_FAILED

    def _locate_and_single_click_image(self, image_path: str, description: str) -> RPAResult:
        try:
            all_locations = self._find_all_image_locations(image_path)
            
            if not all_locations:
                print(f"✗ Não foi possível localizar {description}")
                return RPAResult.IMAGE_NOT_FOUND
            
            if len(all_locations) == 1:
                location = all_locations[0]
                center = PyAutoGui.center(location)
                
                PyAutoGui.click(center)
                return RPAResult.SUCCESS
            
            else:
                print("  Múltiplas ocorrências encontradas:")
                for i, location in enumerate(all_locations, 1):
                    center = PyAutoGui.center(location)
                    print(f"    {i}. Posição: {center}")
                
                location = all_locations[0]
                center = PyAutoGui.center(location)
                
                PyAutoGui.click(center)
                return RPAResult.SUCCESS
                
        except Exception as e:
            print(f"✗ Erro ao tentar dar click único em {description}: {e}")
            return RPAResult.CLICK_FAILED
    
    def _wait_with_countdown(self, seconds: int, message: str = "Iniciando...") -> None:
        print(f"{message} em {seconds} segundos...")

        for i in range(seconds, 0, -1):
            print(f"Aguardando: {i}")
            time.sleep(1)

        print("Iniciando...")

    def _wait_for_image(self, image_filename: str, alias: str = "", timeout: int = 30, check_interval: float = 1.0) -> RPAResult:
        image_path = self._get_image_path(alias, image_filename)
        
        if not self._validate_image_file(image_path):
            print(f"✗ Arquivo de imagem não encontrado: {image_path}")
            return RPAResult.FILE_NOT_EXISTS
        
        elapsed_time = 0.0
        
        while elapsed_time < timeout:
            try:
                location = PyAutoGui.locateOnScreen(image_path, confidence=self.config.confidence)
                
                if location is not None:
                    PyAutoGui.center(location)
                    return RPAResult.SUCCESS
                
                print(f"⏳ Aguardando... ({elapsed_time:.1f}s/{timeout}s)")
                time.sleep(check_interval)
                elapsed_time += check_interval
                
            except Exception as e:
                print(f"⚠ Erro durante a busca: {e}")
                time.sleep(check_interval)
                elapsed_time += check_interval
        
        print(f"✗ Timeout: Imagem {image_filename} não foi encontrada em {timeout} segundos")
        return RPAResult.IMAGE_NOT_FOUND
    
    def _single_click_image(self, image_filename: str, alias: str = "") -> RPAResult:
        image_path = self._get_image_path(alias, image_filename)

        if not self._validate_image_file(image_path):
            print(f"✗ Arquivo de imagem não encontrado: {image_path}")
            return RPAResult.FILE_NOT_EXISTS
        
        result = self._locate_and_single_click_image(image_path, f"imagem ({image_filename})")
        
        if result == RPAResult.CLICK_FAILED:
            print("✗ Falha ao executar o click único")
        elif result == RPAResult.IMAGE_NOT_FOUND:
            print(f"⚠ Imagem {image_filename} não encontrada na tela")
        
        return result

    def _double_click_image(self, icon_filename: str = "icon.png", alias: str = "") -> RPAResult:
        self._wait_with_countdown(self.config.startup_delay, "Procurando ícone no desktop")
        
        image_path = self._get_image_path(alias, icon_filename)
        
        if not self._validate_image_file(image_path):
            print(f"✗ Arquivo de imagem não encontrado: {image_path}")
            return RPAResult.FILE_NOT_EXISTS
        
        result = self._locate_and_double_click_image(image_path, f"ícone ({icon_filename})")
        
        if result == RPAResult.CLICK_FAILED:
            print("✗ Falha ao executar o double click")
        elif result == RPAResult.IMAGE_NOT_FOUND:
            print("⚠ Ícone não encontrado na tela")
        
        return result

    def init(self) -> RPAResult:
        print("\nAbrindo o ReceitanetBX...")
        wait_result = self._wait_for_image("icon.png", "botoes", timeout=10)
        
        if wait_result == RPAResult.SUCCESS:
            return self._double_click_image("icon.png", "botoes")
        else:
            print(f"\n❌ ERRO: {wait_result.value}")
            return wait_result

    def login_por_certificado(self) -> RPAResult:
        print("\nSelecionando o certificado digital...")

        json_manager = JSONManager()
        settings = json_manager.get_settings()
        certificado = settings.get("certificado", "cert.png")
        
        print(f"Usando certificado: {certificado}")
        self._wait_for_image(f"{certificado}.png", "certificados", timeout=120)
        self._single_click_image(f"{certificado}.png", "certificados")

        print("\nSelecionando o perfil...")
        self._single_click_image("combo_perfil.png", "comboboxes/perfil")
        return self._single_click_image("opcao_procurador.png", "comboboxes/perfil")

    def typeCNPJ(self, cnpj) -> RPAResult:
        print(f"\nDigitando CNPJ: {cnpj}...")
        self._single_click_image("combo_tipo_doc.png", "comboboxes/tipo_doc")
        self._single_click_image("opcao_cnpj.png", "comboboxes/tipo_doc")
        self._single_click_image("cnpj_input.png", "inputs")
        
        PyAutoGui.write(cnpj, interval=0.1)
        time.sleep(1)

        print("\nEntrando no sistema...")
        return self._single_click_image("entrar.png", "botoes")
    
    def search(self, start_date: str = "01012020", end_date: str = "31122024") -> RPAResult:
        print("\nPesquisando arquivos...")
        time.sleep(1)
        self._single_click_image("lupa.png", "botoes")

        self._selectOption("combo_sistema.png", "opcao_sped_contribuicoes.png", "comboboxes/sistema")
        self._selectOption("combo_arquivo.png", "opcao_escrituracao.png", "comboboxes/arquivo")
        self._selectOption("combo_pesquisa.png", "opcao_periodo_escrituracao.png", "comboboxes/pesquisa")

        PyAutoGui.write(start_date, interval=0.1)
        PyAutoGui.press("Tab")
        PyAutoGui.write(end_date, interval=0.1)
        PyAutoGui.press("Enter")

        return self._single_click_image("pesquisar.png", "botoes")

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
        