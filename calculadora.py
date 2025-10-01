import pyautogui as pay
import time
import os
from typing import List, Tuple, NamedTuple
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
    confidence: float = 0.8
    click_delay: float = 0.5
    startup_delay: int = 3
    images_folder: str = "images"


class ImageAction(NamedTuple):
    """Representa uma ação de clique em imagem"""
    filename: str
    description: str


class CalculatorAutomation:
    """Classe responsável pela automação da calculadora"""
    
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
    
    def _locate_and_click_image(self, image_path: str, description: str) -> AutomationResult:
        """
        Localiza e clica em uma imagem na tela
        
        Args:
            image_path: Caminho para a imagem
            description: Descrição da ação para logging
            
        Returns:
            AutomationResult: Resultado da operação
        """
        try:
            location = pay.locateOnScreen(image_path, confidence=self.config.confidence)
            if location:
                pay.click(location)
                print(f"✓ Clicou em {description}")
                return AutomationResult.SUCCESS
            else:
                print(f"✗ Não foi possível localizar {description}")
                return AutomationResult.IMAGE_NOT_FOUND
        except Exception as e:
            print(f"✗ Erro ao tentar clicar em {description}: {e}")
            return AutomationResult.CLICK_FAILED
    
    def _wait_with_countdown(self, seconds: int, message: str = "Iniciando automação") -> None:
        """Exibe uma contagem regressiva"""
        print(f"{message} em {seconds} segundos...")
        for i in range(seconds, 0, -1):
            print(f"Aguardando: {i}")
            time.sleep(1)
    
    def execute_click_sequence(self, actions: List[ImageAction]) -> Tuple[int, int]:
        """
        Executa uma sequência de cliques em imagens
        
        Args:
            actions: Lista de ações a serem executadas
            
        Returns:
            Tuple[int, int]: (sucessos, total)
        """
        print("\nIniciando sequência de cliques...")
        
        success_count = 0
        total_actions = len(actions)
        
        for action in actions:
            image_path = self._get_image_path(action.filename)
            
            if not self._validate_image_file(image_path):
                print(f"✗ Arquivo não encontrado: {image_path}")
                break
            
            result = self._locate_and_click_image(image_path, action.description)
            
            if result == AutomationResult.SUCCESS:
                success_count += 1
                time.sleep(self.config.click_delay)
            else:
                print(f"Falha ao clicar em {action.description}")
                break
        
        return success_count, total_actions
    
    def run_calculator_operation(self) -> None:
        """Executa a operação 7 + 2 = na calculadora"""
        self._wait_with_countdown(self.config.startup_delay)
        
        # Sequência: 7 + 2 = (calculadora)
        calculator_sequence = [
            ImageAction("7.png", "número 7"),
            ImageAction("mais.png", "botão mais (+)"),
            ImageAction("2.png", "número 2"),
            ImageAction("igual.png", "botão igual (=)")
        ]
        
        success_count, total_actions = self.execute_click_sequence(calculator_sequence)
        
        print(f"\nAutomação concluída. {success_count}/{total_actions} cliques realizados com sucesso.")
        
        if success_count == total_actions:
            print("✓ Operação completada com sucesso!")
        else:
            print("⚠ Operação completada parcialmente.")


def main():
    """Função principal"""
    config = AutomationConfig(
        confidence=0.8,
        click_delay=0.5,
        startup_delay=3,
        images_folder="images"
    )
    
    automation = CalculatorAutomation(config)
    automation.run_calculator_operation()


if __name__ == "__main__":
    main()