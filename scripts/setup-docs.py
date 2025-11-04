#!/usr/bin/env python3
"""
Script para automatizar la configuración de documentación en proyectos.
Uso: python setup-docs.py --project-name "Mi Proyecto" --type [individual|central]
"""

import argparse
import os
import json
import shutil
from pathlib import Path

def create_project_structure(project_name, project_path="."):
    """Crea la estructura de directorios para la documentación"""

    docs_dirs = [
        "docs/docs/getting-started",
        "docs/docs/api",
        "docs/docs/guides",
        "docs/docs/examples"
    ]

    for dir_path in docs_dirs:
        Path(os.path.join(project_path, dir_path)).mkdir(parents=True, exist_ok=True)
        print(f"✅ Creado: {dir_path}")

    return True

def create_mkdocs_config(project_name, project_path=".", is_multi=False):
    """Genera el archivo mkdocs.yml"""

    if is_multi:
        config = f"""site_name: Centro de Documentación - {project_name}
site_description: Documentación consolidada de proyectos
site_url: https://tu-usuario.github.io/docs/

repo_url: https://github.com/tu-usuario/docs
edit_uri: edit/main/docs/docs

theme: readthedocs

nav:
  - 🏠 Inicio: index.md
  - 📚 Proyectos: proyectos/index.md
  # Agregar más proyectos aquí
"""
    else:
        config = f"""site_name: {project_name}
site_description: Documentación de {project_name}
site_url: https://tu-usuario.github.io/{project_name.lower().replace(' ', '-')}/

repo_url: https://github.com/tu-usuario/{project_name.lower().replace(' ', '-')}
edit_uri: edit/main/docs/docs

theme: readthedocs

nav:
  - 🏠 Inicio: index.md
  - 🚀 Getting Started:
      - Instalación: getting-started/installation.md
      - Configuración: getting-started/configuration.md
      - Quick Start: getting-started/quickstart.md
  - 📡 API Reference:
      - Endpoints: api/endpoints.md
      - Autenticación: api/authentication.md
      - Ejemplos: api/examples.md
  - 📖 Guides:
      - Desarrollo: guides/development.md
      - Testing: guides/testing.md
      - Deployment: guides/deployment.md
  - 💡 Examples:
      - Básico: examples/basic.md
      - Avanzado: examples/advanced.md
"""

    config_path = os.path.join(project_path, "docs", "mkdocs.yml")
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config)

    print(f"✅ Creado: docs/mkdocs.yml")
    return config_path

def create_requirements(project_path="."):
    """Crea el archivo requirements.txt"""

    requirements = """mkdocs~=1.1,!=1.2
# Temas opcionales (descomenta el que prefieras)
# mkdocs-material>=8.0
# mkdocs-gitbook>=1.0
# mkdocs-rtd-dropdown>=1.0

# Plugins opcionales
# mkdocs-mermaid2-plugin  # Para diagramas
# mkdocs-pdf-export-plugin  # Para exportar a PDF
# mkdocs-minify-plugin  # Para minificar HTML
"""

    req_path = os.path.join(project_path, "docs", "requirements.txt")
    with open(req_path, "w") as f:
        f.write(requirements)

    print(f"✅ Creado: docs/requirements.txt")
    return req_path

def create_github_action(project_path="."):
    """Crea el workflow de GitHub Actions"""

    workflow = """name: Deploy Docs

on:
  push:
    branches:
      - main
      - master

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'

      - name: Cache dependencies
        uses: actions/cache@v2
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('docs/requirements.txt') }}

      - name: Install dependencies
        run: |
          cd docs
          pip install -r requirements.txt

      - name: Build and deploy
        run: |
          cd docs
          mkdocs gh-deploy --force
"""

    workflow_dir = os.path.join(project_path, ".github", "workflows")
    Path(workflow_dir).mkdir(parents=True, exist_ok=True)

    workflow_path = os.path.join(workflow_dir, "docs.yml")
    with open(workflow_path, "w") as f:
        f.write(workflow)

    print(f"✅ Creado: .github/workflows/docs.yml")
    return workflow_path

