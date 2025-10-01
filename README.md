# RPA - Automação de Calculadora

Este projeto implementa um script de automação RPA (Robotic Process Automation) que realiza operações em uma calculadora usando reconhecimento de imagens.

## Funcionalidades

- Reconhecimento de imagens na tela usando PyAutoGUI
- Sequência automatizada de cliques: 7 + 2 =
- Tratamento de erros robusto
- Feedback visual do progresso
- Validação da existência dos arquivos de imagem

## Requisitos

- Python 3.7+
- pyautogui
- pillow
- opencv-python

## Instalação

```bash
pip install pyautogui pillow opencv-python
```

## Como usar

1. Certifique-se de que a calculadora (ou aplicativo alvo) está visível na tela
2. Execute o script:

```bash
python main.py
```

3. O script irá:
   - Contar de 3 até 1 (tempo para posicionar a tela)
   - Localizar e clicar sequencialmente nas imagens: 7, +, 2, =

## Estrutura do projeto

```
rpa/
├── main.py          # Script principal
├── images/          # Pasta com imagens de referência
│   ├── 7.png       # Imagem do número 7
│   ├── mais.png    # Imagem do botão +
│   ├── 2.png       # Imagem do número 2
│   ├── igual.png   # Imagem do botão =
│   └── icon.png    # Ícone adicional
└── README.md       # Este arquivo
```

## Melhorias implementadas

- ✅ Correção de erro de sintaxe
- ✅ Tratamento de exceções
- ✅ Verificação da existência de arquivos
- ✅ Feedback visual do progresso
- ✅ Uso de confidence para melhor detecção
- ✅ Estrutura modular com funções
- ✅ Documentação do código

## Notas importantes

- As imagens devem estar na pasta `images/`
- O script usa confidence de 0.8 para reconhecimento de imagens
- Pequenas pausas entre cliques para garantir responsividade
- O script para se alguma imagem não for encontrada
