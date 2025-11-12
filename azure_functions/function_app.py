import azure.functions as func
import datetime
import json
import logging

app = func.FunctionApp()

@app.queue_trigger(arg_name="msg", queue_name="user-notifications",
                   connection="AzureWebJobsStorage") 
def process_user_notifications(msg: func.QueueMessage) -> None:
    """
    Queue-triggered function that processes user notification messages.
    Triggered when a message is added to the 'user-notifications' queue.
    """
    logging.info('=== Python queue trigger function STARTED ===')
    
    try:
        # Parse the message JSON
        logging.info('Reading message body...')
        message_body = msg.get_body().decode('utf-8')
        logging.info(f'Raw message: {message_body}')
        
        logging.info('Parsing JSON...')
        message_data = json.loads(message_body)
        logging.info(f'Parsed data: {message_data}')
        
        # Extract user information
        notification_type = message_data.get('type')
        user_id = message_data.get('user_id')
        username = message_data.get('username')
        email = message_data.get('email')
        
        logging.info(f'Processing notification: {notification_type}')
        logging.info(f'User ID: {user_id}, Username: {username}, Email: {email}')
        
        # Simulate sending welcome email
        if notification_type == 'user_created':
            send_welcome_email(username, email)
        
        logging.info('Message processed successfully!')
        
    except Exception as e:
        logging.error(f'Error processing message: {str(e)}')
        raise


def send_welcome_email(username: str, email: str):
    """
    Simulate sending a welcome email to a new user.
    In production, this would integrate with SendGrid, AWS SES, or similar service.
    """
    logging.info(f'📧 SENDING WELCOME EMAIL')
    logging.info(f'   To: {email}')
    logging.info(f'   Subject: Welcome to our platform, {username}!')
    logging.info(f'   Body: Hi {username}, thanks for joining us!')
    logging.info(f'✅ Email sent successfully!')