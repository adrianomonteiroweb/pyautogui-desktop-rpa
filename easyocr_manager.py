"""
EasyOCR Manager - Versão Refatorada
Sistema otimizado para busca e clique em datas com ordenação visual
"""

import easyocr
import pyautogui
import os
from typing import List, Tuple, Optional, Dict, Any


class EasyOCRManager:
    """
    Gerenciador otimizado para operações de OCR e interações com PyAutoGUI
    Especializado em busca e clique de datas com ordenação visual
    """
    
    def __init__(self, languages: List[str] = ['pt']):
        """
        Inicializa o leitor EasyOCR
        
        Args:
            languages: Lista de idiomas para o OCR (padrão: ['pt'])
        """
        self.reader = easyocr.Reader(languages)
        self.screenshot_path = r"C:\Users\adria\Documents\hobots\abax\screenshot.png"
        
        # Cria o diretório se não existir
        os.makedirs(os.path.dirname(self.screenshot_path), exist_ok=True)
    
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
        
        # PRIORIDADE 1: Busca pelo padrão completo DD/MM/YYYY00:00:00
        target_with_time = f"{target_clean}00:00:00"
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
    
    def _is_fuzzy_date_match(self, target: str, text: str) -> bool:
        """
        Busca aproximada por texto, útil quando o OCR não é 100% preciso
        
        Args:
            target: Data alvo
            text: Texto encontrado
            
        Returns:
            bool: True se for uma correspondência fuzzy válida
        """
        target_clean = self._normalize_text(target.lower())
        text_clean = self._normalize_text(text.lower())
        
        # Para datas, verifica componentes específicos
        target_parts = target_clean.split('/')
        if len(target_parts) != 3:
            return False
            
        day_target, month_target, year_target = target_parts
        
        # Verifica se tem mês e ano corretos
        has_month = month_target in text_clean
        has_year = year_target in text_clean
        
        return has_month and has_year
    
    # =============================================================================
    # MÉTODOS DE BUSCA E ANÁLISE
    # =============================================================================
    
    def find_date_occurrences(self, target_date: str) -> Dict[str, Any]:
        """
        Encontra todas as ocorrências de uma data na tela
        
        Args:
            target_date: Data alvo no formato "DD/MM/YYYY"
            
        Returns:
            Dict com informações das ocorrências encontradas
        """
        try:
            screenshot_path = self.take_screenshot()
            results = self.read_text_from_image(screenshot_path)
            
            exact_matches = []
            fuzzy_matches = []
            
            for bbox, text, confidence in results:
                x_centro, y_centro = self._calculate_center_coordinates(bbox)
                
                match_data = (bbox, text, confidence, x_centro, y_centro)
                
                if self._is_exact_date_match(target_date, text):
                    exact_matches.append(match_data)
                elif self._is_fuzzy_date_match(target_date, text):
                    fuzzy_matches.append(match_data)
            
            # Ordena por posição visual
            exact_matches_sorted = self._sort_matches_visually(exact_matches)
            fuzzy_matches_sorted = self._sort_matches_visually(fuzzy_matches)
            
            return {
                'exact_matches': exact_matches_sorted,
                'fuzzy_matches': fuzzy_matches_sorted,
                'total_exact': len(exact_matches),
                'total_fuzzy': len(fuzzy_matches),
                'last_exact': exact_matches_sorted[-1] if exact_matches_sorted else None,
                'last_fuzzy': fuzzy_matches_sorted[-1] if fuzzy_matches_sorted else None
            }
            
        except Exception as e:
            print(f"❌ Erro na busca por ocorrências: {e}")
            return {
                'exact_matches': [],
                'fuzzy_matches': [],
                'total_exact': 0,
                'total_fuzzy': 0,
                'last_exact': None,
                'last_fuzzy': None
            }
    
    # =============================================================================
    # MÉTODOS DE CLIQUE OTIMIZADOS
    # =============================================================================
    
    def click_date_with_time_pattern(self, target_date: str) -> bool:
        """
        Busca especificamente por datas no formato DD/MM/YYYY 00:00:00
        Método OTIMIZADO para o padrão mais comum
        
        Args:
            target_date: Data alvo no formato "DD/MM/YYYY"
            
        Returns:
            bool: True se encontrou e clicou, False caso contrário
        """
        try:
            target_with_time = f"{target_date} 00:00:00"
            print(f"🔍 [OTIMIZADO] Procurando padrão: {target_with_time}")
            
            occurrences = self.find_date_occurrences(target_date)
            
            if occurrences['exact_matches']:
                # Clica na última ocorrência visual
                last_match = occurrences['last_exact']
                bbox, text, confidence, x_centro, y_centro = last_match
                
                print(f"✅ Padrão encontrado: '{text}' (confiança: {confidence:.2f})")
                print(f"🖱️ Clicando na ÚLTIMA ocorrência visual: x={x_centro:.0f}, y={y_centro:.0f}")
                
                if occurrences['total_exact'] > 1:
                    print(f"📊 Total de {occurrences['total_exact']} ocorrências - clicando na última")
                    self._debug_show_visual_order(occurrences['exact_matches'])
                
                pyautogui.click(x_centro, y_centro)
                return True
            else:
                print(f"❌ Padrão '{target_with_time}' não encontrado")
                return False
                
        except Exception as e:
            print(f"❌ Erro no método otimizado: {e}")
            return False
    
    def click_exact_date(self, target_date: str) -> bool:
        """
        Busca e clica em uma data exata
        
        Args:
            target_date: Data alvo no formato "DD/MM/YYYY"
            
        Returns:
            bool: True se encontrou e clicou, False caso contrário
        """
        try:
            print(f"🔍 [EXATO] Procurando data: {target_date}")
            
            occurrences = self.find_date_occurrences(target_date)
            
            if occurrences['exact_matches']:
                last_match = occurrences['last_exact']
                bbox, text, confidence, x_centro, y_centro = last_match
                
                print(f"✅ Data exata encontrada: '{text}' (confiança: {confidence:.2f})")
                print(f"🖱️ Clicando na ÚLTIMA ocorrência: x={x_centro:.0f}, y={y_centro:.0f}")
                
                if occurrences['total_exact'] > 1:
                    self._debug_show_visual_order(occurrences['exact_matches'])
                
                pyautogui.click(x_centro, y_centro)
                return True
            else:
                print(f"❌ Data exata '{target_date}' não encontrada")
                return False
                
        except Exception as e:
            print(f"❌ Erro na busca exata: {e}")
            return False
    
    def click_fuzzy_date(self, target_date: str) -> bool:
        """
        Busca e clica usando correspondência aproximada
        
        Args:
            target_date: Data alvo no formato "DD/MM/YYYY"
            
        Returns:
            bool: True se encontrou e clicou, False caso contrário
        """
        try:
            print(f"🔍 [FUZZY] Busca aproximada: {target_date}")
            
            occurrences = self.find_date_occurrences(target_date)
            
            if occurrences['fuzzy_matches']:
                last_match = occurrences['last_fuzzy']
                bbox, text, confidence, x_centro, y_centro = last_match
                
                print(f"✅ Correspondência fuzzy: '{text}' (confiança: {confidence:.2f})")
                print(f"🖱️ Clicando na ÚLTIMA ocorrência fuzzy: x={x_centro:.0f}, y={y_centro:.0f}")
                
                pyautogui.click(x_centro, y_centro)
                return True
            else:
                print(f"❌ Nenhuma correspondência fuzzy para '{target_date}'")
                return False
                
        except Exception as e:
            print(f"❌ Erro na busca fuzzy: {e}")
            return False
    
    # =============================================================================
    # MÉTODO PRINCIPAL DE BUSCA INTELIGENTE
    # =============================================================================
    
    def click_best_date_match(self, target_date: str) -> bool:
        """
        Método principal que tenta diferentes estratégias para encontrar e clicar na data
        
        Args:
            target_date: Data alvo no formato "DD/MM/YYYY"
            
        Returns:
            bool: True se encontrou e clicou, False caso contrário
        """
        try:
            print(f"🎯 [INTELIGENTE] Buscando melhor correspondência: {target_date}")
            
            # ESTRATÉGIA 1: Padrão otimizado DD/MM/YYYY 00:00:00
            if self.click_date_with_time_pattern(target_date):
                print("✅ Sucesso com método otimizado!")
                return True
            
            # ESTRATÉGIA 2: Busca exata
            print("🔄 Tentando busca exata...")
            if self.click_exact_date(target_date):
                print("✅ Sucesso com busca exata!")
                return True
            
            # ESTRATÉGIA 3: Busca fuzzy
            print("🔄 Tentando busca aproximada...")
            if self.click_fuzzy_date(target_date):
                print("✅ Sucesso com busca aproximada!")
                return True
            
            # ESTRATÉGIA 4: Busca por padrões genéricos
            print("🔄 Tentando busca por padrões...")
            if self._try_generic_date_patterns(target_date):
                print("✅ Sucesso com padrões genéricos!")
                return True
            
            print("❌ Todas as estratégias falharam")
            return False
            
        except Exception as e:
            print(f"❌ Erro no método inteligente: {e}")
            return False
    
    # =============================================================================
    # MÉTODOS AUXILIARES E DEBUG
    # =============================================================================
    
    def _debug_show_visual_order(self, matches: List[Tuple]) -> None:
        """
        Mostra a ordem visual das correspondências (para debug)
        
        Args:
            matches: Lista de matches ordenados visualmente
        """
        print(f"📍 Ordem visual das correspondências:")
        for i, (_, text, _, x, y) in enumerate(matches, 1):
            marker = "👇 ÚLTIMA" if i == len(matches) else f"  {i}ª"
            print(f"     {marker}: '{text}' em x={x:.0f}, y={y:.0f}")
    
    def _try_generic_date_patterns(self, target_date: str) -> bool:
        """
        Busca por padrões genéricos de data como fallback final
        
        Args:
            target_date: Data alvo
            
        Returns:
            bool: True se encontrou e clicou
        """
        try:
            screenshot_path = self.take_screenshot()
            results = self.read_text_from_image(screenshot_path)
            
            date_candidates = []
            
            for bbox, text, confidence in results:
                # Procura por textos que possam ser datas
                if ('/' in text or any(char.isdigit() for char in text)) and len(text) >= 8:
                    if any(part in text for part in target_date.split('/')):
                        x_centro, y_centro = self._calculate_center_coordinates(bbox)
                        date_candidates.append((bbox, text, confidence, x_centro, y_centro))
            
            if date_candidates:
                # Ordena e clica na última
                sorted_candidates = self._sort_matches_visually(date_candidates)
                last_candidate = sorted_candidates[-1]
                bbox, text, confidence, x_centro, y_centro = last_candidate
                
                print(f"📅 Candidato genérico: '{text}' (confiança: {confidence:.2f})")
                print(f"🖱️ Clicando em: x={x_centro:.0f}, y={y_centro:.0f}")
                
                pyautogui.click(x_centro, y_centro)
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Erro na busca genérica: {e}")
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
        return self.click_date_with_time_pattern(target_date)
    
    def click_last_occurrence(self, text_to_find: str, fuzzy_match: bool = False) -> bool:
        """Método legado para compatibilidade"""
        if fuzzy_match:
            return self.click_fuzzy_date(text_to_find)
        else:
            return self.click_exact_date(text_to_find)
    
    def find_text_coordinates(self, text_to_find: str) -> Optional[Tuple[float, float]]:
        """Método legado para compatibilidade"""
        occurrences = self.find_date_occurrences(text_to_find)
        if occurrences['last_exact']:
            _, _, _, x, y = occurrences['last_exact']
            return (x, y)
        return None