import pyautogui as pay
import time
import os
from typing import Tuple
from dataclasses import dataclass
from enum import Enum


class AutomationResult(Enum):
    SUCCESS = "success"
    IMAGE_NOT_FOUND = "image_not_found"
    FILE_NOT_EXISTS = "file_not_exists"
    CLICK_FAILED = "click_failed"


@dataclass
class AutomationConfig:
    confidence: float = 0.9  # Aumentando a confiança para ser mais preciso
    double_click_interval: float = 0.1
    startup_delay: int = 3
    images_folder: str = "images"
    preview_mode: bool = False  # Modo para mostrar todas as ocorrências encontradas


class DesktopIconAutomation:
    def __init__(self, config: AutomationConfig = None):
        self.config = config or AutomationConfig()
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
    
    def _locate_and_double_click_image(self, image_path: str, description: str) -> AutomationResult:
        try:
            all_locations = self._find_all_image_locations(image_path)
            
            if not all_locations:
                print(f"✗ Não foi possível localizar {description}")
                return AutomationResult.IMAGE_NOT_FOUND
            
            print(f"🔍 Encontradas {len(all_locations)} ocorrência(s) de {description}:")
            
            if len(all_locations) == 1:
                location = all_locations[0]
                center = pay.center(location)
                print(f"  Posição única encontrada: {center}")
                
                pay.doubleClick(center, interval=self.config.double_click_interval)
                print(f"✓ Double click realizado em {description}")
                return AutomationResult.SUCCESS
            
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
                return AutomationResult.SUCCESS
                
        except Exception as e:
            print(f"✗ Erro ao tentar dar double click em {description}: {e}")
            return AutomationResult.CLICK_FAILED

    def _locate_and_single_click_image(self, image_path: str, description: str) -> AutomationResult:
        try:
            all_locations = self._find_all_image_locations(image_path)
            
            if not all_locations:
                print(f"✗ Não foi possível localizar {description}")
                return AutomationResult.IMAGE_NOT_FOUND
            
            print(f"🔍 Encontradas {len(all_locations)} ocorrência(s) de {description}:")
            
            if len(all_locations) == 1:
                location = all_locations[0]
                center = pay.center(location)
                print(f"  Posição única encontrada: {center}")
                
                pay.click(center)
                print(f"✓ Click único realizado em {description}")
                return AutomationResult.SUCCESS
            
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
                return AutomationResult.SUCCESS
                
        except Exception as e:
            print(f"✗ Erro ao tentar dar click único em {description}: {e}")
            return AutomationResult.CLICK_FAILED
    
    def _wait_with_countdown(self, seconds: int, message: str = "Iniciando automação") -> None:
        print(f"{message} em {seconds} segundos...")

        for i in range(seconds, 0, -1):
            print(f"Aguardando: {i}")
            time.sleep(1)

        print("Iniciando...")
    
    def single_click_image(self, image_filename: str) -> AutomationResult:
        print(f"\n=== AUTOMAÇÃO DE CLICK ÚNICO NA IMAGEM {image_filename.upper()} ===")
        
        image_path = self._get_image_path(image_filename)
        
        if not self._validate_image_file(image_path):
            print(f"✗ Arquivo de imagem não encontrado: {image_path}")
            return AutomationResult.FILE_NOT_EXISTS
        
        print(f"Procurando pela imagem: {image_filename}")
        print(f"Caminho da imagem: {image_path}")
        
        result = self._locate_and_single_click_image(image_path, f"imagem ({image_filename})")
        
        if result == AutomationResult.SUCCESS:
            print(f"✓ Click único na imagem {image_filename} executado com sucesso!")
        elif result == AutomationResult.IMAGE_NOT_FOUND:
            print(f"⚠ Imagem {image_filename} não encontrada na tela. Verifique se:")
            print("  - A imagem está visível na tela")
            print(f"  - O arquivo {image_filename} corresponde ao elemento atual")
            print("  - A resolução da tela não mudou")
        else:
            print("✗ Falha ao executar o click único")
        
        return result

    def double_click_desktop_icon(self, icon_filename: str = "icon.png") -> AutomationResult:
        self._wait_with_countdown(self.config.startup_delay, "Procurando ícone no desktop")
        
        image_path = self._get_image_path(icon_filename)
        
        if not self._validate_image_file(image_path):
            print(f"✗ Arquivo de imagem não encontrado: {image_path}")
            return AutomationResult.FILE_NOT_EXISTS
        
        print(f"Procurando pelo ícone: {icon_filename}")
        print(f"Caminho da imagem: {image_path}")
        
        result = self._locate_and_double_click_image(image_path, f"ícone ({icon_filename})")
        
        if result == AutomationResult.SUCCESS:
            print("✓ Double click no ícone executado com sucesso!")
        elif result == AutomationResult.IMAGE_NOT_FOUND:
            print("⚠ Ícone não encontrado na tela. Verifique se:")
            print("  - O ícone está visível no desktop")
            print("  - A imagem icon.png corresponde ao ícone atual")
            print("  - A resolução da tela não mudou")
        else:
            print("✗ Falha ao executar o double click")
        
        return result


