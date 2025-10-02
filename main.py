import pyautogui as pay
import time
import os
from typing import Tuple
from dataclasses import dataclass
from enum import Enum


class RPAResult(Enum):
    SUCCESS = "success"
    IMAGE_NOT_FOUND = "image_not_found"
    FILE_NOT_EXISTS = "file_not_exists"
    CLICK_FAILED = "click_failed"


@dataclass
class RPAConfig:
    confidence: float = 0.9  # Aumentando a confiança para ser mais preciso
    double_click_interval: float = 0.1
    startup_delay: int = 3
    images_folder: str = "images"
    preview_mode: bool = False  # Modo para mostrar todas as ocorrências encontradas


class DesktopRPA:
    def __init__(self, config: RPAConfig = None):
        self.config = config or RPAConfig()
        self._setup_pyautogui()
    
    def _setup_pyautogui(self) -> None:
        pay.FAILSAFE = True
        pay.PAUSE = 0.1
    
    def _get_image_path(self, filename: str) -> str:
        return os.path.join(self.config.images_folder, filename)
    
    def _validate_image_file(self, image_path: str) -> bool:
        return os.path.exists(image_path)
    
    def _find_all_image_locations(self, image_path: str) -> list:
        try:
            locations = list(pay.locateAllOnScreen(image_path, confidence=self.config.confidence))
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
            
            print(f"🔍 Encontradas {len(all_locations)} ocorrência(s) de {description}:")
            
            if len(all_locations) == 1:
                location = all_locations[0]
                center = pay.center(location)
                print(f"  Posição única encontrada: {center}")
                
                pay.doubleClick(center, interval=self.config.double_click_interval)
                print(f"✓ Double click realizado em {description}")
                return RPAResult.SUCCESS
            
            else:
                print("  Múltiplas ocorrências encontradas:")
                for i, location in enumerate(all_locations, 1):
                    center = pay.center(location)
                    print(f"    {i}. Posição: {center}")
                
                location = all_locations[0]
                center = pay.center(location)
                print(f"  🎯 Clicando na primeira ocorrência: {center}")
                
                pay.doubleClick(center, interval=self.config.double_click_interval)
                print(f"✓ Double click realizado em {description}")
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
            
            print(f"🔍 Encontradas {len(all_locations)} ocorrência(s) de {description}:")
            
            if len(all_locations) == 1:
                location = all_locations[0]
                center = pay.center(location)
                print(f"  Posição única encontrada: {center}")
                
                pay.click(center)
                print(f"✓ Click único realizado em {description}")
                return RPAResult.SUCCESS
            
            else:
                print("  Múltiplas ocorrências encontradas:")
                for i, location in enumerate(all_locations, 1):
                    center = pay.center(location)
                    print(f"    {i}. Posição: {center}")
                
                location = all_locations[0]
                center = pay.center(location)
                print(f"  🎯 Clicando na primeira ocorrência: {center}")
                
                pay.click(center)
                print(f"✓ Click único realizado em {description}")
                return RPAResult.SUCCESS
                
        except Exception as e:
            print(f"✗ Erro ao tentar dar click único em {description}: {e}")
            return RPAResult.CLICK_FAILED
    
    def _wait_with_countdown(self, seconds: int, message: str = "Iniciando automação") -> None:
        print(f"{message} em {seconds} segundos...")

        for i in range(seconds, 0, -1):
            print(f"Aguardando: {i}")
            time.sleep(1)

        print("Iniciando...")
    
    def wait_for_image(self, image_filename: str, timeout: int = 30, check_interval: float = 1.0) -> RPAResult:
        image_path = self._get_image_path(image_filename)
        
        if not self._validate_image_file(image_path):
            print(f"✗ Arquivo de imagem não encontrado: {image_path}")
            return RPAResult.FILE_NOT_EXISTS
        
        elapsed_time = 0.0
        
        while elapsed_time < timeout:
            try:
                # Tenta localizar a imagem na tela
                location = pay.locateOnScreen(image_path, confidence=self.config.confidence)
                
                if location is not None:
                    center = pay.center(location)
                    print(f"✓ Imagem {image_filename} encontrada após {elapsed_time:.1f}s na posição: {center}")
                    return RPAResult.SUCCESS
                
                # Se não encontrou, aguarda o intervalo especificado
                print(f"⏳ Aguardando... ({elapsed_time:.1f}s/{timeout}s)")
                time.sleep(check_interval)
                elapsed_time += check_interval
                
            except Exception as e:
                print(f"⚠ Erro durante a busca: {e}")
                time.sleep(check_interval)
                elapsed_time += check_interval
        
        print(f"✗ Timeout: Imagem {image_filename} não foi encontrada em {timeout} segundos")
        return RPAResult.IMAGE_NOT_FOUND
    
    def single_click_image(self, image_filename: str) -> RPAResult:
        image_path = self._get_image_path(image_filename)
        
        if not self._validate_image_file(image_path):
            print(f"✗ Arquivo de imagem não encontrado: {image_path}")
            return RPAResult.FILE_NOT_EXISTS
        
        result = self._locate_and_single_click_image(image_path, f"imagem ({image_filename})")
        
        if result == RPAResult.CLICK_FAILED:
            print("✗ Falha ao executar o click único")
        elif result == RPAResult.IMAGE_NOT_FOUND:
            print(f"⚠ Imagem {image_filename} não encontrada na tela. Verifique se:")
        
        return result

    def double_click_image(self, icon_filename: str = "icon.png") -> RPAResult:
        self._wait_with_countdown(self.config.startup_delay, "Procurando ícone no desktop")
        
        image_path = self._get_image_path(icon_filename)
        
        if not self._validate_image_file(image_path):
            print(f"✗ Arquivo de imagem não encontrado: {image_path}")
            return RPAResult.FILE_NOT_EXISTS
        
        
        result = self._locate_and_double_click_image(image_path, f"ícone ({icon_filename})")
        
        if result == RPAResult.CLICK_FAILED:
            print("✗ Falha ao executar o double click")
        elif result == RPAResult.IMAGE_NOT_FOUND:
            print("⚠ Ícone não encontrado na tela. Verifique se:")
        
        return result


