# Sorteio Profissional

Sistema profissional de sorteio para eventos presenciais com interface moderna, animações neon e suporte a múltiplos monitores. Suporta **sorteio de números** e **sorteio de nomes** (digitados ou importados de arquivo).

## Requisitos

- Python 3.11+
- Pip

## Instalação

```bash
pip install -r requirements.txt
```

As dependências opcionais para importação de arquivos são:

- `python-docx` — para ler arquivos `.docx`
- `pypdf` — para ler arquivos `.pdf`

> Arquivos `.csv`, `.txt` e `.odt` (LibreOffice/OpenDocument) são lidos
> apenas com a biblioteca padrão do Python, sem dependências extras.

## Execução

```bash
python main.py
```

## Funcionalidades

- Interface do operador com controles completos
- **Sorteio de números** (interface por faixa/intervalo)
- **Sorteio de nomes** — digite nomes na caixa de texto ou **importe de arquivo**
- Importação de listas de nomes a partir de `.csv`, `.txt`, `.doc`, `.docx`, `.pdf` e `.odt`
  - Diálogo de importação próprio com navegação por pastas (clique simples importa)
- Tela pública com animações neon em segundo monitor
- Sorteio sem repetição com algoritmo eficiente
- Animações com desaceleração progressiva
- Efeitos de partículas e glow no resultado vencedor
- Efeitos sonoros opcionais
- Configurações persistidas em JSON
- Exportação de histórico em CSV/TXT
- Detecção automática de monitores
- Splash screen de carregamento
- Atalhos de teclado
- Tema escuro com detalhes neon (alternável com Ctrl+T)

## Uso do sorteio de nomes

1. No seletor de modo, escolha **Nomes**.
2. Digite os nomes (um por linha) ou clique em **"Importar Arquivos..."** para carregar de um arquivo.
3. Ao sortear, os nomes vão sendo removidos da lista, sem repetição.
4. Terminado, o histórico registra o resultado para exportação.

### Formatos de importação suportados

| Extensão  | Origem                                  | Requer biblioteca extra? |
|-----------|-----------------------------------------|--------------------------|
| `.csv`    | Planilhas / texto separado por vírgula  | Não                       |
| `.txt`    | Texto simples (um nome por linha)       | Não                       |
| `.odt`    | LibreOffice / OpenDocument              | Não                       |
| `.docx`   | Microsoft Word (novo formato)           | `python-docx`            |
| `.pdf`    | Documentos PDF                          | `pypdf`                  |
| `.doc`    | Microsoft Word (formato antigo)         | `textract`/`antiword`    |

> O formato binário antigo `.doc` só é lido se o `textract` (ou o conversor
> `antiword`) estiver instalado no sistema. Prefira `.docx`, `.pdf` ou `.odt`.

## Estrutura

```
Sorteio/
├── main.py                # Ponto de entrada
├── requirements.txt
├── config/settings.json   # Configurações do usuário (gerado em runtime)
├── assets/
│   ├── icons/
│   └── sounds/
├── exports/               # Históricos exportados
├── logs/
└── src/
    ├── app.py              # Coordenador principal
    ├── main_window.py      # Interface do operador
    ├── public_window.py    # Tela pública (segundo monitor)
    ├── animation_engine.py # Sistema de animações e partículas
    ├── lottery_engine.py   # Lógica do sorteio
    ├── name_importer.py    # Leitura de arquivos de nomes (.csv/.txt/.doc/.docx/.pdf/.odt)
    ├── sound_manager.py    # Gerenciamento de áudio
    ├── settings_manager.py # Configurações (JSON)
    ├── theme_manager.py    # Temas e cores neon
    ├── monitor_manager.py  # Detecção de monitores
    ├── history_manager.py  # Histórico e exportação
    ├── font_manager.py     # Gerenciamento de fontes
    ├── validator.py        # Validação de entrada
    └── splash_screen.py    # Tela de abertura
```

## Atalhos

| Tecla      | Ação                   |
|------------|------------------------|
| F11        | Tela cheia             |
| Espaço     | Novo sorteio           |
| ESC        | Sair                   |
| Ctrl+R     | Resetar tudo           |
| Ctrl+E     | Exportar histórico     |
| Ctrl+M     | Minimizar janela       |
| Ctrl+Q     | Sair                   |
| Ctrl+T     | Alternar tema          |

## Compilação (executável)

### Executável com PyInstaller

```bash
./programa.sh
```

Ou manualmente:

```bash
pyinstaller --onefile --noconsole --name "SorteioProfissional" \
    --icon "icone.png" \
    --add-data "assets:assets" \
    --add-data "config:config" \
    --hidden-import customtkinter \
    --hidden-import PIL \
    --hidden-import screeninfo \
    --hidden-import pygame \
    --collect-all customtkinter \
    --collect-all PIL \
    --collect-all screeninfo \
    --collect-all pygame \
    main.py
```

O executável será gerado em `./dist/SorteioProfissional`.

### AppImage (Linux)

Primeiro gere o executável com o PyInstaller e depois:

```bash
./build-appimage.sh
```

O AppImage será gerado em `./dist/SorteioProfissional-x86_64.AppImage`.

## Licença

GPL — desenvolvido por José Edes Neves (2026).
