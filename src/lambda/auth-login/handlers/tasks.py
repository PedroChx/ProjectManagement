import json
import uuid
from utils.response import success_response, error_response
from utils.auth_utils import require_auth
from utils.db_utils import (
    check_user_project_access, get_project_tasks,
    create_task, update_task, delete_task
)


@require_auth
def list_tasks(event, context, user):
    """
    GET /projects/{id}/tasks
    Listar todas las tareas de un proyecto
    """
    try:
        project_id = event['pathParameters']['id']
        
        # Verificar acceso al proyecto
        access = check_user_project_access(user['userId'], project_id)
        if not access:
            return error_response(403, 'No tienes acceso a este proyecto', 'FORBIDDEN')
        
        # Obtener tareas
        tasks = get_project_tasks(project_id)
        
        # Ordenar por fecha de creación
        tasks.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
        
        return success_response(200, {
            'tasks': tasks,
            'count': len(tasks)
        })
        
    except KeyError:
        return error_response(400, 'ID de proyecto requerido', 'MISSING_ID')
    except Exception as e:
        print(f"Error en list_tasks: {str(e)}")
        return error_response(500, 'Error interno del servidor', 'INTERNAL_ERROR')


@require_auth
def create_task_handler(event, context, user):
    """
    POST /projects/{id}/tasks
    Crear nueva tarea
    """
    try:
        project_id = event['pathParameters']['id']
        body = json.loads(event.get('body', '{}'))
        
        # Verificar acceso al proyecto
        access = check_user_project_access(user['userId'], project_id)
        if not access:
            return error_response(403, 'No tienes acceso a este proyecto', 'FORBIDDEN')
        
        # Validar campo requerido
        if 'title' not in body or not body['title'].strip():
            return error_response(400, 'El título de la tarea es requerido', 'MISSING_TITLE')
        
        # Validar longitud del título
        if len(body['title'].strip()) < 3:
            return error_response(400, 'El título debe tener al menos 3 caracteres', 'TITLE_TOO_SHORT')
        
        # Crear tarea
        task_id = str(uuid.uuid4())
        
        task = create_task(
            task_id=task_id,
            project_id=project_id,
            title=body['title'].strip(),
            description=body.get('description', '').strip(),
            status=body.get('status', 'pending'),
            assigned_to=body.get('assignedTo', user['userId']),
            created_by=user['userId']
        )
        
        return success_response(201, {
            'task': task
        }, 'Tarea creada exitosamente')
        
    except KeyError:
        return error_response(400, 'ID de proyecto requerido', 'MISSING_ID')
    except Exception as e:
        print(f"Error en create_task: {str(e)}")
        return error_response(500, 'Error interno del servidor', 'INTERNAL_ERROR')


@require_auth
def update_task_handler(event, context, user):
    """
    PUT /projects/{projectId}/tasks/{taskId}
    Actualizar tarea
    """
    try:
        project_id = event['pathParameters']['projectId']
        task_id = event['pathParameters']['taskId']
        body = json.loads(event.get('body', '{}'))
        
        # Verificar acceso al proyecto
        access = check_user_project_access(user['userId'], project_id)
        if not access:
            return error_response(403, 'No tienes acceso a este proyecto', 'FORBIDDEN')
        
        # Validar que hay campos para actualizar
        allowed_fields = ['title', 'description', 'status', 'assignedTo']
        updates = {k: v for k, v in body.items() if k in allowed_fields}
        
        if not updates:
            return error_response(400, 'No hay campos para actualizar', 'NO_UPDATES')
        
        # Validar título si se está actualizando
        if 'title' in updates and len(updates['title'].strip()) < 3:
            return error_response(400, 'El título debe tener al menos 3 caracteres', 'TITLE_TOO_SHORT')
        
        # Actualizar tarea
        updated_task = update_task(project_id, task_id, updates)
        
        return success_response(200, {
            'task': updated_task
        }, 'Tarea actualizada exitosamente')
        
    except KeyError as e:
        return error_response(400, f'Parámetro requerido faltante: {str(e)}', 'MISSING_PARAMETER')
    except Exception as e:
        print(f"Error en update_task: {str(e)}")
        return error_response(500, 'Error interno del servidor', 'INTERNAL_ERROR')


@require_auth
def delete_task_handler(event, context, user):
    """
    DELETE /projects/{projectId}/tasks/{taskId}
    Eliminar tarea
    """
    try:
        project_id = event['pathParameters']['projectId']
        task_id = event['pathParameters']['taskId']
        
        # Verificar acceso al proyecto
        access = check_user_project_access(user['userId'], project_id)
        if not access:
            return error_response(403, 'No tienes acceso a este proyecto', 'FORBIDDEN')
        
        # Eliminar tarea
        delete_task(project_id, task_id)
        
        return success_response(200, {
            'taskId': task_id
        }, 'Tarea eliminada exitosamente')
        
    except KeyError as e:
        return error_response(400, f'Parámetro requerido faltante: {str(e)}', 'MISSING_PARAMETER')
    except Exception as e:
        print(f"Error en delete_task: {str(e)}")
        return error_response(500, 'Error interno del servidor', 'INTERNAL_ERROR')