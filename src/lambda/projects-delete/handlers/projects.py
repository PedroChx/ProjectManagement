import json
import uuid
from utils.response import success_response, error_response
from utils.auth_utils import require_auth
from utils.db_utils import (
    create_project, get_user_projects, get_project,
    update_project, delete_project, check_user_project_access,
    get_project_members
)


@require_auth
def list_projects(event, context, user):
    """
    GET /projects
    Listar todos los proyectos del usuario
    """
    try:
        projects = get_user_projects(user['userId'])
        
        # Ordenar por fecha de creación (más recientes primero)
        projects.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
        
        return success_response(200, {
            'projects': projects,
            'count': len(projects)
        })
        
    except Exception as e:
        print(f"Error en list_projects: {str(e)}")
        return error_response(500, 'Error interno del servidor', 'INTERNAL_ERROR')


@require_auth
def create_project_handler(event, context, user):
    """
    POST /projects
    Crear nuevo proyecto
    """
    try:
        body = json.loads(event.get('body', '{}'))
        
        # Validar campo requerido
        if 'name' not in body or not body['name'].strip():
            return error_response(400, 'El nombre del proyecto es requerido', 'MISSING_NAME')
        
        # Validar longitud del nombre
        if len(body['name'].strip()) < 3:
            return error_response(400, 'El nombre debe tener al menos 3 caracteres', 'NAME_TOO_SHORT')
        
        # Crear proyecto
        project_id = str(uuid.uuid4())
        
        project = create_project(
            project_id=project_id,
            name=body['name'].strip(),
            description=body.get('description', '').strip(),
            status=body.get('status', 'active'),
            user_id=user['userId'],
            user_name=user['name']
        )
        
        return success_response(201, {
            'project': project
        }, 'Proyecto creado exitosamente')
        
    except Exception as e:
        print(f"Error en create_project: {str(e)}")
        return error_response(500, 'Error interno del servidor', 'INTERNAL_ERROR')


@require_auth
def get_project_details(event, context, user):
    """
    GET /projects/{id}
    Obtener detalles de un proyecto
    """
    try:
        project_id = event['pathParameters']['id']
        
        # Verificar acceso
        access = check_user_project_access(user['userId'], project_id)
        if not access:
            return error_response(403, 'No tienes acceso a este proyecto', 'FORBIDDEN')
        
        # Obtener proyecto
        project = get_project(project_id)
        if not project:
            return error_response(404, 'Proyecto no encontrado', 'NOT_FOUND')
        
        # Obtener miembros
        members = get_project_members(project_id)
        
        # Agregar información adicional
        project['members'] = members
        project['userRole'] = access.get('role', 'member')
        
        return success_response(200, {
            'project': project
        })
        
    except KeyError:
        return error_response(400, 'ID de proyecto requerido', 'MISSING_ID')
    except Exception as e:
        print(f"Error en get_project_details: {str(e)}")
        return error_response(500, 'Error interno del servidor', 'INTERNAL_ERROR')


@require_auth
def update_project_handler(event, context, user):
    """
    PUT /projects/{id}
    Actualizar proyecto (solo owner)
    """
    try:
        project_id = event['pathParameters']['id']
        body = json.loads(event.get('body', '{}'))
        
        # Verificar acceso y rol
        access = check_user_project_access(user['userId'], project_id)
        if not access or access.get('role') != 'owner':
            return error_response(403, 'Solo el owner puede actualizar el proyecto', 'FORBIDDEN')
        
        # Validar que hay campos para actualizar
        allowed_fields = ['name', 'description', 'status']
        updates = {k: v for k, v in body.items() if k in allowed_fields}
        
        if not updates:
            return error_response(400, 'No hay campos para actualizar', 'NO_UPDATES')
        
        # Validar nombre si se está actualizando
        if 'name' in updates and len(updates['name'].strip()) < 3:
            return error_response(400, 'El nombre debe tener al menos 3 caracteres', 'NAME_TOO_SHORT')
        
        # Actualizar proyecto
        updated_project = update_project(project_id, updates)
        
        return success_response(200, {
            'project': updated_project
        }, 'Proyecto actualizado exitosamente')
        
    except KeyError:
        return error_response(400, 'ID de proyecto requerido', 'MISSING_ID')
    except Exception as e:
        print(f"Error en update_project: {str(e)}")
        return error_response(500, 'Error interno del servidor', 'INTERNAL_ERROR')


@require_auth
def delete_project_handler(event, context, user):
    """
    DELETE /projects/{id}
    Eliminar proyecto (solo owner)
    """
    try:
        project_id = event['pathParameters']['id']
        
        # Verificar acceso y rol
        access = check_user_project_access(user['userId'], project_id)
        if not access or access.get('role') != 'owner':
            return error_response(403, 'Solo el owner puede eliminar el proyecto', 'FORBIDDEN')
        
        # Eliminar proyecto
        delete_project(project_id)
        
        return success_response(200, {
            'projectId': project_id
        }, 'Proyecto eliminado exitosamente')
        
    except KeyError:
        return error_response(400, 'ID de proyecto requerido', 'MISSING_ID')
    except Exception as e:
        print(f"Error en delete_project: {str(e)}")
        return error_response(500, 'Error interno del servidor', 'INTERNAL_ERROR')