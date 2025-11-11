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


FOR AZURE DB connection:
a. Setting -> cofiguration -> app setting.
b. If above not found:- Settings environment variable then add below:
1. DATABASE_URL = This is for now taken from neon.net
2. FLASK_ENV = prod
3. SCM_DO_BUILD_DURING_DEPLOYMENT
4. SECRET_KEY = #Generated on terminal -- python -c "import secrets; print(secrets.token_hex(32))"

Set UP cinfiguration for github:
1. Go to Deployment Center and enter the required fields.

If there is issue with the github flow then we need to download the publish profile and setup up the flow manually:-
check.github\workflows -> azure-deploy.yml
open downloedede settings file.
Go to your github repo -> settings -> secrets and variables ->
actions -> new repository secret
Go to your GitHub repository: https://github.com/kshitijvyas/flask_azure
Click Settings (top tab)
In left menu, click Secrets and variables → Actions
Click "New repository secret"
Fill in:
Name: AZUREAPPSERVICE_PUBLISHPROFILE
Value: Open the .PublishSettings file and copy ALL its contents
Click Add secret

Step 4: Push Workflow to GitHub
git add .github/workflows/azure-deploy.yml
git commit -m "Add GitHub Actions deployment workflow"
git push

This will trigger automatic deployment!
We can check logs on github and azure logs in development center as success.

Keyvaultsetup:
Step 1: Create Azure Key Vault
Via Azure Portal:
Go to Azure Portal: https://portal.azure.com
Click "Create a resource"
Search for "Key Vault"
Click Create

Step 2: Add Secrets to Key Vault
Once created:

Go to your Key Vault resource
In left menu, click "Secrets" (under Objects)
Click "+ Generate/Import"

If above not works:
Use RBAC Instead (Azure's Modern Way)
Step 1: Assign Role to Your App
Go to your Key Vault (flask-keyvault-kshitij) in Azure Portal
In the left menu, click "Access control (IAM)"
Click "+ Add" → "Add role assignment"
Step 2: Select Role
Search for: "Key Vault Secrets User"
Select it
Click Next
Step 3: Assign to Your App
Assign access to: Select "Managed identity"
Click "+ Select members"
Subscription: Select your subscription
Managed identity: Select "App Service" from dropdown
You should see: flask-azure-app-kshitij (your app)
Click on it to select
Click "Select" (bottom)
Click "Review + assign"
Click "Review + assign" again

Why System-Assigned vs User-Assigned?
System-assigned (What we need):

✅ Automatically created with the app
✅ Deleted when app is deleted
✅ Simpler for single app scenarios
✅ What our code expects
User-assigned:

Used for multiple resources sharing same identity
More complex setup
Not needed for our use case

TO add appinghts:
Go to add resources - app insights add ifo,
Copy insight string.
Use in the code.
INitialize the code in init.py
