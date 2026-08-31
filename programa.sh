#!/bin/bash

set -e

source .venv/bin/activate

pip install -r requirements.txt

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

echo ""
echo "=========================================="
echo " Compilação concluída com sucesso!"
echo " Executável: ./dist/SorteioProfissional"
echo "=========================================="
echo ""

./dist/SorteioProfissional

