# 🚀 Getting Started - Proyecto 1

## Requisitos Previos

- Python 3.8+
- PostgreSQL 12+
- Docker y Docker Compose
- Redis 6+

## Instalación Rápida

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/proyecto-1.git
cd proyecto-1
```

### 2. Configurar Variables de Entorno

```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### 3. Iniciar con Docker Compose

```bash
docker-compose up -d
```

### 4. Ejecutar Migraciones

```bash
docker-compose exec api python manage.py migrate
```

### 5. Crear Usuario Administrador

```bash
docker-compose exec api python manage.py createsuperuser
```

## Verificar Instalación

Accede a:
- API: http://localhost:8000
- Admin UI: http://localhost:3000
- Documentación API: http://localhost:8000/docs

## Próximos Pasos

- Consulta la [API Reference](../api/index.md) para detalles de endpoints
- Revisa las [Guías](../guides/index.md) para configuración avanzada
- Explora los [Ejemplos](../examples/index.md) para casos de uso comunes