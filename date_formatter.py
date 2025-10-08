from datetime import datetime
from typing import Union


class DateFormatter:
    """
    Classe responsável por formatar datas para diferentes padrões utilizados no RPA.
    """

    @staticmethod
    def iso_to_ddmmyyyy(date_str: str) -> str:
        """
        Converte uma data do formato ISO (YYYY-MM-DD) para o formato DDMMYYYY.
        
        Args:
            date_str (str): Data no formato ISO (ex: "2025-01-01")
            
        Returns:
            str: Data no formato DDMMYYYY (ex: "01012025")
            
        Raises:
            ValueError: Se a data não estiver no formato correto
        """
        try:
            # Parse da data no formato ISO
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            
            # Converte para o formato DDMMYYYY
            return date_obj.strftime("%d%m%Y")
            
        except ValueError as e:
            raise ValueError(f"Formato de data inválido: {date_str}. Esperado: YYYY-MM-DD") from e

    @staticmethod
    def ddmmyyyy_to_iso(date_str: str) -> str:
        """
        Converte uma data do formato DDMMYYYY para o formato ISO (YYYY-MM-DD).
        
        Args:
            date_str (str): Data no formato DDMMYYYY (ex: "01012025")
            
        Returns:
            str: Data no formato ISO (ex: "2025-01-01")
            
        Raises:
            ValueError: Se a data não estiver no formato correto
        """
        try:
            # Parse da data no formato DDMMYYYY
            date_obj = datetime.strptime(date_str, "%d%m%Y")
            
            # Converte para o formato ISO
            return date_obj.strftime("%Y-%m-%d")
            
        except ValueError as e:
            raise ValueError(f"Formato de data inválido: {date_str}. Esperado: DDMMYYYY") from e

    @staticmethod
    def format_period_dates(period_dict: dict) -> dict:
        """
        Formata as datas de um período do formato ISO para DDMMYYYY.
        
        Args:
            period_dict (dict): Dicionário com as chaves 'start_date' e 'end_date' no formato ISO
            
        Returns:
            dict: Dicionário com as datas formatadas para DDMMYYYY
            
        Example:
            Input: {"start_date": "2025-01-01", "end_date": "2025-12-31"}
            Output: {"start_date": "01012025", "end_date": "31122025"}
        """
        formatted_period = {}
        
        if 'start_date' in period_dict:
            formatted_period['start_date'] = DateFormatter.iso_to_ddmmyyyy(period_dict['start_date'])
            
        if 'end_date' in period_dict:
            formatted_period['end_date'] = DateFormatter.iso_to_ddmmyyyy(period_dict['end_date'])
            
        return formatted_period

    @staticmethod
    def validate_date_format(date_str: str, format_type: str = "iso") -> bool:
        """
        Valida se uma data está no formato correto.
        
        Args:
            date_str (str): String da data para validar
            format_type (str): Tipo do formato ("iso" para YYYY-MM-DD ou "ddmmyyyy" para DDMMYYYY)
            
        Returns:
            bool: True se a data estiver no formato correto, False caso contrário
        """
        try:
            if format_type.lower() == "iso":
                datetime.strptime(date_str, "%Y-%m-%d")
            elif format_type.lower() == "ddmmyyyy":
                datetime.strptime(date_str, "%d%m%Y")
            else:
                return False
            return True
        except ValueError:
            return False


# Funções de conveniência para uso direto
def format_date_for_input(iso_date: str) -> str:
    """
    Função de conveniência para formatar uma data ISO para input no sistema.
    
    Args:
        iso_date (str): Data no formato ISO (YYYY-MM-DD)
        
    Returns:
        str: Data formatada para input (DDMMYYYY)
    """
    return DateFormatter.iso_to_ddmmyyyy(iso_date)


def format_period_for_input(period: dict) -> dict:
    """
    Função de conveniência para formatar um período para input no sistema.
    
    Args:
        period (dict): Período com datas no formato ISO
        
    Returns:
        dict: Período com datas formatadas para input
    """
    return DateFormatter.format_period_dates(period)


# Exemplo de uso
if __name__ == "__main__":
    # Teste das funções
    test_date = "2025-01-01"
    formatted_date = DateFormatter.iso_to_ddmmyyyy(test_date)
    print(f"Data original: {test_date}")
    print(f"Data formatada: {formatted_date}")
    
    # Teste com período
    test_period = {"start_date": "2025-01-01", "end_date": "2025-12-31"}
    formatted_period = DateFormatter.format_period_dates(test_period)
    print(f"\nPeríodo original: {test_period}")
    print(f"Período formatado: {formatted_period}")
    
    # Teste de validação
    print(f"\nValidação de '2025-01-01' como ISO: {DateFormatter.validate_date_format('2025-01-01', 'iso')}")
    print(f"Validação de '01012025' como DDMMYYYY: {DateFormatter.validate_date_format('01012025', 'ddmmyyyy')}")