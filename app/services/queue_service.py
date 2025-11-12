"""
Azure Queue Storage Service
Handles sending messages to Azure Storage Queues for async processing
"""
import json
import logging
from azure.storage.queue import QueueClient
from azure.identity import DefaultAzureCredential
import os

logger = logging.getLogger(__name__)


class QueueService:
    """Service for managing Azure Queue Storage operations"""
    
    def __init__(self):
        self.queue_client = None
        self.queue_name = "user-notifications"
    
    def _initialize(self):
        """Initialize Queue client connection"""
        if self.queue_client:
            return
        
        storage_account_name = os.environ.get('STORAGE_ACCOUNT_NAME')
        
        if not storage_account_name:
            logger.warning("Storage account not configured. Queue messaging disabled.")
            return
        
        try:
            # Azure Queue URL format
            queue_url = f"https://{storage_account_name}.queue.core.windows.net/{self.queue_name}"
            
            # Use Managed Identity for authentication
            credential = DefaultAzureCredential()
            self.queue_client = QueueClient(
                account_url=f"https://{storage_account_name}.queue.core.windows.net",
                queue_name=self.queue_name,
                credential=credential
            )
            
            # Ensure queue exists (create if not)
            self.queue_client.create_queue()
            logger.info(f"Queue client connected to '{self.queue_name}'")
        except Exception as e:
            # Queue might already exist, that's fine
            if "already exists" in str(e).lower():
                logger.info(f"Queue '{self.queue_name}' already exists")
            else:
                logger.error(f"Queue connection failed: {e}. Queue messaging disabled.")
                self.queue_client = None
    
    def send_message(self, message_data):
        """
        Send a message to the queue
        
        Args:
            message_data: Dictionary with message data (will be JSON serialized)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self._initialize()
            
            if not self.queue_client:
                logger.warning("Queue client not available. Message not sent.")
                return False
            
            # Serialize message to JSON
            message_json = json.dumps(message_data)
            
            # Send to queue
            self.queue_client.send_message(message_json)
            logger.info(f"Message sent to queue: {message_data.get('type', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message to queue: {e}")
            return False
    
    def send_user_created_notification(self, user_data):
        """
        Send a notification when a new user is created
        
        Args:
            user_data: Dictionary with user information (id, username, email)
        """
        try:
            # Convert timestamp to string if it's a datetime object
            timestamp = user_data.get("created_at")
            if timestamp and hasattr(timestamp, 'isoformat'):
                timestamp = timestamp.isoformat()
            
            message = {
                "type": "user_created",
                "user_id": user_data.get("id"),
                "username": user_data.get("username"),
                "email": user_data.get("email"),
                "timestamp": timestamp
            }
            return self.send_message(message)
        except Exception as e:
            logger.error(f"Error sending user notification: {e}")
            return False


# Singleton instance
queue_service = QueueService()
