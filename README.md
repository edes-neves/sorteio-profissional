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
- **Tela pública personalizável** — cor de fundo, cores de textos/títulos e transparência configuráveis (menu **Configurações** → **Tela Pública**)
- Sorteio sem repetição com algoritmo eficiente
- Animações com desaceleração progressiva
- Efeitos de partículas e glow no resultado vencedor
- Efeitos sonoros opcionais
- Configurações persistidas em JSON
- Exportação de histórico em CSV/TXT
- Detecção automática de monitores
- **Verificação automática de atualizações** — ao abrir, o app consulta o GitHub; se houver versão nova, mostra as melhorias e oferece o download para a pasta Downloads
- **Menu "Preciso de ajuda"** (menu **Sobre**) — abre um email de suporte para o desenvolvedor
- Splash screen de carregamento
- Atalhos de teclado
- Tema escuro com detalhes neon (alternável com Ctrl+T)

## Menu Exibir

O menu **Exibir** na parte superior da janela principal reúne as opções de visualização:

- **Alternar Tema** (Ctrl+T) — alterna entre os temas escuro e claro
- **Tela Cheia (F11)** — ativa/desativa a tela cheia da tela pública
- **Minimizar/Restaurar Tela Pública** (Ctrl+M) — mostra ou oculta a tela pública

No menu **Sobre** há ainda a opção **Preciso de ajuda**, que abre um email de
suporte para `nevestecnologias@gmail.com`.

## Atualização automática

Ao abrir o Sorteio Profissional, ele verifica automaticamente no GitHub se
existe uma versão mais nova:

1. Se houver, uma janela avisa com a **descrição das melhorias** da nova versão.
2. Ao clicar em **"Sim, baixar"**, o novo AppImage é baixado para a **pasta
   Downloads** com barra de progresso.
3. Ao terminar, são exibidas as **instruções para instalação** da nova versão.

A verificação é silenciosa quando não há atualização (ou sem internet), e não
atrapalha o uso do programa.

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
    ├── updater.py          # Verificação de atualizações no GitHub
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
