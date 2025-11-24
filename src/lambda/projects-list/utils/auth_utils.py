import jwt
import hashlib
import os
from datetime import datetime, timedelta
from functools import wraps
from .response import error_response

JWT_SECRET = os.environ.get('JWT_SECRET', 'dev-secret-change-in-production')
JWT_ALGORITHM = 'HS256'
TOKEN_EXPIRATION_DAYS = 7


def hash_password(password):
    """Hash password usando SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, hashed_password):
    """Verificar password contra hash"""
    return hash_password(password) == hashed_password


def generate_token(user_data):
    """
    Generar JWT token
    
    Args:
        user_data: dict con userId, email, name
    
    Returns:
        JWT token string
    """
    payload = {
        'userId': user_data['userId'],
        'email': user_data['email'],
        'name': user_data['name'],
        'exp': datetime.utcnow() + timedelta(days=TOKEN_EXPIRATION_DAYS),
        'iat': datetime.utcnow()
    }
    
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token):
    """
    Decodificar JWT token
    
    Returns:
        dict con datos del usuario o None si es inválido
    """
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def extract_token_from_header(event):
    """
    Extraer token del header Authorization
    
    Returns:
        token string o None
    """
    auth_header = event.get('headers', {}).get('Authorization', '')
    
    # Manejar case-insensitive headers
    if not auth_header:
        headers = event.get('headers', {})
        for key, value in headers.items():
            if key.lower() == 'authorization':
                auth_header = value
                break
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    return auth_header.split(' ')[1]


def get_user_from_token(event):
    """
    Obtener usuario del token en el evento
    
    Returns:
        dict con datos del usuario o None
    """
    token = extract_token_from_header(event)
    if not token:
        return None
    
    return decode_token(token)


def require_auth(handler):
    """
    Decorador para requerir autenticación en handlers
    
    Usage:
        @require_auth
        def my_handler(event, context, user):
            # user contiene los datos del usuario autenticado
            pass
    """
    @wraps(handler)
    def wrapper(event, context):
        user = get_user_from_token(event)
        
        if not user:
            return error_response(401, 'Token inválido o expirado', 'UNAUTHORIZED')
        
        return handler(event, context, user)
    
    return wrapper