def create_sample_content(project_name, project_path="."):
    """Crea contenido de ejemplo"""

    # Index principal
    index_content = f"""# {project_name}

## 📖 Descripción

Bienvenido a la documentación de {project_name}.

## ⚡ Características Principales

- ✨ Característica 1
- 🚀 Característica 2
- 🔧 Característica 3
- 📊 Característica 4

## 🚀 Quick Start

```bash
# Instalación rápida
pip install {project_name.lower().replace(' ', '-')}
```

## 📚 Secciones de Documentación

- [🚀 Getting Started](getting-started/installation.md) - Comienza aquí
- [📡 API Reference](api/endpoints.md) - Documentación de la API
- [📖 Guides](guides/development.md) - Guías detalladas
- [💡 Examples](examples/basic.md) - Ejemplos de código

## 📊 Estado del Proyecto

- **Versión:** 1.0.0
- **Estado:** 🟢 Desarrollo Activo
- **Licencia:** MIT
- **Última Actualización:** 2024

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor, lee nuestra [guía de contribución](guides/contributing.md).

## 📝 Licencia

Este proyecto está bajo licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.
"""

    index_path = os.path.join(project_path, "docs", "docs", "index.md")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_content)

    print(f"✅ Creado: docs/docs/index.md")

    # Getting Started - Installation
    installation_content = f"""# 🚀 Instalación

## Requisitos Previos

Antes de instalar {project_name}, asegúrate de tener:

- Python 3.7 o superior
- pip (gestor de paquetes de Python)
- Git (opcional, para instalación desde fuente)

## Métodos de Instalación

### Opción 1: Usando pip (Recomendado)

```bash
pip install {project_name.lower().replace(' ', '-')}
```

### Opción 2: Desde el código fuente

```bash
git clone https://github.com/tu-usuario/{project_name.lower().replace(' ', '-')}.git
cd {project_name.lower().replace(' ', '-')}
pip install -e .
```

### Opción 3: Usando Docker

```bash
docker pull tu-usuario/{project_name.lower().replace(' ', '-')}:latest
docker run -it tu-usuario/{project_name.lower().replace(' ', '-')}
```

## Verificar Instalación

```bash
python -c "import {project_name.lower().replace(' ', '_').replace('-', '_')}; print({project_name.lower().replace(' ', '_').replace('-', '_')}.__version__)"
```

## Próximos Pasos

- [Configuración](configuration.md)
- [Quick Start](quickstart.md)
- [Ejemplos](../examples/basic.md)

## Solución de Problemas

Si encuentras problemas durante la instalación:

1. Verifica que tu versión de Python sea compatible
2. Actualiza pip: `pip install --upgrade pip`
3. Consulta la sección de [FAQ](../guides/faq.md)
4. Abre un [issue en GitHub](https://github.com/tu-usuario/{project_name.lower().replace(' ', '-')}/issues)
"""

    installation_path = os.path.join(project_path, "docs", "docs", "getting-started", "installation.md")
    with open(installation_path, "w", encoding="utf-8") as f:
        f.write(installation_content)

    print(f"✅ Creado: docs/docs/getting-started/installation.md")

    return True

def create_makefile(project_path="."):
    """Crea un Makefile para comandos comunes"""

    makefile_content = """# Makefile para gestión de documentación

.PHONY: help install serve build deploy clean

help:
	@echo "Comandos disponibles:"
	@echo "  make install  - Instala las dependencias"
	@echo "  make serve    - Inicia servidor de desarrollo"
	@echo "  make build    - Construye el sitio estático"
	@echo "  make deploy   - Despliega a GitHub Pages"
	@echo "  make clean    - Limpia archivos generados"

install:
	cd docs && pip install -r requirements.txt

serve:
	cd docs && mkdocs serve --strict

build:
	cd docs && mkdocs build --strict

deploy:
	cd docs && mkdocs gh-deploy --force

clean:
	rm -rf docs/site/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
"""

    makefile_path = os.path.join(project_path, "Makefile")
    with open(makefile_path, "w") as f:
        f.write(makefile_content)

    print(f"✅ Creado: Makefile")
    return makefile_path

def main():
    parser = argparse.ArgumentParser(description="Configurar documentación para proyectos")
    parser.add_argument("--project-name", required=True, help="Nombre del proyecto")
    parser.add_argument("--type", choices=["individual", "central"], default="individual",
                       help="Tipo de documentación: individual para un proyecto o central para múltiples")
    parser.add_argument("--path", default=".", help="Ruta donde crear la documentación")
    parser.add_argument("--theme", default="readthedocs",
                       choices=["readthedocs", "material", "gitbook"],
                       help="Tema de MkDocs a utilizar")

    args = parser.parse_args()

    print(f"\n🚀 Configurando documentación para: {args.project_name}")
    print(f"📁 Tipo: {args.type}")
    print(f"📂 Ubicación: {os.path.abspath(args.path)}\n")

    # Crear estructura
    create_project_structure(args.project_name, args.path)

    # Crear archivos de configuración
    create_mkdocs_config(args.project_name, args.path, is_multi=(args.type == "central"))
    create_requirements(args.path)
    create_github_action(args.path)
    create_makefile(args.path)

    # Crear contenido de ejemplo
    create_sample_content(args.project_name, args.path)

    print("\n✨ ¡Configuración completada!")
    print("\n📋 Próximos pasos:")
    print("1. cd " + args.path)
    print("2. make install  # Instalar dependencias")
    print("3. make serve    # Iniciar servidor local")
    print("4. Visitar http://localhost:8000")
    print("\n💡 Para desplegar en GitHub Pages:")
    print("   make deploy")

    # Crear archivo de instrucciones
    readme_path = os.path.join(args.path, "docs", "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(f"""# Documentación de {args.project_name}

## 🚀 Inicio Rápido

```bash
# Instalar dependencias
make install

# Servidor de desarrollo
make serve

# Construir sitio
make build

# Desplegar a GitHub Pages
make deploy
```

## 📁 Estructura

- `mkdocs.yml` - Configuración principal
- `requirements.txt` - Dependencias Python
- `docs/` - Contenido en Markdown
  - `index.md` - Página principal
  - `getting-started/` - Guías de inicio
  - `api/` - Documentación de API
  - `guides/` - Guías detalladas
  - `examples/` - Ejemplos de código

## 🎨 Personalización

Edita `mkdocs.yml` para:
- Cambiar el tema
- Modificar la navegación
- Agregar plugins
- Configurar búsqueda

## 📝 Licencia

MIT
""")

    print(f"\n📄 Documentación de configuración guardada en: docs/README.md")

if __name__ == "__main__":
    main()