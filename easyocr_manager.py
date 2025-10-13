"""
EasyOCR Manager - Versão Otimizada
Sistema simplificado focado no método que funciona: busca por datas com padrão DD/MM/YYYY 00:00:00
Sempre clica na última ocorrência visual (ordenada por posição Y, depois X)
Implementa padrão Singleton para reutilizar a instância e evitar inicializações custosas
"""

import easyocr
import pyautogui
import os
import warnings
import sys
import io
from typing import List, Tuple, Optional, Dict, Any

# Suprime o aviso específico do pin_memory do PyTorch
warnings.filterwarnings("ignore", message=".*pin_memory.*", category=UserWarning)
# Suprime a mensagem sobre CUDA/MPS não disponível
warnings.filterwarnings("ignore", message=".*CUDA.*defaulting to CPU.*")
warnings.filterwarnings("ignore", message=".*Neither CUDA nor MPS.*")


class EasyOCRManager:
    """
    Gerenciador otimizado para operações de OCR e interações com PyAutoGUI
    Focado no método que funciona: busca por datas DD/MM/YYYY 00:00:00 e clique na última ocorrência visual
    Implementa padrão Singleton para reutilizar a instância e evitar inicializações custosas
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, languages: List[str] = ['pt']):
        """
        Implementa padrão Singleton para reutilizar a instância
        """
        if cls._instance is None:
            cls._instance = super(EasyOCRManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, languages: List[str] = ['pt']):
        """
        Inicializa o leitor EasyOCR apenas uma vez (Singleton)
        
        Args:
            languages: Lista de idiomas para o OCR (padrão: ['pt'])
        """
        # Evita reinicialização se já foi inicializado
        if self._initialized:
            return
            
        # Suprime saídas durante a inicialização do EasyOCR
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        try:
            self.reader = easyocr.Reader(languages)
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        
        self.screenshot_path = r"C:\Users\adria\Documents\hobots\abax\screenshot.png"
        
        # Cria o diretório se não existir
        os.makedirs(os.path.dirname(self.screenshot_path), exist_ok=True)
        
        # Marca como inicializado
        self._initialized = True
    
    # =============================================================================
    # MÉTODOS BÁSICOS DE OCR E SCREENSHOT
    # =============================================================================
    
    def take_screenshot(self) -> str:
        """
        Captura um screenshot da tela e salva no caminho especificado
        
        Returns:
            str: Caminho do arquivo de screenshot salvo
        """
        screenshot = pyautogui.screenshot()
        screenshot.save(self.screenshot_path)
        return self.screenshot_path
    
    def read_text_from_image(self, image_path: str) -> List[Tuple]:
        """
        Lê texto de uma imagem usando EasyOCR
        
        Args:
            image_path: Caminho para a imagem
            
        Returns:
            List[Tuple]: Lista de tuplas contendo (bbox, texto, confiança)
        """
        return self.reader.readtext(image_path)
    
    # =============================================================================
    # MÉTODOS DE PROCESSAMENTO E NORMALIZAÇÃO
    # =============================================================================
    
    def _normalize_text(self, text: str) -> str:
        """
        Normaliza texto para comparação (remove espaços, converte 'o' para '0')
        
        Args:
            text: Texto a ser normalizado
            
        Returns:
            str: Texto normalizado
        """
        return text.replace(' ', '').replace('o', '0').replace('O', '0')
    
    def _calculate_center_coordinates(self, bbox: List[List[float]]) -> Tuple[float, float]:
        """
        Calcula as coordenadas do centro de uma bounding box
        
        Args:
            bbox: Bounding box do texto
            
        Returns:
            Tuple[float, float]: Coordenadas (x, y) do centro
        """
        x_coords = [p[0] for p in bbox]
        y_coords = [p[1] for p in bbox]
        x_centro = sum(x_coords) / 4
        y_centro = sum(y_coords) / 4
        return x_centro, y_centro
    
    def _sort_matches_visually(self, matches: List[Tuple]) -> List[Tuple]:
        """
        Ordena matches por posição visual (Y primeiro, depois X)
        
        Args:
            matches: Lista de matches com coordenadas
            
        Returns:
            List[Tuple]: Matches ordenados visualmente
        """
        return sorted(matches, key=lambda x: (x[4], x[3]))  # (y_centro, x_centro)
    
    # =============================================================================
    # MÉTODOS DE VALIDAÇÃO DE DATAS
    # =============================================================================
    
    def _is_exact_date_match(self, target: str, text: str) -> bool:
        """
        Verifica se um texto corresponde EXATAMENTE a uma data alvo
        Otimizado para o padrão DD/MM/YYYY 00:00:00
        
        Args:
            target: Data alvo (ex: "01/07/2025")
            text: Texto encontrado pelo OCR
            
        Returns:
            bool: True se for uma correspondência válida
        """
        target_clean = self._normalize_text(target)
        text_clean = self._normalize_text(text)
        
        # PRIORIDADE 1: Busca pelo padrão completo DD/MM/YYYY 00:00:00
        target_with_time = f"{target_clean} 00:00:00"

        if target_with_time in text_clean:
            return True
        
        # PRIORIDADE 2: Busca pela data básica DD/MM/YYYY
        if target_clean in text_clean:
            target_parts = target.split('/')
            if len(target_parts) == 3:
                day, month, year = target_parts
                if f"{day}/{month}/{year}" in text_clean:
                    return True
        
        return False
    

    
    # =============================================================================
    # MÉTODOS DE BUSCA E ANÁLISE
    # =============================================================================
    
    def find_date_occurrences(self, target_date: str, screenshot_path: str = None) -> Dict[str, Any]:
        """
        Encontra todas as ocorrências de uma data na tela
        
        Args:
            target_date: Data alvo no formato "DD/MM/YYYY"
            screenshot_path: Caminho para screenshot (opcional, captura novo se não fornecido)
            
        Returns:
            Dict com informações das ocorrências encontradas
        """
        try:
            if screenshot_path is None:
                screenshot_path = self.take_screenshot()
            results = self.read_text_from_image(screenshot_path)
            
            exact_matches = []
            
            for bbox, text, confidence in results:
                x_centro, y_centro = self._calculate_center_coordinates(bbox)
                
                match_data = (bbox, text, confidence, x_centro, y_centro)
                
                if self._is_exact_date_match(target_date, text):
                    exact_matches.append(match_data)
            
            # Ordena por posição visual
            exact_matches_sorted = self._sort_matches_visually(exact_matches)
            
            return {
                'exact_matches': exact_matches_sorted,
                'total_exact': len(exact_matches),
                'last_exact': exact_matches_sorted[-1] if exact_matches_sorted else None
            }
            
        except Exception as e:
            print(f"❌ Erro na busca por ocorrências: {e}")
            return {
                'exact_matches': [],
                'total_exact': 0,
                'last_exact': None
            }
    
    # =============================================================================
    # MÉTODOS DE CLIQUE OTIMIZADOS
    # =============================================================================
    
    def find_column_header_position(self, column_image_path: str) -> Optional[Tuple[float, float]]:
        """
        Encontra a posição do cabeçalho da coluna usando uma imagem de referência
        
        Args:
            column_image_path: Caminho para a imagem do cabeçalho da coluna
            
        Returns:
            Tuple[float, float]: Coordenadas (x, y) do centro da coluna ou None se não encontrar
        """
        try:
            # Localiza a imagem na tela
            location = pyautogui.locateOnScreen(column_image_path, confidence=0.8)
            if location:
                # Retorna o centro da área encontrada
                center = pyautogui.center(location)
                return (center.x, center.y)
            return None
        except Exception as e:
            print(f"❌ Erro ao localizar coluna: {e}")
            return None
    
    def click_date_in_column(self, target_date: str, column_image_path: str, 
                           max_rows_below: int = 10, row_height: int = 25) -> bool:
        """
        Clica em uma data específica que está na mesma coluna vertical de um cabeçalho
        
        Args:
            target_date: Data alvo no formato "DD/MM/YYYY"
            column_image_path: Caminho para a imagem do cabeçalho da coluna
            max_rows_below: Número máximo de linhas para procurar abaixo do cabeçalho
            row_height: Altura aproximada de cada linha da tabela em pixels
            
        Returns:
            bool: True se encontrou e clicou, False caso contrário
        """
        try:
            # Encontra a posição da coluna
            column_position = self.find_column_header_position(column_image_path)
            if not column_position:
                print(f"❌ Não foi possível localizar a coluna de referência")
                return False
            
            column_x, column_y = column_position
            print(f"✅ Coluna encontrada em: x={column_x}, y={column_y}")
            
            # Captura screenshot para análise OCR
            screenshot_path = self.take_screenshot()
            results = self.read_text_from_image(screenshot_path)
            
            # Procura por datas que estão na mesma coluna (mesma coordenada X aproximada)
            # e abaixo do cabeçalho (coordenada Y maior)
            tolerance_x = 50  # Tolerância horizontal para considerar "mesma coluna"
            
            matches_in_column = []
            
            for bbox, text, confidence in results:
                x_centro, y_centro = self._calculate_center_coordinates(bbox)
                
                # Verifica se está na mesma coluna (X similar) e abaixo do cabeçalho (Y maior)
                if (abs(x_centro - column_x) <= tolerance_x and 
                    y_centro > column_y and 
                    y_centro <= column_y + (max_rows_below * row_height)):
                    
                    if self._is_exact_date_match(target_date, text):
                        matches_in_column.append((bbox, text, confidence, x_centro, y_centro))
            
            if matches_in_column:
                # Ordena por posição Y (primeira ocorrência de cima para baixo)
                matches_in_column.sort(key=lambda x: x[4])  # Ordena por y_centro
                
                # Clica na primeira ocorrência encontrada na coluna
                first_match = matches_in_column[0]
                bbox, text, confidence, x_centro, y_centro = first_match
                
                print(f"✅ Data '{target_date}' encontrada na coluna em: x={x_centro}, y={y_centro}")
                print(f"   Texto OCR: '{text}' (confiança: {confidence:.2f})")
                
                pyautogui.click(x_centro, y_centro)
                return True
            else:
                print(f"❌ Data '{target_date}' não encontrada na coluna especificada")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao clicar na data da coluna: {e}")
            return False
    
    def click_date_below_data_inicio_column(self, target_date: str) -> bool:
        """
        Método específico para clicar em datas na coluna "Data Início"
        
        Args:
            target_date: Data alvo no formato "DD/MM/YYYY"
            
        Returns:
            bool: True se encontrou e clicou, False caso contrário
        """
        column_image_path = os.path.join(os.path.dirname(__file__), 
                                       "images", "tabelas", "coluna_data_inicio.png")
        
        if not os.path.exists(column_image_path):
            print(f"❌ Imagem da coluna não encontrada: {column_image_path}")
            return False
        
        return self.click_date_in_column(target_date, column_image_path)
    
    def find_all_dates_positions(self, target_dates: List[str], screenshot_path: str = None) -> Dict[str, Tuple[float, float]]:
        """
        Mapeia as posições de múltiplas datas de uma só vez para otimizar o processo
        
        Args:
            target_dates: Lista de datas alvo no formato "DD/MM/YYYY"
            screenshot_path: Caminho para screenshot (opcional, captura novo se não fornecido)
            
        Returns:
            Dict[str, Tuple[float, float]]: Dicionário com data -> (x, y) das posições encontradas
        """
        try:
            if screenshot_path is None:
                screenshot_path = self.take_screenshot()
            
            results = self.read_text_from_image(screenshot_path)
            date_positions = {}
            
            # Para cada data alvo, procura sua posição
            for target_date in target_dates:
                exact_matches = []
                
                for bbox, text, confidence in results:
                    if self._is_exact_date_match(target_date, text):
                        x_centro, y_centro = self._calculate_center_coordinates(bbox)
                        exact_matches.append((bbox, text, confidence, x_centro, y_centro))
                
                # Ordena por posição visual e pega a última
                if exact_matches:
                    exact_matches_sorted = self._sort_matches_visually(exact_matches)
                    last_match = exact_matches_sorted[-1]
                    _, _, _, x_centro, y_centro = last_match
                    date_positions[target_date] = (x_centro, y_centro)
            
            return date_positions
            
        except Exception as e:
            print(f"❌ Erro ao mapear posições das datas: {e}")
            return {}

    def click_best_date_match(self, target_date: str, screenshot_path: str = None) -> bool:
        """
        Método otimizado que busca e clica em datas no formato DD/MM/YYYY 00:00:00
        Sempre clica na ÚLTIMA ocorrência visual (ordenada por Y, depois X)
        
        Args:
            target_date: Data alvo no formato "DD/MM/YYYY"
            screenshot_path: Caminho para screenshot (opcional, captura novo se não fornecido)
            
        Returns:
            bool: True se encontrou e clicou, False caso contrário
        """
        try:
            target_with_time = f"{target_date} 00:00:00"
            
            occurrences = self.find_date_occurrences(target_date, screenshot_path)
            
            if occurrences['exact_matches']:
                # Clica na última ocorrência visual
                last_match = occurrences['last_exact']
                bbox, text, confidence, x_centro, y_centro = last_match
                
                pyautogui.click(x_centro, y_centro)
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Erro no método otimizado: {e}")
            return False

# =============================================================================
# CLASSE DE COMPATIBILIDADE (ALIAS)
# =============================================================================

class EasyOCR(EasyOCRManager):
    """
    Classe de compatibilidade para manter código existente funcionando
    """
    
    def click_date_with_time(self, target_date: str) -> bool:
        """Alias para compatibilidade"""
        return self.click_best_date_match(target_date)
    
    def click_last_occurrence(self, text_to_find: str, fuzzy_match: bool = False) -> bool:
        """Método legado para compatibilidade"""
        return self.click_best_date_match(text_to_find)
        
    def click_date_in_data_inicio_column(self, target_date: str) -> bool:
        """Método para clicar em data específica na coluna Data Início"""
        return self.click_date_below_data_inicio_column(target_date)
    
    def find_text_coordinates(self, text_to_find: str) -> Optional[Tuple[float, float]]:
        """Método legado para compatibilidade"""
        occurrences = self.find_date_occurrences(text_to_find)

        if occurrences['last_exact']:
            _, _, _, x, y = occurrences['last_exact']
            return (x, y)
        
        return None