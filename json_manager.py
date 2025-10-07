import json
import os
from typing import Dict, Any, Optional


class JSONManager:
    """Gerenciador para ler arquivos JSON do projeto (settings.json e params.json)"""
    
    def __init__(self, project_root: Optional[str] = None):
        if project_root is None:
            self.project_root = os.path.dirname(os.path.abspath(__file__))
        else:
            self.project_root = project_root
    
    def _read_json_file(self, filename: str) -> Dict[str, Any]:
        # Garante que o arquivo tenha extensão .json
        if not filename.endswith('.json'):
            filename += '.json'
        
        file_path = os.path.join(self.project_root, filename)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo {filename} não encontrado em {self.project_root}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                if not content:
                    # Arquivo vazio, retorna dicionário vazio
                    return {}
                return json.loads(content)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Erro ao decodificar JSON do arquivo {filename}: {str(e)}", e.doc, e.pos)
    
    def get_settings(self) -> Dict[str, Any]:
        return self._read_json_file('settings.json')
    
    def get_params(self) -> Dict[str, Any]:
        return self._read_json_file('params.json')
    
    def get_json(self, filename: str) -> Dict[str, Any]:
        return self._read_json_file(filename)
    
    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        configs = {}
        
        try:
            configs['settings'] = self.get_settings()
        except FileNotFoundError:
            configs['settings'] = {}
        
        try:
            configs['params'] = self.get_params()
        except FileNotFoundError:
            configs['params'] = {}
        
        return configs


# Função de conveniência para uso direto
def load_json_config(filename: str) -> Dict[str, Any]:
    manager = JSONManager()
    return manager.get_json(filename)


def load_settings() -> Dict[str, Any]:
    manager = JSONManager()
    return manager.get_settings()


def load_params() -> Dict[str, Any]:
    manager = JSONManager()
    return manager.get_params()


def load_all_configs() -> Dict[str, Dict[str, Any]]:
    manager = JSONManager()
    return manager.get_all_configs()


# Exemplo de uso
if __name__ == "__main__":
    # Exemplo usando a classe
    json_manager = JSONManager()
    
    try:
        settings = json_manager.get_settings()
        print("Settings carregadas:", settings)
    except FileNotFoundError as e:
        print(f"Erro: {e}")
    
    try:
        params = json_manager.get_params()
        print("Params carregados:", params)
    except FileNotFoundError as e:
        print(f"Erro: {e}")
    
    # Exemplo usando funções utilitárias
    try:
        all_configs = load_all_configs()
        print("Todas as configurações:", all_configs)
    except Exception as e:
        print(f"Erro ao carregar configurações: {e}")
