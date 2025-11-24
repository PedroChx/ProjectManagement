# tasks-delete

## Descripción
Eliminar tarea

## Endpoint
- **Método:** `DELETE`
- **Path:** `/projects/{id}/tasks/{taskId}`

## Handler
- **Función:** `app.lambda_handler`
- **Runtime:** Python 3.11

## Variables de Entorno
- `TABLE_NAME`: Nombre de la tabla DynamoDB
- `JWT_SECRET`: Secreto para tokens JWT
- `ENVIRONMENT`: Ambiente de ejecución (dev/staging/prod)

## Despliegue Local
```bash
sam local invoke tasksdelete -e events/test-event.json
```

## Testing
```bash
pytest tests/test_tasks_delete.py
```
