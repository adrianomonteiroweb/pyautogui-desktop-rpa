import re


class TextFormatter:
    def getOnlyNumbers(self, text):
        """
        Remove letras e caracteres especiais de uma string, retornando apenas números.
        
        Args:
            text (str): A string de entrada
            
        Returns:
            str: String contendo apenas números
        """
        if not isinstance(text, str):
            text = str(text)
        
        # Remove tudo que não seja dígito
        return re.sub(r'[^0-9]', '', text)