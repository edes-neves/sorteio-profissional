#!/bin/bash

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

APP_NAME="SorteioProfissional"
DIST_DIR="$PROJECT_DIR/dist"
EXECUTABLE="$DIST_DIR/$APP_NAME"

APPDIR="$PROJECT_DIR/AppDir"
TOOLS_DIR="$PROJECT_DIR/.appimage-tools"

LINUXDEPLOY="$TOOLS_DIR/linuxdeploy-x86_64.AppImage"
FINAL_APPIMAGE="$DIST_DIR/${APP_NAME}-x86_64.AppImage"

ICON="$PROJECT_DIR/icone.png"

echo ""
echo "============================================================"
echo "       SORTEIO PROFISSIONAL - GERADOR DE APPIMAGE"
echo "============================================================"
echo ""

echo "[INFO] Projeto:"
echo "       $PROJECT_DIR"
echo ""

# ------------------------------------------------------------

# Arquitetura

# ------------------------------------------------------------

ARCH="$(uname -m)"

if [ "$ARCH" != "x86_64" ]; then
echo "[ERRO] Arquitetura incompatível: $ARCH"
exit 1
fi

echo "[OK] Arquitetura x86_64 detectada."

# ------------------------------------------------------------

# Dependências

# ------------------------------------------------------------

echo "[INFO] Verificando dependências..."

if ! command -v wget >/dev/null 2>&1; then
echo "[ERRO] wget não está instalado."
echo ""
echo "Execute:"
echo "sudo apt update"
echo "sudo apt install wget"
exit 1
fi

if ! command -v file >/dev/null 2>&1; then
echo "[ERRO] file não está instalado."
echo ""
echo "Execute:"
echo "sudo apt update"
echo "sudo apt install file"
exit 1
fi

echo "[OK] Dependências encontradas."

# ------------------------------------------------------------

# Executável

# ------------------------------------------------------------

if [ ! -f "$EXECUTABLE" ]; then
echo "[ERRO] Executável não encontrado:"
echo "$EXECUTABLE"
echo ""
echo "Execute primeiro o PyInstaller."
exit 1
fi

echo "[OK] Executável encontrado."

# ------------------------------------------------------------

# Ícone

# ------------------------------------------------------------

if [ ! -f "$ICON" ]; then
echo "[ERRO] Ícone não encontrado:"
echo "$ICON"
exit 1
fi

echo "[OK] Ícone encontrado."

# ------------------------------------------------------------

# Diretórios

# ------------------------------------------------------------

echo "[INFO] Criando diretórios..."

mkdir -p "$TOOLS_DIR"
mkdir -p "$DIST_DIR"

echo "[OK] Diretórios preparados."

# ------------------------------------------------------------

# Linuxdeploy

# ------------------------------------------------------------

if [ ! -f "$LINUXDEPLOY" ]; then

```
echo "[INFO] linuxdeploy não encontrado."
echo "[INFO] Baixando linuxdeploy..."
echo ""

wget \
    --progress=bar:force \
    -O "$LINUXDEPLOY" \
    "https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage"

chmod +x "$LINUXDEPLOY"

echo ""
echo "[OK] linuxdeploy baixado."
```

else


echo "[OK] linuxdeploy já está disponível."

chmod +x "$LINUXDEPLOY"


fi

# ------------------------------------------------------------

# AppDir

# ------------------------------------------------------------

echo "[INFO] Limpando AppDir anterior..."

rm -rf "$APPDIR"

mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"

echo "[OK] AppDir preparado."

# ------------------------------------------------------------

# Executável

# ------------------------------------------------------------

echo "[INFO] Copiando executável..."

cp "$EXECUTABLE" "$APPDIR/usr/bin/$APP_NAME"

chmod +x "$APPDIR/usr/bin/$APP_NAME"

echo "[OK] Executável copiado."

# ------------------------------------------------------------

# Ícone

# ------------------------------------------------------------

echo "[INFO] Copiando ícone..."

cp "$ICON" "$APPDIR/usr/share/icons/hicolor/256x256/apps/$APP_NAME.png"

cp "$ICON" "$APPDIR/$APP_NAME.png"

echo "[OK] Ícone copiado."

# ------------------------------------------------------------

# Desktop

# ------------------------------------------------------------

echo "[INFO] Criando arquivo .desktop..."

cat > "$APPDIR/$APP_NAME.desktop" <<EOF
[Desktop Entry]
Name=Sorteio Profissional
Comment=Aplicativo profissional de sorteios
Exec=$APP_NAME
Icon=$APP_NAME
Type=Application
Categories=Utility;
Terminal=false
StartupNotify=true
EOF

cp "$APPDIR/$APP_NAME.desktop" \
"$APPDIR/usr/share/applications/$APP_NAME.desktop"

echo "[OK] Arquivo .desktop criado."

# ------------------------------------------------------------

# Gerar AppImage

# ------------------------------------------------------------

echo "============================================================"
echo "              GERANDO APPIMAGE"
echo "============================================================"
echo ""

echo "[INFO] Executando linuxdeploy..."
echo ""

cd "$PROJECT_DIR"

"$LINUXDEPLOY" --appdir="$APPDIR" --executable="$APPDIR/usr/bin/$APP_NAME" --desktop-file="$APPDIR/$APP_NAME.desktop" --icon-file="$APPDIR/$APP_NAME.png" --output=appimage

echo ""
echo "[OK] linuxdeploy terminou."

# ------------------------------------------------------------

# Localizar AppImage

# ------------------------------------------------------------

GENERATED=""

for FILE in "$PROJECT_DIR"/*.AppImage; do
if [ -f "$FILE" ]; then
GENERATED="$FILE"
break
fi
done

if [ -z "$GENERATED" ]; then
echo "[ERRO] Nenhum AppImage foi encontrado."
exit 1
fi

# ------------------------------------------------------------

# Mover para dist

# ------------------------------------------------------------

echo "[INFO] Movendo AppImage para dist..."

rm -f "$FINAL_APPIMAGE"

mv "$GENERATED" "$FINAL_APPIMAGE"

chmod +x "$FINAL_APPIMAGE"

SIZE="$(du -h "$FINAL_APPIMAGE" | cut -f1)"

# ------------------------------------------------------------

# Final

# ------------------------------------------------------------

echo ""
echo "============================================================"
echo "          APPIMAGE GERADO COM SUCESSO!"
echo "============================================================"
echo ""
echo "Arquivo:"
echo "  $FINAL_APPIMAGE"
echo ""
echo "Tamanho:"
echo "  $SIZE"
echo ""
echo "Executar:"
echo "  ./dist/${APP_NAME}-x86_64.AppImage"
echo ""
echo "============================================================"
echo ""
echo "[OK] Processo concluído."
echo ""

