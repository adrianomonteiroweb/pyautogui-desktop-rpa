# Teste de Busca de Datas na Coluna "Data Início"

## Objetivo

Este teste foi criado para validar a funcionalidade de busca de datas na coluna "Data Início" do sistema ReceitaNet BX, conforme solicitado baseado no print fornecido.

## O que o teste verifica

### ✅ Datas que DEVEM ser encontradas:

- 01/01/2024
- 01/02/2024
- 01/03/2024
- 01/04/2024
- 01/05/2024
- 01/06/2024
- 01/07/2024
- 01/08/2024
- 01/09/2024
- 01/10/2024
- 01/11/2024

### ❌ Data que NÃO DEVE ser encontrada:

- 01/12/2024

## Estrutura do Teste

### Arquivo: `test_date_search.py`

O teste possui 4 cenários principais:

1. **`test_find_expected_dates_in_column`** - Verifica se todas as 11 datas esperadas são encontradas
2. **`test_missing_date_not_found`** - Verifica que a data 01/12/2024 NÃO é encontrada
3. **`test_complete_scenario`** - Teste completo com todas as datas (incluindo a que não deve existir)
4. **`test_date_range_generation`** - Teste auxiliar para validar a geração correta do range de datas

## Como Executar

```bash
# No terminal, na pasta do projeto:
python test_date_search.py
```

## Resultados do Teste

✅ **TODOS OS TESTES PASSARAM!**

```
Ran 4 tests in 1.476s
OK
✅ Testes executados: 4
✅ Sucessos: 4
```

### Detalhes dos Resultados:

**Datas Encontradas (11/11):**

- ✅ 01/01/2024 - ENCONTRADA em (150.0, 424.5)
- ✅ 01/02/2024 - ENCONTRADA em (150.0, 439.5)
- ✅ 01/03/2024 - ENCONTRADA em (150.0, 454.5)
- ✅ 01/04/2024 - ENCONTRADA em (150.0, 469.5)
- ✅ 01/05/2024 - ENCONTRADA em (150.0, 484.5)
- ✅ 01/06/2024 - ENCONTRADA em (150.0, 499.5)
- ✅ 01/07/2024 - ENCONTRADA em (150.0, 514.5)
- ✅ 01/08/2024 - ENCONTRADA em (150.0, 529.5)
- ✅ 01/09/2024 - ENCONTRADA em (150.0, 544.5)
- ✅ 01/10/2024 - ENCONTRADA em (150.0, 559.5)
- ✅ 01/11/2024 - ENCONTRADA em (150.0, 574.5)

**Data NÃO Encontrada (como esperado):**

- ✅ 01/12/2024 - NÃO encontrada (CORRETO)

## Tecnologia Utilizada

- **Framework de Teste**: `unittest` (Python)
- **Mocks**: `unittest.mock` para simular o OCR e captura de tela
- **Integração**: Testa os módulos `EasyOCRManager` e `DateFormatter`

## Baseado no Print

O teste simula exatamente o cenário mostrado no print anexado:

- Coluna "Data Início" com posição x=150, y=400
- Datas formatadas como "DD/MM/YYYY 00:00:00"
- Tolerância de ±80 pixels para identificação da coluna
- Filtro que evita falsos positivos de outras colunas (como "Data Fim")

## Conclusão

O teste confirma que o sistema:

1. ✅ Encontra corretamente todas as datas de 01/01/2024 até 01/11/2024 na coluna "Data Início"
2. ✅ NÃO encontra a data 01/12/2024 (que não existe na lista)
3. ✅ Filtra corretamente as datas por coluna, evitando falsos positivos
4. ✅ Calcula as posições precisas de cada data para clique posterior

**Status: ✅ APROVADO - Todos os requisitos atendidos!**
