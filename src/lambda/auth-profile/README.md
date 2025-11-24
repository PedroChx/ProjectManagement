# auth-profile

## Descripción
Obtener perfil del usuario autenticado

## Endpoint
- **Método:** `GET`
- **Path:** `/auth/me`

## Handler
- **Función:** `app.lambda_handler`
- **Runtime:** Python 3.11

## Variables de Entorno
- `TABLE_NAME`: Nombre de la tabla DynamoDB
- `JWT_SECRET`: Secreto para tokens JWT
- `ENVIRONMENT`: Ambiente de ejecución (dev/staging/prod)

## Despliegue Local
```bash
sam local invoke authprofile -e events/test-event.json
```

## Testing
```bash
pytest tests/test_auth_profile.py
```
