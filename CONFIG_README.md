# Flask Azure App - Environment Configuration

## Quick Start

### Development Mode
```bash
# Option 1: Set environment variable
export FLASK_ENV=development  # Linux/Mac
set FLASK_ENV=development     # Windows CMD
$env:FLASK_ENV="development"  # PowerShell

# Option 2: Update .env file
# Set FLASK_ENV=development in .env

# Run with Docker
docker-compose -f compose.dev.yaml up --build

# Or run locally
python run.py
```

### Production Mode
```bash
# Option 1: Set environment variable
export FLASK_ENV=production  # Linux/Mac
set FLASK_ENV=production     # Windows CMD
$env:FLASK_ENV="production"  # PowerShell

# Option 2: Update .env file
# Set FLASK_ENV=production in .env

# Run with Docker
docker-compose up --build

# Make sure to set a secure SECRET_KEY!
```

## Configuration Details

### Development
- **Database**: `flask_azure_dev`
- **Secret Key**: `dev-secret-key-not-secure` (hardcoded, not secure)
- **Debug**: `True`
- **Auto-reload**: Enabled

### Production
- **Database**: `flask_azure_prod`
- **Secret Key**: From `SECRET_KEY` environment variable (MUST be set!)
- **Debug**: `False`
- **Connection Pool**: Configured for performance

## Environment Variables

| Variable | Dev Default | Prod Required | Description |
|----------|-------------|---------------|-------------|
| `FLASK_ENV` | `development` | `production` | **Main toggle** |
| `DEV_DATABASE_URL` | Local PostgreSQL | - | Dev database connection |
| `DATABASE_URL` | - | ✅ Required | Prod database connection |
| `SECRET_KEY` | Hardcoded | ✅ Required | Session encryption key |

## Switching Environments

**Just change one flag:**
```bash
# .env file
FLASK_ENV=development  # or production
```

That's it! The app automatically uses the correct:
- Database connection
- Secret key
- Debug settings
- Connection pooling

## Security Notes

⚠️ **Production Checklist:**
1. Set `FLASK_ENV=production`
2. Generate strong `SECRET_KEY`: `python -c "import secrets; print(secrets.token_hex(32))"`
3. Use secure database password (not `postgres`)
4. Set proper environment variables in Azure App Service
5. Never commit `.env` file to Git!
