import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime

# Inicializar cliente DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'ProjectManagement-dev')
table = dynamodb.Table(table_name)


def get_timestamp():
    """Obtener timestamp ISO actual"""
    return datetime.utcnow().isoformat()


# ==================== USER OPERATIONS ====================

def create_user(user_id, email, name, hashed_password):
    """Crear nuevo usuario en DynamoDB"""
    user_item = {
        'PK': f"USER#{user_id}",
        'SK': 'PROFILE',
        'userId': user_id,
        'email': email,
        'name': name,
        'password': hashed_password,
        'createdAt': get_timestamp()
    }
    
    table.put_item(Item=user_item)
    return user_item


def get_user_by_email(email):
    """Buscar usuario por email"""
    response = table.query(
        IndexName='EmailIndex',
        KeyConditionExpression=Key('email').eq(email)
    )
    
    if response['Count'] > 0:
        return response['Items'][0]
    return None


def get_user_by_id(user_id):
    """Obtener usuario por ID"""
    response = table.get_item(
        Key={
            'PK': f"USER#{user_id}",
            'SK': 'PROFILE'
        }
    )
    
    return response.get('Item')


# ==================== PROJECT OPERATIONS ====================

def create_project(project_id, name, description, status, user_id, user_name):
    """Crear nuevo proyecto"""
    timestamp = get_timestamp()
    
    # Metadata del proyecto
    project_item = {
        'PK': f"PROJECT#{project_id}",
        'SK': 'METADATA',
        'projectId': project_id,
        'name': name,
        'description': description,
        'status': status,
        'createdBy': user_id,
        'createdByName': user_name,
        'createdAt': timestamp,
        'updatedAt': timestamp,
        'taskCount': 0,
        'memberCount': 1
    }
    
    # Miembro owner
    member_item = {
        'PK': f"PROJECT#{project_id}",
        'SK': f"MEMBER#{user_id}",
        'userId': user_id,
        'userName': user_name,
        'role': 'owner',
        'joinedAt': timestamp
    }
    
    # Relación usuario-proyecto
    user_project_item = {
        'PK': f"USER#{user_id}",
        'SK': f"PROJECT#{project_id}",
        'projectId': project_id,
        'projectName': name,
        'role': 'owner',
        'joinedAt': timestamp
    }
    
    # Escribir en batch
    with table.batch_writer() as batch:
        batch.put_item(Item=project_item)
        batch.put_item(Item=member_item)
        batch.put_item(Item=user_project_item)
    
    return project_item


def get_user_projects(user_id):
    """Obtener todos los proyectos de un usuario"""
    response = table.query(
        KeyConditionExpression=Key('PK').eq(f"USER#{user_id}") & Key('SK').begins_with('PROJECT#')
    )
    
    projects = []
    for item in response['Items']:
        project_id = item['SK'].replace('PROJECT#', '')
        
        # Obtener metadata del proyecto
        project_data = table.get_item(
            Key={
                'PK': f"PROJECT#{project_id}",
                'SK': 'METADATA'
            }
        )
        
        if 'Item' in project_data:
            project = project_data['Item']
            project['userRole'] = item.get('role', 'member')
            projects.append(project)
    
    return projects


def get_project(project_id):
    """Obtener detalles de un proyecto"""
    response = table.get_item(
        Key={
            'PK': f"PROJECT#{project_id}",
            'SK': 'METADATA'
        }
    )
    
    return response.get('Item')


def update_project(project_id, updates):
    """Actualizar proyecto"""
    update_expr = "SET updatedAt = :timestamp"
    expr_values = {':timestamp': get_timestamp()}
    expr_names = {}
    
    for key, value in updates.items():
        if key in ['name', 'description', 'status']:
            update_expr += f", #{key} = :{key}"
            expr_values[f":{key}"] = value
            expr_names[f"#{key}"] = key
    
    response = table.update_item(
        Key={
            'PK': f"PROJECT#{project_id}",
            'SK': 'METADATA'
        },
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_values,
        ExpressionAttributeNames=expr_names if expr_names else None,
        ReturnValues='ALL_NEW'
    )
    
    return response.get('Attributes')


