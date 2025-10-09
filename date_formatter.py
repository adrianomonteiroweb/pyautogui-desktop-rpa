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

    @staticmethod
    def generate_monthly_start_dates(start_date: str, end_date: str, format_type: str = "dd/mm/yyyy") -> list:
        """
        Gera todas as datas iniciais de cada mês dentro do range especificado.
        
        Args:
            start_date (str): Data de início no formato DD/MM/YYYY (ex: "01/01/2023")
            end_date (str): Data de fim no formato DD/MM/YYYY (ex: "31/12/2024")
            format_type (str): Formato de saída das datas (padrão: "dd/mm/yyyy")
                             - "dd/mm/yyyy": 01/01/2023
                             - "ddmmyyyy": 01012023
                             - "iso": 2023-01-01
            
        Returns:
            list: Lista com as datas iniciais de cada mês no formato especificado
            
        Example:
            Input: start_date="01/01/2023", end_date="31/12/2024"
            Output: ["01/01/2023", "01/02/2023", "01/03/2023", ..., "01/12/2024"]
            
        Raises:
            ValueError: Se as datas não estiverem no formato correto ou se start_date > end_date
        """
        try:
            # Parse das datas de entrada (formato DD/MM/YYYY)
            start_dt = datetime.strptime(start_date, "%d/%m/%Y")
            end_dt = datetime.strptime(end_date, "%d/%m/%Y")
            
            # Validação: data inicial deve ser menor ou igual à data final
            if start_dt > end_dt:
                raise ValueError(f"Data inicial ({start_date}) deve ser menor ou igual à data final ({end_date})")
            
            monthly_dates = []
            current_date = datetime(start_dt.year, start_dt.month, 1)  # Primeiro dia do mês inicial
            
            # Gera as datas do primeiro dia de cada mês
            while current_date <= end_dt:
                # Formata conforme o tipo solicitado
                if format_type.lower() == "dd/mm/yyyy":
                    formatted_date = current_date.strftime("%d/%m/%Y")
                elif format_type.lower() == "ddmmyyyy":
                    formatted_date = current_date.strftime("%d%m%Y")
                elif format_type.lower() == "iso":
                    formatted_date = current_date.strftime("%Y-%m-%d")
                else:
                    raise ValueError(f"Formato não suportado: {format_type}. Suportados: 'dd/mm/yyyy', 'ddmmyyyy', 'iso'")
                
                monthly_dates.append(formatted_date)
                
                # Avança para o próximo mês
                if current_date.month == 12:
                    current_date = datetime(current_date.year + 1, 1, 1)
                else:
                    current_date = datetime(current_date.year, current_date.month + 1, 1)
            
            return monthly_dates
            
        except ValueError as e:
            if "does not match format" in str(e):
                raise ValueError(f"Formato de data inválido. Use DD/MM/YYYY (ex: 01/01/2023)") from e
            else:
                raise e


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


def generate_monthly_dates(start_date: str, end_date: str, format_type: str = "dd/mm/yyyy") -> list:
    """
    Função de conveniência para gerar datas iniciais de cada mês.
    
    Args:
        start_date (str): Data de início no formato DD/MM/YYYY
        end_date (str): Data de fim no formato DD/MM/YYYY
        format_type (str): Formato de saída das datas
        
    Returns:
        list: Lista com as datas iniciais de cada mês
    """
    return DateFormatter.generate_monthly_start_dates(start_date, end_date, format_type)


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
    
    # Teste do gerador de datas mensais
    print(f"\n--- Teste do gerador de datas mensais ---")
    start = "01/01/2023"
    end = "31/12/2024"
    monthly_dates = DateFormatter.generate_monthly_start_dates(start, end)
    print(f"Range: {start} até {end}")
    print(f"Datas geradas ({len(monthly_dates)} meses):")
    for i, date in enumerate(monthly_dates[:6]):  # Mostra apenas os primeiros 6
        print(f"  {i+1}: {date}")
    if len(monthly_dates) > 6:
        print(f"  ... e mais {len(monthly_dates) - 6} datas")
    
    # Teste com diferentes formatos
    print(f"\nTeste com formato DDMMYYYY:")
    monthly_ddmmyyyy = DateFormatter.generate_monthly_start_dates(start, end, "ddmmyyyy")
    print(f"Primeiras 3 datas: {monthly_ddmmyyyy[:3]}")
    
    print(f"\nTeste com formato ISO:")
    monthly_iso = DateFormatter.generate_monthly_start_dates(start, end, "iso")
    print(f"Primeiras 3 datas: {monthly_iso[:3]}")