import os
import shutil
import getpass
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from json_manager import JSONManager


class FilesManager:
    """Gerenciador para manipular arquivos em massa"""
    
    def __init__(self):
        self.json_manager = JSONManager()
        self.current_user = getpass.getuser()
        self.source_folder = fr"C:\Users\{self.current_user}\Documents\Arquivos ReceitanetBX"
    
    def _render_template(self, template: str, data: Dict[str, Any]) -> str:
        """
        Renderiza um template substituindo variáveis no formato {{key}} pelos valores do dicionário
        Similar ao Mustache.js, mas com funcionalidade básica.
        
        Exemplos:
            template = "C:/arquivos/{{cnpj}}/{{ie}}"
            data = {"cnpj": "12345678000195", "ie": "123456789"}
            resultado = "C:/arquivos/12345678000195/123456789"
        
        Args:
            template: String com template contendo variáveis no formato {{key}}
            data: Dicionário com os dados para substituição
        
        Returns:
            String com as variáveis substituídas. Variáveis não encontradas permanecem inalteradas.
        """
        if not template:
            return template
        
        # Regex para encontrar variáveis no formato {{key}}
        pattern = r'\{\{([^}]+)\}\}'
        
        def replace_var(match):
            var_name = match.group(1).strip()
            if var_name in data:
                return str(data[var_name])
            else:
                # Mantém a variável original se não encontrar o valor
                return match.group(0)
        
        return re.sub(pattern, replace_var, template)
    
    def _get_destination_path(self, data: Optional[Dict[str, Any]] = None) -> str:
        """
        Obtém o caminho de destino do settings.json, processando templates se data for fornecida
        
        Args:
            data: Dicionário com dados para substituição de variáveis
        
        Returns:
            Caminho de destino processado
        """
        settings = self.json_manager.get_settings()
        arquivos_config = settings.get("arquivos", {})
        caminho = arquivos_config.get("caminho")
        
        if not caminho:
            raise ValueError("Caminho de destino não encontrado em settings.json -> arquivos.caminho")
        
        # Se data foi fornecida, processa o template
        if data:
            caminho = self._render_template(caminho, data)
        
        return caminho
    
    def _ensure_directory_exists(self, path: str) -> None:
        """Garante que o diretório existe, criando-o se necessário"""
        Path(path).mkdir(parents=True, exist_ok=True)
    
    def _get_files_in_directory(self, directory: str, extensions: Optional[List[str]] = None) -> List[str]:
        """
        Obtém lista de arquivos em um diretório
        
        Args:
            directory: Caminho do diretório
            extensions: Lista de extensões para filtrar (ex: ['.pdf', '.xml'])
        
        Returns:
            Lista com caminhos completos dos arquivos
        """
        if not os.path.exists(directory):
            return []
        
        files = []
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                if extensions is None or any(file.lower().endswith(ext.lower()) for ext in extensions):
                    files.append(file_path)
        
        return files
    
    def move_files(self, 
                   extensions: Optional[List[str]] = None, 
                   custom_source: Optional[str] = None,
                   custom_destination: Optional[str] = None,
                   data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Move arquivos em massa da pasta padrão para o destino configurado
        
        Args:
            extensions: Lista de extensões para filtrar (ex: ['.pdf', '.xml'])
            custom_source: Caminho de origem personalizado (opcional)
            custom_destination: Caminho de destino personalizado (opcional)
            data: Dicionário com dados para substituição de variáveis no caminho
        
        Returns:
            Dict com informações sobre a operação (arquivos movidos, erros, etc.)
        """
        source_path = custom_source or self.source_folder
        destination_path = custom_destination or self._get_destination_path(data)
        
        # Garante que os diretórios existem
        if not os.path.exists(source_path):
            return {
                "success": False,
                "error": f"Diretório de origem não encontrado: {source_path}",
                "files_moved": [],
                "files_failed": []
            }
        
        self._ensure_directory_exists(destination_path)
        
        # Obtém lista de arquivos
        files_to_move = self._get_files_in_directory(source_path, extensions)
        
        if not files_to_move:
            return {
                "success": True,
                "message": "Nenhum arquivo encontrado para mover",
                "files_moved": [],
                "files_failed": []
            }
        
        files_moved = []
        files_failed = []
        
        for file_path in files_to_move:
            try:
                filename = os.path.basename(file_path)
                destination_file = os.path.join(destination_path, filename)
                
                # Se arquivo já existe no destino, adiciona sufixo numérico
                counter = 1
                base_name, extension = os.path.splitext(filename)
                while os.path.exists(destination_file):
                    new_filename = f"{base_name}_{counter}{extension}"
                    destination_file = os.path.join(destination_path, new_filename)
                    counter += 1
                
                shutil.move(file_path, destination_file)
                files_moved.append({
                    "original": file_path,
                    "destination": destination_file
                })
                
            except Exception as e:
                files_failed.append({
                    "file": file_path,
                    "error": str(e)
                })
        
        return {
            "success": len(files_failed) == 0,
            "source_path": source_path,
            "destination_path": destination_path,
            "total_files": len(files_to_move),
            "files_moved": files_moved,
            "files_failed": files_failed,
            "message": f"Operação concluída. {len(files_moved)} arquivos movidos, {len(files_failed)} falharam."
        }
    
    def copy_files(self, 
                   extensions: Optional[List[str]] = None, 
                   custom_source: Optional[str] = None,
                   custom_destination: Optional[str] = None,
                   empresa: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Copia arquivos em massa da pasta padrão para o destino configurado
        
        Args:
            extensions: Lista de extensões para filtrar (ex: ['.pdf', '.xml'])
            custom_source: Caminho de origem personalizado (opcional)
            custom_destination: Caminho de destino personalizado (opcional)
            empresa: Dicionário com dados da empresa para substituição de variáveis no caminho
        
        Returns:
            Dict com informações sobre a operação (arquivos copiados, erros, etc.)
        """
        source_path = custom_source or self.source_folder
        destination_path = custom_destination or self._get_destination_path(empresa)
        
        # Garante que os diretórios existem
        if not os.path.exists(source_path):
            return {
                "success": False,
                "error": f"Diretório de origem não encontrado: {source_path}",
                "files_copied": [],
                "files_failed": []
            }
        
        self._ensure_directory_exists(destination_path)
        
        # Obtém lista de arquivos
        files_to_copy = self._get_files_in_directory(source_path, extensions)
        
        if not files_to_copy:
            return {
                "success": True,
                "message": "Nenhum arquivo encontrado para copiar",
                "files_copied": [],
                "files_failed": []
            }
        
        files_copied = []
        files_failed = []
        
        for file_path in files_to_copy:
            try:
                filename = os.path.basename(file_path)
                destination_file = os.path.join(destination_path, filename)
                
                # Se arquivo já existe no destino, adiciona sufixo numérico
                counter = 1
                base_name, extension = os.path.splitext(filename)
                while os.path.exists(destination_file):
                    new_filename = f"{base_name}_{counter}{extension}"
                    destination_file = os.path.join(destination_path, new_filename)
                    counter += 1
                
                shutil.copy2(file_path, destination_file)
                files_copied.append({
                    "original": file_path,
                    "destination": destination_file
                })
                
            except Exception as e:
                files_failed.append({
                    "file": file_path,
                    "error": str(e)
                })
        
        return {
            "success": len(files_failed) == 0,
            "source_path": source_path,
            "destination_path": destination_path,
            "total_files": len(files_to_copy),
            "files_copied": files_copied,
            "files_failed": files_failed,
            "message": f"Operação concluída. {len(files_copied)} arquivos copiados, {len(files_failed)} falharam."
        }
    
    def list_files(self, 
                   extensions: Optional[List[str]] = None, 
                   custom_source: Optional[str] = None) -> Dict[str, Any]:
        """
        Lista arquivos na pasta de origem
        
        Args:
            extensions: Lista de extensões para filtrar (ex: ['.pdf', '.xml'])
            custom_source: Caminho de origem personalizado (opcional)
        
        Returns:
            Dict com informações sobre os arquivos encontrados
        """
        source_path = custom_source or self.source_folder
        
        if not os.path.exists(source_path):
            return {
                "success": False,
                "error": f"Diretório não encontrado: {source_path}",
                "files": []
            }
        
        files = self._get_files_in_directory(source_path, extensions)
        
        files_info = []
        for file_path in files:
            stat = os.stat(file_path)
            files_info.append({
                "name": os.path.basename(file_path),
                "path": file_path,
                "size": stat.st_size,
                "modified": stat.st_mtime
            })
        
        return {
            "success": True,
            "source_path": source_path,
            "total_files": len(files_info),
            "files": files_info
        }
    
    def get_rendered_destination_path(self, empresa: Dict[str, Any]) -> str:
        """
        Obtém o caminho de destino renderizado com os dados da empresa
        
        Args:
            empresa: Dicionário com dados da empresa para substituição de variáveis
        
        Returns:
            Caminho de destino processado com as variáveis substituídas
        """
        return self._get_destination_path(empresa)
    
    def get_info(self, empresa: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Obtém informações sobre configuração atual
        
        Args:
            empresa: Dicionário com dados da empresa para visualizar caminho renderizado
        
        Returns:
            Dict com informações de configuração
        """
        try:
            destination_path_template = self._get_destination_path()
            if empresa:
                destination_path_rendered = self._get_destination_path(empresa)
            else:
                destination_path_rendered = destination_path_template
        except Exception as e:
            destination_path_template = f"ERRO: {str(e)}"
            destination_path_rendered = destination_path_template
        
        info = {
            "current_user": self.current_user,
            "source_folder": self.source_folder,
            "destination_folder_template": destination_path_template,
            "source_exists": os.path.exists(self.source_folder)
        }
        
        if empresa:
            info["destination_folder_rendered"] = destination_path_rendered
            info["empresa_data"] = empresa
        
        return info


# Exemplo de uso
if __name__ == "__main__":
    files_manager = FilesManager()
    
    # Dados de exemplo de uma empresa
    empresa_exemplo = {
        "cnpj": "06097786000193",
        "razao_social": "EMPRESA EXEMPLO LTDA"
    }
    
    # Mostra informações da configuração sem empresa
    print("Informações de configuração (template):")
    info = files_manager.get_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Mostra informações da configuração com empresa (renderizado)
    print("\nInformações de configuração (renderizado com empresa):")
    info_with_empresa = files_manager.get_info(empresa_exemplo)
    for key, value in info_with_empresa.items():
        print(f"  {key}: {value}")
    
    # Exemplo de renderização de caminho
    print(f"\nCaminho renderizado para CNPJ {empresa_exemplo['cnpj']}:")
    rendered_path = files_manager.get_rendered_destination_path(empresa_exemplo)
    print(f"  {rendered_path}")
    
    # Lista arquivos na pasta de origem
    print("\nListando arquivos na pasta de origem:")
    files_list = files_manager.list_files()
    if files_list["success"]:
        print(f"Encontrados {files_list['total_files']} arquivos:")
        for file_info in files_list["files"]:
            print(f"  - {file_info['name']} ({file_info['size']} bytes)")
    else:
        print(f"Erro: {files_list['error']}")
    
    # Exemplo de movimentação de arquivos com template
    # result = files_manager.move_files(empresa=empresa_exemplo)
    # print(f"\nResultado da movimentação: {result['message']}")
