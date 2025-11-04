#!/usr/bin/env python3
"""
Script de Agregación de Documentación Multi-Proyecto
=====================================================
Este script escanea múltiples proyectos y agrega su documentación
en un sitio MkDocs centralizado.
"""

import os
import sys
import yaml
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import argparse

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocumentationAggregator:
    """Agregador principal de documentación multi-proyecto"""

    def __init__(self, base_dir: Path, output_dir: Path):
        self.base_dir = base_dir
        self.output_dir = output_dir
        self.docs_dir = output_dir / "docs" / "docs"
        self.projects_dir = self.docs_dir / "proyectos"
        self.projects: List[Dict[str, Any]] = []

    def setup_directories(self):
        """Crear estructura de directorios necesaria"""
        logger.info("Configurando estructura de directorios...")
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    def find_project_branches(self) -> List[str]:
        """Encontrar todas las ramas de documentación de proyectos"""
        logger.info("Buscando ramas de documentación...")

        # Obtener lista de ramas remotas
        result = subprocess.run(
            ["git", "branch", "-r"],
            capture_output=True,
            text=True,
            cwd=self.base_dir
        )

        branches = []
        for line in result.stdout.splitlines():
            line = line.strip()
            # Buscar ramas con formato: origin/docs/*
            if "origin/docs/" in line:
                branch_name = line.replace("origin/", "")
                branches.append(branch_name)
                logger.info(f"  Encontrada rama: {branch_name}")

        return branches

    def checkout_branch(self, branch: str) -> Optional[Path]:
        """Checkout de una rama específica en directorio temporal"""
        temp_dir = Path(f"/tmp/docs-branch-{branch.replace('/', '-')}")

        if temp_dir.exists():
            shutil.rmtree(temp_dir)

        logger.info(f"Clonando rama {branch}...")

        # Clonar solo la rama específica
        result = subprocess.run(
            [
                "git", "clone",
                "--single-branch",
                "--branch", branch,
                "--depth", "1",
                str(self.base_dir),
                str(temp_dir)
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            logger.error(f"Error al clonar rama {branch}: {result.stderr}")
            return None

        return temp_dir

    def read_project_config(self, project_path: Path) -> Optional[Dict[str, Any]]:
        """Leer configuración docs.yaml del proyecto"""
        config_path = project_path / "docs.yaml"

        if not config_path.exists():
            logger.warning(f"No se encontró docs.yaml en {project_path}")
            return None

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            # Validar campos requeridos
            required = ['project', 'documentation']
            for field in required:
                if field not in config:
                    logger.error(f"Campo requerido '{field}' faltante en {config_path}")
                    return None

            return config

        except Exception as e:
            logger.error(f"Error al leer {config_path}: {e}")
            return None

    def copy_project_docs(self, project_config: Dict, source_path: Path, project_slug: str):
        """Copiar documentación del proyecto al sitio central"""
        logger.info(f"Copiando documentación de {project_slug}...")

        project_dest = self.projects_dir / project_slug
        project_dest.mkdir(parents=True, exist_ok=True)

        # Crear archivo índice del proyecto
        self.create_project_index(project_config, project_dest)

        # Procesar estructura de documentación
        doc_structure = project_config.get('documentation', {}).get('structure', [])

        for item in doc_structure:
            source = source_path / item['source']
            title = item['title']
            item_type = item.get('type', 'file')

            if item_type == 'directory' and source.is_dir():
                # Copiar directorio completo
                dest_dir = project_dest / Path(item['source']).name
                if dest_dir.exists():
                    shutil.rmtree(dest_dir)
                shutil.copytree(source, dest_dir)
                logger.info(f"  Copiado directorio: {item['source']}")

            elif source.is_file():
                # Copiar archivo individual
                dest_file = project_dest / Path(item['source']).name
                shutil.copy2(source, dest_file)
                logger.info(f"  Copiado archivo: {item['source']}")

        # Copiar assets adicionales
        assets = project_config.get('documentation', {}).get('assets', [])
        for asset in assets:
            asset_path = source_path / asset
            if asset_path.exists():
                if asset_path.is_dir():
                    dest_dir = project_dest / Path(asset).name
                    if dest_dir.exists():
                        shutil.rmtree(dest_dir)
                    shutil.copytree(asset_path, dest_dir)
                else:
                    shutil.copy2(asset_path, project_dest / Path(asset).name)
                logger.info(f"  Copiado asset: {asset}")

    def create_project_index(self, config: Dict, dest_path: Path):
        """Crear archivo índice del proyecto"""
        project_info = config['project']

        index_content = f"""# {project_info['name']}

## 📋 Información del Proyecto

**Descripción:** {project_info.get('description', 'Sin descripción')}

**Estado:** {project_info.get('status', 'development')}

**Versión:** {project_info.get('version', '0.0.0')}

**Repositorio:** [{project_info.get('repository', 'No especificado')}]({project_info.get('repository', '#')})

## 🛠️ Stack Tecnológico

"""

        # Agregar tecnologías
        technologies = project_info.get('technologies', [])
        for tech in technologies:
            if isinstance(tech, dict):
                index_content += f"- **{tech.get('name', 'Unknown')}** {tech.get('version', '')}\n"
            else:
                index_content += f"- {tech}\n"

        index_content += """

## 📚 Documentación Disponible

"""

        # Agregar enlaces a secciones
        doc_structure = config.get('documentation', {}).get('structure', [])
        for item in doc_structure:
            icon = item.get('icon', '📄')
            title = item['title']
            source = Path(item['source']).name
            index_content += f"- {icon} [{title}](./{source})\n"

        # Agregar metadata
        index_content += f"""

---

*Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        # Escribir archivo
        index_file = dest_path / "index.md"
        index_file.write_text(index_content, encoding='utf-8')

    def aggregate_from_local_projects(self, project_dirs: List[Path]):
        """Agregar documentación de proyectos locales (para desarrollo)"""
        logger.info("Agregando documentación de proyectos locales...")

        for project_dir in project_dirs:
            if not project_dir.exists():
                logger.warning(f"Directorio no encontrado: {project_dir}")
                continue

            config = self.read_project_config(project_dir)
            if config:
                project_slug = config['project']['slug']
                self.copy_project_docs(config, project_dir, project_slug)
                self.projects.append(config)

    def aggregate_from_branches(self):
        """Agregar documentación desde ramas de Git"""
        logger.info("Agregando documentación desde ramas...")

        branches = self.find_project_branches()

        for branch in branches:
            temp_path = self.checkout_branch(branch)
            if temp_path:
                config = self.read_project_config(temp_path)
                if config:
                    project_slug = config['project']['slug']
                    self.copy_project_docs(config, temp_path, project_slug)
                    self.projects.append(config)

                # Limpiar directorio temporal
                shutil.rmtree(temp_path)

    def generate_mkdocs_config(self):
        """Generar archivo mkdocs.yml actualizado"""
        logger.info("Generando configuración MkDocs...")

        # Configuración base
        mkdocs_config = {
            'site_name': 'Centro de Documentación',
            'site_description': 'Documentación consolidada de todos los proyectos',
            'site_url': 'https://tu-usuario.github.io/docs/',
            'repo_url': 'https://github.com/tu-usuario/docs',
            'edit_uri': 'edit/main/docs/docs',
            'theme': {
                'name': 'material',
                'palette': {
                    'primary': 'blue',
                    'accent': 'blue'
                },
                'features': [
                    'navigation.tabs',
                    'navigation.sections',
                    'navigation.expand',
                    'search.highlight',
                    'search.share'
                ],
                'language': 'es'
            },
            'plugins': [
                'search',
                'tags'
            ],
            'extra': {
                'social': [
                    {'icon': 'fontawesome/brands/github', 'link': 'https://github.com/tu-usuario'}
                ]
            }
        }

        # Generar navegación
        nav = [
            {'🏠 Inicio': 'index.md'},
            {'📚 Proyectos': self.generate_projects_nav()},
            {'📖 Guías MkDocs': [
                {'About MkDocs': 'about-mkdocs.md'}
            ]}
        ]

        mkdocs_config['nav'] = nav

        # Guardar configuración
        config_path = self.output_dir / "docs" / "mkdocs.yml"
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(mkdocs_config, f, allow_unicode=True, default_flow_style=False)

        logger.info(f"Configuración guardada en {config_path}")

    def generate_projects_nav(self) -> List[Dict]:
        """Generar navegación de proyectos"""
        nav_items = [{'Índice de Proyectos': 'proyectos/index.md'}]

        # Ordenar proyectos por prioridad y nombre
        sorted_projects = sorted(
            self.projects,
            key=lambda p: (
                -p.get('aggregator', {}).get('priority', 50),
                p['project']['name']
            )
        )

        # Agrupar por categoría
        categories = {}
        for project in sorted_projects:
            category = project.get('aggregator', {}).get('category', 'General')
            if category not in categories:
                categories[category] = []
            categories[category].append(project)

        # Generar navegación por categoría
        for category, projects in categories.items():
            category_items = []
            for project in projects:
                project_info = project['project']
                slug = project_info['slug']
                name = project_info['name']
                status_emoji = {
                    'production': '✅',
                    'beta': '🔵',
                    'development': '🟡',
                    'deprecated': '⚫'
                }.get(project_info.get('status', 'development'), '⚪')

                # Navegación del proyecto
                project_nav = {
                    f"{status_emoji} {name}": [
                        {'Resumen': f'proyectos/{slug}/index.md'}
                    ]
                }

                # Agregar secciones del proyecto
                for item in project.get('documentation', {}).get('structure', []):
                    if item.get('type') == 'directory':
                        project_nav[f"{status_emoji} {name}"].append({
                            item['title']: f"proyectos/{slug}/{Path(item['source']).name}/index.md"
                        })
                    else:
                        project_nav[f"{status_emoji} {name}"].append({
                            item['title']: f"proyectos/{slug}/{Path(item['source']).name}"
                        })

                category_items.append(project_nav)

            nav_items.append({f"📁 {category}": category_items})

        return nav_items

    def generate_projects_index(self):
        """Generar página índice de todos los proyectos"""
        logger.info("Generando índice de proyectos...")

        index_content = """# 📚 Documentación de Proyectos

Bienvenido al centro de documentación consolidada. Aquí encontrarás la documentación completa de todos los proyectos.

## 🔍 Búsqueda Rápida

Utiliza la barra de búsqueda superior para encontrar información específica en cualquier proyecto.

## 📊 Estadísticas

"""

        # Estadísticas
        total_projects = len(self.projects)
        by_status = {}
        by_category = {}

        for project in self.projects:
            status = project['project'].get('status', 'development')
            category = project.get('aggregator', {}).get('category', 'General')

            by_status[status] = by_status.get(status, 0) + 1
            by_category[category] = by_category.get(category, 0) + 1

        index_content += f"- **Total de Proyectos:** {total_projects}\n"
        index_content += f"- **Por Estado:** "
        index_content += ", ".join([f"{k}: {v}" for k, v in by_status.items()])
        index_content += "\n"
        index_content += f"- **Por Categoría:** "
        index_content += ", ".join([f"{k}: {v}" for k, v in by_category.items()])
        index_content += "\n\n"

        # Proyectos destacados
        featured = [p for p in self.projects if p.get('aggregator', {}).get('featured', False)]
        if featured:
            index_content += "## ⭐ Proyectos Destacados\n\n"
            for project in featured:
                info = project['project']
                index_content += f"### [{info['name']}](./{info['slug']}/index.md)\n"
                index_content += f"{info.get('description', 'Sin descripción')}\n\n"
                index_content += f"- **Estado:** {info.get('status', 'development')}\n"
                index_content += f"- **Versión:** {info.get('version', '0.0.0')}\n"
                index_content += f"- **[Ver Documentación →](./{info['slug']}/index.md)**\n\n"

        # Lista completa por categoría
        index_content += "## 📂 Todos los Proyectos\n\n"

        # Agrupar por categoría
        categories = {}
        for project in self.projects:
            category = project.get('aggregator', {}).get('category', 'General')
            if category not in categories:
                categories[category] = []
            categories[category].append(project)

        for category in sorted(categories.keys()):
            index_content += f"### {category}\n\n"

            for project in sorted(categories[category], key=lambda p: p['project']['name']):
                info = project['project']
                status_badge = {
                    'production': '![Production](https://img.shields.io/badge/Production-green)',
                    'beta': '![Beta](https://img.shields.io/badge/Beta-blue)',
                    'development': '![Development](https://img.shields.io/badge/Development-yellow)',
                    'deprecated': '![Deprecated](https://img.shields.io/badge/Deprecated-red)'
                }.get(info.get('status', 'development'), '')

                index_content += f"#### [{info['name']}](./{info['slug']}/index.md) {status_badge}\n\n"
                index_content += f"{info.get('description', 'Sin descripción')}\n\n"

                # Tecnologías
                techs = info.get('technologies', [])
                if techs:
                    tech_list = []
                    for tech in techs[:5]:  # Limitar a 5 tecnologías
                        if isinstance(tech, dict):
                            tech_list.append(tech.get('name', 'Unknown'))
                        else:
                            tech_list.append(str(tech))
                    index_content += f"**Tecnologías:** {', '.join(tech_list)}\n\n"

                index_content += f"[📖 Ver Documentación](./{info['slug']}/index.md) | "
                index_content += f"[🔗 Repositorio]({info.get('repository', '#')})\n\n"
                index_content += "---\n\n"

        # Guardar archivo
        index_file = self.projects_dir / "index.md"
        index_file.write_text(index_content, encoding='utf-8')
        logger.info(f"Índice guardado en {index_file}")

    def validate_documentation(self):
        """Validar la documentación agregada"""
        logger.info("Validando documentación agregada...")

        issues = []

        for project in self.projects:
            project_slug = project['project']['slug']
            project_dir = self.projects_dir / project_slug

            # Verificar que existe el directorio del proyecto
            if not project_dir.exists():
                issues.append(f"Directorio no encontrado para {project_slug}")
                continue

            # Verificar archivos requeridos
            required_files = ['index.md']
            for req_file in required_files:
                if not (project_dir / req_file).exists():
                    issues.append(f"Archivo requerido {req_file} no encontrado en {project_slug}")

        if issues:
            logger.warning("Problemas encontrados durante la validación:")
            for issue in issues:
                logger.warning(f"  - {issue}")
        else:
            logger.info("✅ Validación completada sin problemas")

        return len(issues) == 0

    def build_mkdocs_site(self):
        """Construir el sitio MkDocs"""
        logger.info("Construyendo sitio MkDocs...")

        result = subprocess.run(
            ["mkdocs", "build", "--strict"],
            capture_output=True,
            text=True,
            cwd=self.output_dir / "docs"
        )

        if result.returncode == 0:
            logger.info("✅ Sitio construido exitosamente")
            return True
        else:
            logger.error(f"Error al construir sitio: {result.stderr}")
            return False

    def run(self, mode='branches', local_projects=None):
        """Ejecutar el proceso completo de agregación"""
        logger.info("=" * 60)
        logger.info("Iniciando agregación de documentación")
        logger.info("=" * 60)

        # Configurar directorios
        self.setup_directories()

        # Agregar documentación según el modo
        if mode == 'local' and local_projects:
            self.aggregate_from_local_projects(local_projects)
        else:
            self.aggregate_from_branches()

        # Generar índice de proyectos
        if self.projects:
            self.generate_projects_index()

            # Generar configuración MkDocs
            self.generate_mkdocs_config()

            # Validar documentación
            if self.validate_documentation():
                # Construir sitio
                self.build_mkdocs_site()
        else:
            logger.warning("No se encontraron proyectos para agregar")

        logger.info("=" * 60)
        logger.info(f"Agregación completada. Total de proyectos: {len(self.projects)}")
        logger.info("=" * 60)


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Agregador de Documentación Multi-Proyecto'
    )

    parser.add_argument(
        '--mode',
        choices=['branches', 'local'],
        default='branches',
        help='Modo de agregación: branches (desde ramas Git) o local (directorios locales)'
    )

    parser.add_argument(
        '--base-dir',
        type=Path,
        default=Path.cwd(),
        help='Directorio base del repositorio'
    )

    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path.cwd(),
        help='Directorio de salida para la documentación'
    )

    parser.add_argument(
        '--local-projects',
        nargs='+',
        type=Path,
        help='Rutas a proyectos locales (solo en modo local)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Mostrar salida detallada'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Crear agregador
    aggregator = DocumentationAggregator(args.base_dir, args.output_dir)

    # Ejecutar agregación
    aggregator.run(mode=args.mode, local_projects=args.local_projects)


if __name__ == '__main__':
    main()