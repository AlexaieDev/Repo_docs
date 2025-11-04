#!/bin/bash
# Script para sincronizar documentación de proyectos individuales con repositorio central
# Uso: ./sync-docs.sh [nombre-proyecto] [ruta-proyecto]

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuración
CENTRAL_REPO_URL="https://github.com/tu-usuario/docs-central.git"
CENTRAL_REPO_PATH="/tmp/docs-central"

# Verificar argumentos
if [ "$#" -lt 1 ]; then
    echo -e "${RED}Error: Se requiere el nombre del proyecto${NC}"
    echo "Uso: $0 [nombre-proyecto] [ruta-proyecto-opcional]"
    exit 1
fi

PROJECT_NAME=$1
PROJECT_PATH=${2:-.}

echo -e "${GREEN}🔄 Sincronizando documentación de ${PROJECT_NAME}...${NC}"

# Verificar que existe la carpeta docs en el proyecto
if [ ! -d "$PROJECT_PATH/docs/docs" ]; then
    echo -e "${RED}Error: No se encontró la carpeta docs/docs en $PROJECT_PATH${NC}"
    exit 1
fi

# Clonar o actualizar repo central
if [ -d "$CENTRAL_REPO_PATH" ]; then
    echo -e "${YELLOW}📥 Actualizando repositorio central...${NC}"
    cd $CENTRAL_REPO_PATH
    git pull origin main
else
    echo -e "${YELLOW}📥 Clonando repositorio central...${NC}"
    git clone $CENTRAL_REPO_URL $CENTRAL_REPO_PATH
fi

# Crear carpeta del proyecto si no existe
DEST_PATH="$CENTRAL_REPO_PATH/docs/docs/proyectos/$PROJECT_NAME"
mkdir -p "$DEST_PATH"

# Copiar documentación
echo -e "${YELLOW}📋 Copiando documentación...${NC}"
cp -r "$PROJECT_PATH/docs/docs/"* "$DEST_PATH/"

# Crear o actualizar índice del proyecto en repo central
cat > "$DEST_PATH/index.md" << EOF
# $PROJECT_NAME

> Documentación sincronizada automáticamente desde el repositorio del proyecto

## 📅 Última Sincronización

$(date +"%Y-%m-%d %H:%M:%S")

## 🔗 Repositorio Original

[Ver en GitHub](https://github.com/tu-usuario/$PROJECT_NAME)

## 📚 Contenido

$(ls -1 "$DEST_PATH" | grep -v index.md | sed 's/^/- /')

---

*Esta documentación se sincroniza automáticamente con el repositorio principal del proyecto.*
EOF

# Actualizar navegación en mkdocs.yml si el proyecto no está listado
cd $CENTRAL_REPO_PATH
if ! grep -q "$PROJECT_NAME" docs/mkdocs.yml; then
    echo -e "${YELLOW}📝 Agregando proyecto a la navegación...${NC}"

    # Backup del archivo original
    cp docs/mkdocs.yml docs/mkdocs.yml.bak

    # Agregar proyecto a la navegación (esto es simplificado, podrías usar Python para algo más robusto)
    sed -i "/- Índice de Proyectos: proyectos\/index.md/a\\      - $PROJECT_NAME:\n          - Resumen: proyectos/$PROJECT_NAME/index.md\n          - Getting Started: proyectos/$PROJECT_NAME/getting-started/index.md\n          - API: proyectos/$PROJECT_NAME/api/index.md\n          - Guides: proyectos/$PROJECT_NAME/guides/index.md\n          - Examples: proyectos/$PROJECT_NAME/examples/index.md" docs/mkdocs.yml
fi

# Commit y push
echo -e "${YELLOW}📤 Subiendo cambios...${NC}"
cd $CENTRAL_REPO_PATH
git add .
git commit -m "📚 Update docs for $PROJECT_NAME - $(date +"%Y-%m-%d %H:%M")"

# Preguntar si hacer push
read -p "¿Deseas hacer push al repositorio remoto? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push origin main
    echo -e "${GREEN}✅ Documentación sincronizada exitosamente${NC}"
else
    echo -e "${YELLOW}⚠️  Cambios guardados localmente. Ejecuta 'cd $CENTRAL_REPO_PATH && git push' cuando estés listo${NC}"
fi

# Opcional: Limpiar
read -p "¿Deseas eliminar el repositorio temporal? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf $CENTRAL_REPO_PATH
    echo -e "${GREEN}🧹 Limpieza completada${NC}"
fi

echo -e "${GREEN}✨ ¡Proceso completado!${NC}"