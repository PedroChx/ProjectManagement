# projects-get

## Descripción
Obtener detalles de un proyecto

## Endpoint
- **Método:** `GET`
- **Path:** `/projects/{id}`

## Handler
- **Función:** `app.lambda_handler`
- **Runtime:** Python 3.11

## Variables de Entorno
- `TABLE_NAME`: Nombre de la tabla DynamoDB
- `JWT_SECRET`: Secreto para tokens JWT
- `ENVIRONMENT`: Ambiente de ejecución (dev/staging/prod)

## Despliegue Local
```bash
sam local invoke projectsget -e events/test-event.json
```

## Testing
```bash
pytest tests/test_projects_get.py
```
