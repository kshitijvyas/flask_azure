"""
Azure Blob Storage Service
Handles file uploads and deletions using Azure Blob Storage with Managed Identity
"""
import os
import uuid
from flask import current_app
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential


class StorageService:
    """Service for managing blob storage operations"""
    
    def __init__(self):
        self.account_name = None
        self.container_name = None
        self.blob_service_client = None
    
    def _initialize(self):
        """Initialize blob service client with Managed Identity"""
        if self.blob_service_client:
            return
        
        self.account_name = current_app.config.get('STORAGE_ACCOUNT_NAME')
        self.container_name = current_app.config.get('STORAGE_CONTAINER_NAME')
        
        if not self.account_name or not self.container_name:
            raise ValueError("Storage account name and container name must be configured")
        
        # Use Managed Identity for authentication (works in Azure)
        # Falls back to local credentials for development
        account_url = f"https://{self.account_name}.blob.core.windows.net"
        credential = DefaultAzureCredential()
        
        self.blob_service_client = BlobServiceClient(account_url, credential=credential)
    
    def upload_file(self, file_data, filename, content_type=None):
        """
        Upload a file to blob storage
        
        Args:
            file_data: File bytes or file-like object
            filename: Original filename
            content_type: MIME type (e.g., 'image/jpeg')
        
        Returns:
            str: Public URL of the uploaded blob
        """
        self._initialize()
        
        # Generate unique blob name to avoid conflicts
        file_extension = os.path.splitext(filename)[1]
        blob_name = f"{uuid.uuid4()}{file_extension}"
        
        # Get blob client
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=blob_name
        )
        
        # Upload with content type
        from azure.storage.blob import ContentSettings
        
        content_settings = ContentSettings(content_type=content_type) if content_type else None
        blob_client.upload_blob(
            file_data,
            content_settings=content_settings,
            overwrite=True
        )
        
        # Return the blob URL
        return blob_client.url
    
    def delete_file(self, blob_url):
        """
        Delete a file from blob storage
        
        Args:
            blob_url: Full URL of the blob to delete
        
        Returns:
            bool: True if deleted successfully
        """
        self._initialize()
        
        try:
            # Extract blob name from URL
            # URL format: https://{account}.blob.core.windows.net/{container}/{blob_name}
            blob_name = blob_url.split(f"{self.container_name}/")[-1]
            
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            blob_client.delete_blob()
            return True
        except Exception as e:
            print(f"Error deleting blob: {e}")
            return False
    
    def get_blob_url(self, blob_name):
        """Get the public URL for a blob"""
        self._initialize()
        return f"https://{self.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}"


# Singleton instance
storage_service = StorageService()
