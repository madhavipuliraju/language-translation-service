import logging
from language_helper import handle_message_translation
from profiler import profile

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@profile
def lambda_handler(event, context):
    translated_message = translate(event)
    logger.info(f"Message translated is:{translated_message}")
    return {
        'statusCode': 200,
        'translated_message': translated_message
    }

def translate(event):
    logger.info(f"Event passing for Translation is:{event}")
    source = event['source']
    user_id = event['user_id']
    message = event['message']

    return handle_message_translation(message, user_id, source)
