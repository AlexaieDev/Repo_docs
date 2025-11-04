# 📡 API Reference - Proyecto 1

## Endpoints Disponibles

### Autenticación

#### POST /api/auth/login
Autentica un usuario y devuelve un token JWT.

**Request:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "contraseña123"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "123",
    "email": "usuario@ejemplo.com",
    "name": "Usuario Ejemplo"
  }
}
```

### Usuarios

#### GET /api/users
Obtiene lista de usuarios (requiere autenticación admin).

#### GET /api/users/{id}
Obtiene información de un usuario específico.

#### POST /api/users
Crea un nuevo usuario.

#### PUT /api/users/{id}
Actualiza información de usuario.

## Códigos de Estado

- `200` - Operación exitosa
- `201` - Recurso creado
- `400` - Petición inválida
- `401` - No autorizado
- `403` - Prohibido
- `404` - No encontrado
- `500` - Error del servidor