def main():
    config = AutomationConfig(
        confidence=0.9,           # Confiança alta para ser mais preciso
        double_click_interval=0.1, # Intervalo entre os cliques do double click
        startup_delay=3,          # Tempo de espera antes de iniciar
        images_folder="images",   # Pasta onde estão as imagens
        preview_mode=False        # Desabilitado por padrão
    )
    
    automation = DesktopIconAutomation(config)
    
    # PASSO 1: Executa o double click no ícone
    result_double_click = automation.double_click_desktop_icon("icon.png")
    
    if result_double_click == AutomationResult.SUCCESS:
        print("\n✓ PASSO 1: Double click executado com sucesso!")
        
        # PASSO 2: Aguarda 5 segundos antes de continuar
        print("\n=== PASSO 2: AGUARDANDO 5 SEGUNDOS ===")
        automation._wait_with_countdown(5, "Preparando para o click no certificado")
        
        # PASSO 3: Executa o click único na imagem cert.png
        result_cert_click = automation.single_click_image("cert.png")
        
        if result_cert_click == AutomationResult.SUCCESS:
            print("\n✓ PASSO 3: Click na imagem cert.png executado com sucesso!")
            
            # PASSO 4: Aguarda 3 segundos antes de continuar
            print("\n=== PASSO 4: AGUARDANDO 3 SEGUNDOS ===")
            automation._wait_with_countdown(3, "Preparando para o click em entrar")
            
            # PASSO 5: Executa o click único na imagem entrar.png
            result_entrar_click = automation.single_click_image("entrar.png")
            
            # Mensagem final baseada nos resultados
            if result_entrar_click == AutomationResult.SUCCESS:
                print("\n🎉 AUTOMAÇÃO COMPLETA CONCLUÍDA COM SUCESSO!")
                print("✓ PASSO 1: Double click no ícone realizado")
                print("✓ PASSO 3: Click único na imagem cert.png realizado")
                print("✓ PASSO 5: Click único na imagem entrar.png realizado")
            else:
                print(f"\n⚠ AUTOMAÇÃO PARCIALMENTE CONCLUÍDA!")
                print("✓ PASSO 1: Double click no ícone realizado")
                print("✓ PASSO 3: Click único na imagem cert.png realizado")
                print(f"✗ PASSO 5: Click em entrar.png falhou: {result_entrar_click.value}")
                print("\nDicas para solução do problema do click em entrar:")
                print("1. Verifique se a imagem entrar.png está na pasta 'images'")
                print("2. Certifique-se de que o botão 'Entrar' está visível na tela")
                print("3. A imagem deve corresponder exatamente ao botão na tela")
        else:
            print(f"\n⚠ AUTOMAÇÃO PARCIALMENTE CONCLUÍDA!")
            print("✓ PASSO 1: Double click no ícone realizado")
            print(f"✗ PASSO 3: Click em cert.png falhou: {result_cert_click.value}")
            print("\nDicas para solução do problema do click no certificado:")
            print("1. Verifique se a imagem cert.png está na pasta 'images'")
            print("2. Certifique-se de que o elemento está visível na tela")
            print("3. A imagem deve corresponder exatamente ao elemento na tela")
    else:
        print(f"\n❌ AUTOMAÇÃO FALHOU NO PRIMEIRO PASSO: {result_double_click.value}")
        print("\nDicas para solução de problemas:")
        print("1. Verifique se a imagem icon.png está na pasta 'images'")
        print("2. Certifique-se de que o ícone está visível no desktop")
        print("3. A imagem deve corresponder exatamente ao ícone na tela")
        print("4. Tente ajustar o nível de confiança (confidence)")


if __name__ == "__main__":
    main()
