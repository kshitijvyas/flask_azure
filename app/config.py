import os
from dotenv import load_dotenv

load_dotenv()


def get_secret(secret_name, default=None):
    """Get secret from Azure Key Vault or environment variable"""
    # Try environment variable first (for local development)
    value = os.environ.get(secret_name.replace('-', '_'))
    if value:
        return value
    
    # Try Azure Key Vault (for production)
    try:
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient
        
        key_vault_name = os.environ.get('KEY_VAULT_NAME', 'flask-keyvault-kshitij')
        key_vault_uri = f"https://{key_vault_name}.vault.azure.net"
        
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=key_vault_uri, credential=credential)
        secret = client.get_secret(secret_name)
        return secret.value
    except Exception as e:
        print(f"Could not retrieve secret {secret_name} from Key Vault: {e}")
        return default


class Config:
    """Base configuration"""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = get_secret('SECRET-KEY') or os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    # Azure Blob Storage
    STORAGE_ACCOUNT_NAME = os.environ.get('STORAGE_ACCOUNT_NAME', 'flaskstoragekvyas')
    STORAGE_CONTAINER_NAME = os.environ.get('STORAGE_CONTAINER_NAME', 'images')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'postgresql://postgres:postgres@localhost:5432/flask_azure_dev'
    SECRET_KEY = 'dev-secret-key-not-secure'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = get_secret('DATABASE-URL') or os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:postgres@localhost:5432/flask_azure_prod'
    SECRET_KEY = get_secret('SECRET-KEY') or os.environ.get('SECRET_KEY')
    
    # PostgreSQL connection pool settings (for Neon.tech compatibility)
    SQLALCHEMY_POOL_SIZE = 5
    SQLALCHEMY_POOL_RECYCLE = 300  # Recycle connections every 5 minutes
    SQLALCHEMY_POOL_PRE_PING = True  # Check connection before using
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'connect_args': {
            'sslmode': 'require',  # Required for Neon.tech
            'connect_timeout': 10
        }
    }


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on FLASK_ENV flag"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
