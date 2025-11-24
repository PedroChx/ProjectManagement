# projects-list

## Descripción
Listar todos los proyectos del usuario

## Endpoint
- **Método:** `GET`
- **Path:** `/projects`

## Handler
- **Función:** `app.lambda_handler`
- **Runtime:** Python 3.11

## Variables de Entorno
- `TABLE_NAME`: Nombre de la tabla DynamoDB
- `JWT_SECRET`: Secreto para tokens JWT
- `ENVIRONMENT`: Ambiente de ejecución (dev/staging/prod)

## Despliegue Local
```bash
sam local invoke projectslist -e events/test-event.json
```

## Testing
```bash
pytest tests/test_projects_list.py
```
