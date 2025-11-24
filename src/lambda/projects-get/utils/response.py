import json
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    """Encoder personalizado para serializar Decimals de DynamoDB"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def success_response(status_code, data, message=None):
    """
    Respuesta exitosa estándar
    
    Args:
        status_code: HTTP status code
        data: Datos a retornar
        message: Mensaje opcional
    """
    body = {'success': True}
    
    if message:
        body['message'] = message
    
    if data is not None:
        body['data'] = data
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Access-Control-Allow-Credentials': 'true'
        },
        'body': json.dumps(body, cls=DecimalEncoder)
    }


def error_response(status_code, error_message, error_code=None):
    """
    Respuesta de error estándar
    
    Args:
        status_code: HTTP status code
        error_message: Mensaje de error
        error_code: Código de error opcional
    """
    body = {
        'success': False,
        'error': error_message
    }
    
    if error_code:
        body['errorCode'] = error_code
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Access-Control-Allow-Credentials': 'true'
        },
        'body': json.dumps(body)
    }