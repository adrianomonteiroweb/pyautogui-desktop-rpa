import pyautogui as pay
import time
import os
from typing import Tuple
from dataclasses import dataclass
from enum import Enum


class AutomationResult(Enum):
    """Enum para resultados da automação"""
    SUCCESS = "success"
    IMAGE_NOT_FOUND = "image_not_found"
    FILE_NOT_EXISTS = "file_not_exists"
    CLICK_FAILED = "click_failed"


@dataclass
class AutomationConfig:
    """Configurações da automação"""
    confidence: float = 0.9  # Aumentando a confiança para ser mais preciso
    double_click_interval: float = 0.1
    startup_delay: int = 3
    images_folder: str = "images"
    preview_mode: bool = False  # Modo para mostrar todas as ocorrências encontradas


class DesktopIconAutomation:
    """Classe responsável pela automação de double click em ícones do desktop"""
    
    def __init__(self, config: AutomationConfig = None):
        self.config = config or AutomationConfig()
        self._setup_pyautogui()
    
    def _setup_pyautogui(self) -> None:
        """Configura o pyautogui"""
        pay.FAILSAFE = True
        pay.PAUSE = 0.1
    
    def _get_image_path(self, filename: str) -> str:
        """Constrói o caminho completo para o arquivo de imagem"""
        return os.path.join(self.config.images_folder, filename)
    
    def _validate_image_file(self, image_path: str) -> bool:
        """Valida se o arquivo de imagem existe"""
        return os.path.exists(image_path)
    
    def _find_all_image_locations(self, image_path: str) -> list:
        """
        Encontra todas as ocorrências de uma imagem na tela
        
        Args:
            image_path: Caminho para a imagem
            
        Returns:
            list: Lista de todas as localizações encontradas
        """
        try:
            locations = list(pay.locateAllOnScreen(image_path, confidence=self.config.confidence))
            return locations
        except Exception as e:
            print(f"Erro ao procurar imagem: {e}")
            return []
    
    def _locate_and_double_click_image(self, image_path: str, description: str) -> AutomationResult:
        """
        Localiza e dá double click em uma imagem na tela
        
        Args:
            image_path: Caminho para a imagem
            description: Descrição da ação para logging
            
        Returns:
            AutomationResult: Resultado da operação
        """
        try:
            # Primeiro, vamos encontrar todas as ocorrências
            all_locations = self._find_all_image_locations(image_path)
            
            if not all_locations:
                print(f"✗ Não foi possível localizar {description}")
                return AutomationResult.IMAGE_NOT_FOUND
            
            print(f"🔍 Encontradas {len(all_locations)} ocorrência(s) de {description}:")
            
            # Se encontrou apenas uma, clica diretamente
            if len(all_locations) == 1:
                location = all_locations[0]
                center = pay.center(location)
                print(f"  Posição única encontrada: {center}")
                
                # Realiza o double click
                pay.doubleClick(center, interval=self.config.double_click_interval)
                print(f"✓ Double click realizado em {description}")
                return AutomationResult.SUCCESS
            
            # Se encontrou múltiplas, mostra todas e pede confirmação
            else:
                print("  Múltiplas ocorrências encontradas:")
                for i, location in enumerate(all_locations, 1):
                    center = pay.center(location)
                    print(f"    {i}. Posição: {center}")
                
                # Por segurança, vamos clicar na primeira (mais provável de ser a correta)
                location = all_locations[0]
                center = pay.center(location)
                print(f"  🎯 Clicando na primeira ocorrência: {center}")
                
                # Realiza o double click
                pay.doubleClick(center, interval=self.config.double_click_interval)
                print(f"✓ Double click realizado em {description}")
                return AutomationResult.SUCCESS
                
        except Exception as e:
            print(f"✗ Erro ao tentar dar double click em {description}: {e}")
            return AutomationResult.CLICK_FAILED
    
    def _wait_with_countdown(self, seconds: int, message: str = "Iniciando automação") -> None:
        """Exibe uma contagem regressiva"""
        print(f"{message} em {seconds} segundos...")
        for i in range(seconds, 0, -1):
            print(f"Aguardando: {i}")
            time.sleep(1)
        print("Iniciando...")
    
    def double_click_desktop_icon(self, icon_filename: str = "icon.png") -> AutomationResult:
        """
        Executa double click no ícone do desktop
        
        Args:
            icon_filename: Nome do arquivo da imagem do ícone
            
        Returns:
            AutomationResult: Resultado da operação
        """
        print("\n=== AUTOMAÇÃO DE DOUBLE CLICK NO ÍCONE DO DESKTOP ===")
        
        # Aguarda antes de iniciar
        self._wait_with_countdown(self.config.startup_delay, "Procurando ícone no desktop")
        
        # Constrói o caminho da imagem
        image_path = self._get_image_path(icon_filename)
        
        # Valida se o arquivo existe
        if not self._validate_image_file(image_path):
            print(f"✗ Arquivo de imagem não encontrado: {image_path}")
            return AutomationResult.FILE_NOT_EXISTS
        
        print(f"Procurando pelo ícone: {icon_filename}")
        print(f"Caminho da imagem: {image_path}")
        
        # Executa o double click
        result = self._locate_and_double_click_image(image_path, f"ícone ({icon_filename})")
        
        # Exibe o resultado
        print("\n=== RESULTADO DA AUTOMAÇÃO ===")
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
    """Função principal"""
    print("=== AUTOMATIZAÇÃO DE DOUBLE CLICK EM ÍCONE DO DESKTOP ===")
    print("Este script irá localizar e dar double click no ícone usando a imagem icon.png")
    print("Certifique-se de que o desktop está visível e o ícone não está oculto")
    
    # Configuração da automação
    config = AutomationConfig(
        confidence=0.9,           # Confiança alta para ser mais preciso
        double_click_interval=0.1, # Intervalo entre os cliques do double click
        startup_delay=3,          # Tempo de espera antes de iniciar
        images_folder="images",   # Pasta onde está a imagem do ícone
        preview_mode=False        # Desabilitado por padrão
    )
    
    # Cria e executa a automação
    automation = DesktopIconAutomation(config)
    result = automation.double_click_desktop_icon("icon.png")
    
    # Mensagem final baseada no resultado
    if result == AutomationResult.SUCCESS:
        print("\n🎉 Automação concluída com sucesso!")
    else:
        print(f"\n❌ Automação falhou: {result.value}")
        print("\nDicas para solução de problemas:")
        print("1. Verifique se a imagem icon.png está na pasta 'images'")
        print("2. Certifique-se de que o ícone está visível no desktop")
        print("3. A imagem deve corresponder exatamente ao ícone na tela")
        print("4. Tente ajustar o nível de confiança (confidence)")


if __name__ == "__main__":
    main()
