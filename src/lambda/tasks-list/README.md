# tasks-list

## Descripción
Listar tareas de un proyecto

## Endpoint
- **Método:** `GET`
- **Path:** `/projects/{id}/tasks`

## Handler
- **Función:** `app.lambda_handler`
- **Runtime:** Python 3.11

## Variables de Entorno
- `TABLE_NAME`: Nombre de la tabla DynamoDB
- `JWT_SECRET`: Secreto para tokens JWT
- `ENVIRONMENT`: Ambiente de ejecución (dev/staging/prod)

## Despliegue Local
```bash
sam local invoke taskslist -e events/test-event.json
```

## Testing
```bash
pytest tests/test_tasks_list.py
```
