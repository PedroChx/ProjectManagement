# auth-register

## Descripción
Registrar nuevo usuario

## Endpoint
- **Método:** `POST`
- **Path:** `/auth/register`

## Handler
- **Función:** `app.lambda_handler`
- **Runtime:** Python 3.11

## Variables de Entorno
- `TABLE_NAME`: Nombre de la tabla DynamoDB
- `JWT_SECRET`: Secreto para tokens JWT
- `ENVIRONMENT`: Ambiente de ejecución (dev/staging/prod)

## Despliegue Local
```bash
sam local invoke authregister -e events/test-event.json
```

## Testing
```bash
pytest tests/test_auth_register.py
```
