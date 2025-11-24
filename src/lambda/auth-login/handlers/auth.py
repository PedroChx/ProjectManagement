import json
import uuid
from utils.response import success_response, error_response
from utils.auth_utils import hash_password, verify_password, generate_token, require_auth
from utils.db_utils import create_user, get_user_by_email, get_user_statistics


def register(event, context):
    """
    POST /auth/register
    Registrar nuevo usuario
    """
    try:
        body = json.loads(event.get('body', '{}'))
        
        # Validar campos requeridos
        required_fields = ['email', 'password', 'name']
        for field in required_fields:
            if field not in body or not body[field]:
                return error_response(400, f'Campo requerido: {field}', 'MISSING_FIELD')
        
        # Validar formato de email
        email = body['email'].lower().strip()
        if '@' not in email:
            return error_response(400, 'Email inválido', 'INVALID_EMAIL')
        
        # Validar longitud de password
        if len(body['password']) < 6:
            return error_response(400, 'La contraseña debe tener al menos 6 caracteres', 'WEAK_PASSWORD')
        
        # Verificar si el email ya existe
        existing_user = get_user_by_email(email)
        if existing_user:
            return error_response(400, 'El email ya está registrado', 'EMAIL_EXISTS')
        
        # Crear usuario
        user_id = str(uuid.uuid4())
        hashed_password = hash_password(body['password'])
        
        user = create_user(
            user_id=user_id,
            email=email,
            name=body['name'].strip(),
            hashed_password=hashed_password
        )
        
        # Generar token
        token = generate_token({
            'userId': user_id,
            'email': email,
            'name': body['name'].strip()
        })
        
        return success_response(201, {
            'token': token,
            'user': {
                'userId': user_id,
                'email': email,
                'name': body['name'].strip()
            }
        }, 'Usuario registrado exitosamente')
        
    except Exception as e:
        print(f"Error en register: {str(e)}")
        return error_response(500, 'Error interno del servidor', 'INTERNAL_ERROR')


def login(event, context):
    """
    POST /auth/login
    Iniciar sesión
    """
    try:
        body = json.loads(event.get('body', '{}'))
        
        # Validar campos
        if 'email' not in body or 'password' not in body:
            return error_response(400, 'Email y contraseña son requeridos', 'MISSING_CREDENTIALS')
        
        email = body['email'].lower().strip()
        
        # Buscar usuario
        user = get_user_by_email(email)
        if not user:
            return error_response(401, 'Credenciales inválidas', 'INVALID_CREDENTIALS')
        
        # Verificar password
        if not verify_password(body['password'], user['password']):
            return error_response(401, 'Credenciales inválidas', 'INVALID_CREDENTIALS')
        
        # Generar token
        token = generate_token({
            'userId': user['userId'],
            'email': user['email'],
            'name': user['name']
        })
        
        return success_response(200, {
            'token': token,
            'user': {
                'userId': user['userId'],
                'email': user['email'],
                'name': user['name']
            }
        }, 'Login exitoso')
        
    except Exception as e:
        print(f"Error en login: {str(e)}")
        return error_response(500, 'Error interno del servidor', 'INTERNAL_ERROR')


@require_auth
def get_profile(event, context, user):
    """
    GET /auth/me
    Obtener perfil del usuario autenticado
    """
    try:
        # Obtener estadísticas del usuario
        stats = get_user_statistics(user['userId'])
        
        return success_response(200, {
            'user': {
                'userId': user['userId'],
                'email': user['email'],
                'name': user['name']
            },
            'statistics': stats
        })
        
    except Exception as e:
        print(f"Error en get_profile: {str(e)}")
        return error_response(500, 'Error interno del servidor', 'INTERNAL_ERROR')