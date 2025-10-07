import csv
import os
from typing import List, Dict, Optional


def ler_arquivo_csv(nome_arquivo: str, mostrar_info: bool = True) -> Optional[Dict[str, any]]:
    # Define o caminho base
    caminho_base = r"C:\Users\adria\Documents\hobots\abax"
    
    # Adiciona extensão .csv se não estiver presente
    if not nome_arquivo.endswith('.csv'):
        nome_arquivo += '.csv'
    
    # Constrói o caminho completo do arquivo
    caminho_arquivo = os.path.join(caminho_base, nome_arquivo)
    
    try:
        # Verifica se o arquivo existe
        if not os.path.exists(caminho_arquivo):
            if mostrar_info:
                print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
            return None
        
        # Lista para armazenar os dados
        dados = []
        colunas = []
        
        # Lê o arquivo CSV
        with open(caminho_arquivo, 'r', encoding='utf-8', newline='') as arquivo:
            # Usa ponto e vírgula como delimitador
            leitor = csv.DictReader(arquivo, delimiter=';')
            
            # Obtém os nomes das colunas dinamicamente
            colunas = leitor.fieldnames if leitor.fieldnames else []
            
            # Remove aspas dos nomes das colunas se existirem
            colunas = [col.strip('"').strip() for col in colunas]
            
            # Converte cada linha em um dicionário
            for linha in leitor:
                # Limpa as aspas dos valores e cria novo dicionário com colunas limpas
                linha_limpa = {}
                for i, (chave, valor) in enumerate(linha.items()):
                    nome_coluna = colunas[i] if i < len(colunas) else chave.strip('"').strip()
                    valor_limpo = valor.strip('"').strip() if valor else ""
                    linha_limpa[nome_coluna] = valor_limpo
                dados.append(linha_limpa)
        
        if mostrar_info:
            print(f"Arquivo '{nome_arquivo}' lido com sucesso.")
        
        return dados
    
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


def exibir_dados_csv(resultado_csv: Dict[str, any]) -> None:
    """
    Exibe os dados do CSV de forma formatada
    
    Args:
        resultado_csv (Dict[str, any]): Resultado retornado pela função ler_arquivo_csv
    """
    if not resultado_csv or not resultado_csv.get('dados'):
        print("Nenhum dado para exibir.")
        return
    
    dados = resultado_csv['dados']
    colunas = resultado_csv['colunas']
    
    # Calcula a largura de cada coluna para melhor formatação
    larguras = {}
    for coluna in colunas:
        # Largura mínima é o tamanho do nome da coluna
        largura_max = len(coluna)
        # Verifica o tamanho dos valores na coluna
        for linha in dados:
            valor = str(linha.get(coluna, ''))
            if len(valor) > largura_max:
                largura_max = len(valor)
        larguras[coluna] = min(largura_max, 50)  # Limita a 50 caracteres
    
    # Exibe informações do arquivo
    print(f"\n=== {resultado_csv['nome_arquivo']} ===")
    print(f"Total de registros: {resultado_csv['total_registros']}")
    print(f"Colunas: {len(colunas)}")
    print()
    
    # Exibe o cabeçalho
    cabecalho = " | ".join([coluna.ljust(larguras[coluna]) for coluna in colunas])
    print(cabecalho)
    print("-" * len(cabecalho))
    
    # Exibe os dados
    for i, linha in enumerate(dados, 1):
        valores = []
        for coluna in colunas:
            valor = str(linha.get(coluna, ''))
            # Trunca valores muito longos
            if len(valor) > larguras[coluna]:
                valor = valor[:larguras[coluna]-3] + "..."
            valores.append(valor.ljust(larguras[coluna]))
        print(" | ".join(valores))
        
        # Limita a exibição a 20 linhas por padrão
        if i >= 20:
            restantes = len(dados) - 20
            if restantes > 0:
                print(f"... e mais {restantes} registros")
            break


def obter_coluna_csv(resultado_csv: Dict[str, any], nome_coluna: str) -> Optional[List[str]]:
    """
    Obtém todos os valores de uma coluna específica
    
    Args:
        resultado_csv (Dict[str, any]): Resultado retornado pela função ler_arquivo_csv
        nome_coluna (str): Nome da coluna a ser extraída
    
    Returns:
        Optional[List[str]]: Lista com todos os valores da coluna ou None se não encontrada
    """
    if not resultado_csv or not resultado_csv.get('dados'):
        return None
    
    if nome_coluna not in resultado_csv['colunas']:
        print(f"Coluna '{nome_coluna}' não encontrada. Colunas disponíveis: {', '.join(resultado_csv['colunas'])}")
        return None
    
    return [linha.get(nome_coluna, '') for linha in resultado_csv['dados']]


def filtrar_dados_csv(resultado_csv: Dict[str, any], coluna: str, valor: str) -> Optional[List[Dict[str, str]]]:
    """
    Filtra os dados do CSV por um valor específico em uma coluna
    
    Args:
        resultado_csv (Dict[str, any]): Resultado retornado pela função ler_arquivo_csv
        coluna (str): Nome da coluna para filtrar
        valor (str): Valor a ser buscado (busca parcial, case-insensitive)
    
    Returns:
        Optional[List[Dict[str, str]]]: Lista de registros que atendem ao filtro
    """
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


# Exemplo de uso
if __name__ == "__main__":
    # Teste do método
    resultado = ler_arquivo_csv("exemplo")  # Lê o arquivo exemplo.csv
    if resultado:
        # Exibe informações do arquivo
        print(f"Arquivo: {resultado['nome_arquivo']}")
        print(f"Colunas encontradas: {resultado['colunas']}")
        print(f"Total de registros: {resultado['total_registros']}")
        
        # Exibe os dados formatados
        exibir_dados_csv(resultado)
        
        # Exemplo de acesso dinâmico aos dados
        print("\nExemplo de acesso dinâmico aos dados:")
        dados = resultado['dados']
        colunas = resultado['colunas']
        
        for i, registro in enumerate(dados[:3]):  # Mostra apenas os 3 primeiros
            print(f"\nRegistro {i+1}:")
            for coluna in colunas:
                valor = registro.get(coluna, 'N/A')
                print(f"  {coluna}: {valor}")
        
        # Exemplo de uso das funções auxiliares
        if 'nome' in colunas:
            print("\nTodos os nomes:")
            nomes = obter_coluna_csv(resultado, 'nome')
            for nome in nomes[:5]:  # Mostra apenas os 5 primeiros
                print(f"  - {nome}")
        
        # Exemplo de filtro
        if 'nome' in colunas:
            filtrados = filtrar_dados_csv(resultado, 'nome', 'empresa')
            if filtrados:
                print(f"\nRegistros com 'empresa' no nome: {len(filtrados)}")
                for registro in filtrados[:2]:  # Mostra apenas os 2 primeiros
                    print(f"  - {registro.get('nome', 'N/A')}")
    else:
        print("Não foi possível ler o arquivo CSV.")