def main():
    config = RPAConfig(
        confidence=0.9,           # Confiança alta para ser mais preciso
        double_click_interval=0.1, # Intervalo entre os cliques do double click
        startup_delay=3,          # Tempo de espera antes de iniciar
        images_folder="images",   # Pasta onde estão as imagens
        preview_mode=False        # Desabilitado por padrão
    )
    
    rpa = DesktopRPA(config)
    
    # Exemplo usando wait_for_image para aguardar o ícone aparecer
    print("\n✓ PASSO 1: Abrindo o ReceitanetBX...")
    wait_for_receitanetbx_icon = rpa.wait_for_image("icon.png", timeout=10)
    
    if wait_for_receitanetbx_icon == RPAResult.SUCCESS:
        rpa.double_click_image("icon.png")
        
        print("\n✓ PASSO 2: Selecionando o certificado digital...")
        rpa.wait_for_image("cert.png", timeout=120)
        rpa.single_click_image("cert.png")

        print("\n✓ PASSO 3: Selecionando o perfil...")
        rpa.wait_for_image("combo_perfil.png", timeout=10)
        rpa.single_click_image("combo_perfil.png")

        rpa.wait_for_image("opcao_procurador.png", timeout=10)
        rpa.single_click_image("opcao_procurador.png")

        print("\n✓ PASSO 4: Inserindo CNPJ da empresa...")
        rpa.wait_for_image("combo_tipo_doc.png", timeout=10)
        rpa.single_click_image("combo_tipo_doc.png")

        rpa.wait_for_image("opcao_cnpj.png", timeout=10)
        rpa.single_click_image("opcao_cnpj.png")

        print("\n✓ PASSO 5: Digitando CNPJ da empresa...")
        rpa.wait_for_image("cnpj_input.png", timeout=10)
        rpa.single_click_image("cnpj_input.png")
        pay.write("06097786000193", interval=0.1)

        time.sleep(1)
                
        print("\n✓ PASSO 6: Entrando no sistema...")
        rpa.wait_for_image("entrar.png", timeout=10)
        rpa.single_click_image("entrar.png")
                
    else:
        print(f"\n❌ ERRO: {wait_for_receitanetbx_icon.value}")


if __name__ == "__main__":
    main()