def delete_project(project_id):
    """Eliminar proyecto (solo metadata, las relaciones se eliminan por separado)"""
    table.delete_item(
        Key={
            'PK': f"PROJECT#{project_id}",
            'SK': 'METADATA'
        }
    )


def check_user_project_access(user_id, project_id):
    """Verificar si el usuario tiene acceso al proyecto"""
    response = table.get_item(
        Key={
            'PK': f"USER#{user_id}",
            'SK': f"PROJECT#{project_id}"
        }
    )
    
    return response.get('Item')


def get_project_members(project_id):
    """Obtener miembros de un proyecto"""
    response = table.query(
        KeyConditionExpression=Key('PK').eq(f"PROJECT#{project_id}") & Key('SK').begins_with('MEMBER#')
    )
    
    return response.get('Items', [])


# ==================== TASK OPERATIONS ====================

def create_task(task_id, project_id, title, description, status, assigned_to, created_by):
    """Crear nueva tarea"""
    timestamp = get_timestamp()
    
    task_item = {
        'PK': f"PROJECT#{project_id}",
        'SK': f"TASK#{task_id}",
        'taskId': task_id,
        'projectId': project_id,
        'title': title,
        'description': description,
        'status': status,
        'assignedTo': assigned_to,
        'createdBy': created_by,
        'createdAt': timestamp,
        'updatedAt': timestamp
    }
    
    table.put_item(Item=task_item)
    
    # Incrementar contador de tareas del proyecto
    table.update_item(
        Key={
            'PK': f"PROJECT#{project_id}",
            'SK': 'METADATA'
        },
        UpdateExpression='SET taskCount = if_not_exists(taskCount, :zero) + :inc',
        ExpressionAttributeValues={
            ':inc': 1,
            ':zero': 0
        }
    )
    
    return task_item


def get_project_tasks(project_id):
    """Obtener todas las tareas de un proyecto"""
    response = table.query(
        KeyConditionExpression=Key('PK').eq(f"PROJECT#{project_id}") & Key('SK').begins_with('TASK#')
    )
    
    return response.get('Items', [])


def update_task(project_id, task_id, updates):
    """Actualizar tarea"""
    update_expr = "SET updatedAt = :timestamp"
    expr_values = {':timestamp': get_timestamp()}
    expr_names = {}
    
    for key, value in updates.items():
        if key in ['title', 'description', 'status', 'assignedTo']:
            update_expr += f", #{key} = :{key}"
            expr_values[f":{key}"] = value
            expr_names[f"#{key}"] = key
    
    response = table.update_item(
        Key={
            'PK': f"PROJECT#{project_id}",
            'SK': f"TASK#{task_id}"
        },
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_values,
        ExpressionAttributeNames=expr_names if expr_names else None,
        ReturnValues='ALL_NEW'
    )
    
    return response.get('Attributes')


def delete_task(project_id, task_id):
    """Eliminar tarea"""
    table.delete_item(
        Key={
            'PK': f"PROJECT#{project_id}",
            'SK': f"TASK#{task_id}"
        }
    )
    
    # Decrementar contador
    table.update_item(
        Key={
            'PK': f"PROJECT#{project_id}",
            'SK': 'METADATA'
        },
        UpdateExpression='SET taskCount = taskCount - :dec',
        ExpressionAttributeValues={':dec': 1}
    )


# ==================== STATISTICS ====================

def get_user_statistics(user_id):
    """Obtener estadísticas del usuario"""
    # Proyectos del usuario
    projects = get_user_projects(user_id)
    
    total_projects = len(projects)
    active_projects = len([p for p in projects if p.get('status') == 'active'])
    completed_projects = len([p for p in projects if p.get('status') == 'completed'])
    
    # Contar tareas totales
    total_tasks = 0
    for project in projects:
        total_tasks += project.get('taskCount', 0)
    
    return {
        'totalProjects': total_projects,
        'activeProjects': active_projects,
        'completedProjects': completed_projects,
        'totalTasks': total_tasks,
        'ownedProjects': len([p for p in projects if p.get('userRole') == 'owner'])
    }