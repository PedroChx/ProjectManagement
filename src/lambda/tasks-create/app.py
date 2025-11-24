"""
Crear nueva tarea
Endpoint: POST /projects/{id}/tasks
Handler: app.lambda_handler
"""

from handlers.tasks import create_task_handler
from utils.response import error_response


def lambda_handler(event, context):
    """
    Handler principal para Crear nueva tarea
    
    Args:
        event: Evento de API Gateway
        context: Contexto de Lambda
    
    Returns:
        Response dict con statusCode, headers y body
    """
    try:
        # Manejar OPTIONS para CORS
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': ''
            }
        
        # Llamar al handler específico
        return create_task_handler(event, context)
        
    except Exception as e:
        print(f"Error en lambda_handler: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(500, 'Error interno del servidor', 'INTERNAL_ERROR')
