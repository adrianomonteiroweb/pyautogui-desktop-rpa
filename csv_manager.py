import csv
import os
from typing import List, Dict, Optional


def ler_arquivo_csv(nome_arquivo: str, mostrar_info: bool = True) -> Optional[Dict[str, any]]:
    user = os.environ.get('USERNAME') or os.environ.get('USER')

    import json
    manifest_path = os.path.join(os.path.dirname(__file__), 'manifest.json')

    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
            bot_id = manifest.get('id', '')
    except Exception as e:
        if mostrar_info:
            print(f"Erro ao ler o manifest.json: {e}")
        return None
    if not user or not bot_id:
        if mostrar_info:
            print("Não foi possível obter o usuário ou o id do bot.")
        return None
    
    caminho_base = fr"C:\Users\{user}\AppData\Roaming\hobots\datasets\{bot_id}"
    
    if not nome_arquivo.endswith('.csv'):
        nome_arquivo += '.csv'
    
    caminho_arquivo = os.path.join(caminho_base, nome_arquivo)
    
    try:
        if not os.path.exists(caminho_arquivo):
            if mostrar_info:
                print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
            return None

        dados = []
        colunas = []

        with open(caminho_arquivo, 'r', encoding='utf-8', newline='') as arquivo:
            leitor = csv.DictReader(arquivo, delimiter=';')

            colunas = leitor.fieldnames if leitor.fieldnames else []

            colunas = [col.strip('"').strip() for col in colunas]

            for linha in leitor:
                linha_limpa = {}

                for i, (chave, valor) in enumerate(linha.items()):
                    nome_coluna = colunas[i] if i < len(colunas) else chave.strip('"').strip()
                    valor_limpo = valor.strip('"').strip() if valor else ""
                    linha_limpa[nome_coluna] = valor_limpo

                dados.append(linha_limpa)

        return {
            'dados': dados,
            'colunas': colunas,
            'nome_arquivo': nome_arquivo,
            'total_registros': len(dados)
        }
    
    except FileNotFoundError:
        if mostrar_info:
            print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
        return None
    except PermissionError:
        if mostrar_info:
            print(f"Erro: Sem permissão para ler o arquivo '{caminho_arquivo}'.")
        return None
    except UnicodeDecodeError:
        if mostrar_info:
            print(f"Erro: Problema de codificação ao ler o arquivo '{caminho_arquivo}'. Tentando com encoding ISO-8859-1...")
        try:
            dados = []
            colunas = []
            with open(caminho_arquivo, 'r', encoding='iso-8859-1', newline='') as arquivo:
                leitor = csv.DictReader(arquivo, delimiter=';')
                colunas = leitor.fieldnames if leitor.fieldnames else []
                colunas = [col.strip('"').strip() for col in colunas]
                
                for linha in leitor:
                    linha_limpa = {}
                    for i, (chave, valor) in enumerate(linha.items()):
                        nome_coluna = colunas[i] if i < len(colunas) else chave.strip('"').strip()
                        valor_limpo = valor.strip('"').strip() if valor else ""
                        linha_limpa[nome_coluna] = valor_limpo
                    dados.append(linha_limpa)
            
            if mostrar_info:
                print(f"Arquivo '{nome_arquivo}' lido com sucesso usando ISO-8859-1.")
            return dados
        except Exception as e:
            if mostrar_info:
                print(f"Erro ao ler o arquivo com encoding alternativo: {e}")
            return None
    except Exception as e:
        if mostrar_info:
            print(f"Erro inesperado ao ler o arquivo: {e}")
        return None

def obter_coluna_csv(resultado_csv: Dict[str, any], nome_coluna: str) -> Optional[List[str]]:
    if not resultado_csv or not resultado_csv.get('dados'):
        return None
    
    if nome_coluna not in resultado_csv['colunas']:
        print(f"Coluna '{nome_coluna}' não encontrada. Colunas disponíveis: {', '.join(resultado_csv['colunas'])}")
        return None
    
    return [linha.get(nome_coluna, '') for linha in resultado_csv['dados']]


def filtrar_dados_csv(resultado_csv: Dict[str, any], coluna: str, valor: str) -> Optional[List[Dict[str, str]]]:
    if not resultado_csv or not resultado_csv.get('dados'):
        return None
    
    if coluna not in resultado_csv['colunas']:
        print(f"Coluna '{coluna}' não encontrada. Colunas disponíveis: {', '.join(resultado_csv['colunas'])}")
        return None
    
    valor_busca = valor.lower()
    dados_filtrados = []
    
    for linha in resultado_csv['dados']:
        valor_linha = str(linha.get(coluna, '')).lower()
        if valor_busca in valor_linha:
            dados_filtrados.append(linha)
    
    return dados_filtrados



