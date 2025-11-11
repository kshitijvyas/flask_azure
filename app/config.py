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
    
    # Additional production settings
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_RECYCLE = 3600


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
