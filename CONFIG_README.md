# Flask Azure Application - Complete Playbook

> **Complete guide for deploying and managing a Flask REST API on Azure App Service**  
> Author: Kshitij Vyas | Last Updated: November 12, 2025

---

## 📑 Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Local Development Setup](#local-development-setup)
4. [Azure Services Configuration](#azure-services-configuration)
5. [Deployment Process](#deployment-process)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [Commands Reference](#commands-reference)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Docker Desktop (for local PostgreSQL)
- Azure Account (Free Tier)
- Git & GitHub Account
- VS Code (recommended)

### Environment Toggle
```bash
# .env file - THE MAIN SWITCH
FLASK_ENV=development  # Local development
FLASK_ENV=production   # Azure production
```

### Run Locally
```bash
# Start PostgreSQL (Docker)
docker-compose -f compose.yaml up -d

# Activate virtual environment
.\env\Scripts\activate  # Windows PowerShell
source env/bin/activate  # Linux/Mac

# Run Flask app
python run.py
```

---

## 🏗️ Architecture Overview

### Technology Stack
```
┌─────────────────────────────────────────────────────────┐
│                    GitHub Actions                        │
│              (CI/CD Pipeline - Auto Deploy)             │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│              Azure App Service (F1 Free)                │
│         flask-azure-app-kshitij-bme9fgf9e4e3chcj       │
│                                                          │
│  • Python 3.12                                          │
│  • Flask 3.1.2 REST API                                 │
│  • Gunicorn WSGI Server                                 │
│  • Startup Command: bash startup.sh                     │
└──────────────────┬──────────────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
┌──────────────────┐  ┌──────────────────┐
│  Azure Key Vault │  │ Neon PostgreSQL  │
│                  │  │   (Production)   │
│  • DATABASE_URL  │  │                  │
│  • SECRET_KEY    │  │  • SSL Required  │
└──────────────────┘  └──────────────────┘
```

### Azure Services Used

| Service | Name | Purpose | Tier |
|---------|------|---------|------|
| **App Service** | flask-azure-app-kshitij | Host Flask API | F1 Free |
| **Key Vault** | flask-keyvault-kshitij | Secure secrets storage | Standard |
| **Application Insights** | flask-app-insights | Monitoring & telemetry | Free (1GB/month) |
| **Blob Storage** | flaskstoragekvyas/images | Avatar file uploads | LRS (5GB free) |
| **Queue Storage** | user-notifications | Async messaging | Included with storage |
| **Redis Cache** | flask-redis-kshitij | Caching layer (paused) | Basic C0 (250MB) |
| **Azure Functions** | (local testing) | Queue message processor | Consumption (1M free) |

---

## 💻 Local Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/kshitijvyas/flask_azure.git
cd flask_azure
```

### 2. Create Virtual Environment
```bash
python -m venv env
.\env\Scripts\activate  # Windows
source env/bin/activate  # Linux/Mac
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure .env File
```properties
# Environment Mode
FLASK_ENV=development

# Local Development Database (Docker)
DEV_DATABASE_URL=postgresql://postgres:admin@localhost:5433/flask_azure_dev

# Azure Services (for local testing)
KEY_VAULT_NAME=flask-keyvault-kshitij
STORAGE_ACCOUNT_NAME=flaskstoragekvyas
STORAGE_CONTAINER_NAME=images
REDIS_URL=rediss://:PASSWORD@flask-redis-kshitij.redis.cache.windows.net:6380/0

# Application Insights
APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...
```

### 5. Start Local PostgreSQL
```bash
docker-compose -f compose.yaml up -d
```

### 6. Run Migrations
```bash
flask db upgrade
```

### 7. Start Flask App
```bash
python run.py
# API available at: http://localhost:5000
```

---

## ☁️ Azure Services Configuration

### 1. Azure App Service Setup

#### Create App Service (Portal)
1. **Azure Portal** → **App Services** → **+ Create**
2. **Resource Group**: `flask-azure-rg`
3. **Name**: `flask-azure-app-kshitij` (generates unique URL)
4. **Runtime**: Python 3.12
5. **Region**: Canada Central
6. **Pricing**: F1 (Free tier - 60 min/day)

6. **Pricing**: F1 (Free tier - 60 min/day)

#### Configure Environment Variables
**Location**: App Service → **Settings** → **Environment variables** → **Application settings**

| Name | Value | Purpose |
|------|-------|---------|
| `FLASK_ENV` | `production` | Enable production mode |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` | Build during deployment |
| `STORAGE_ACCOUNT_NAME` | `flaskstoragekvyas` | Blob storage config |
| `STORAGE_CONTAINER_NAME` | `images` | Avatar container |
| `REDIS_URL` | `rediss://...` | Redis connection string |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | `InstrumentationKey=...` | Monitoring |

⚠️ **Note**: `DATABASE_URL` and `SECRET_KEY` are stored in **Key Vault**, not here!

#### Configure Startup Command
**Location**: App Service → **Settings** → **Configuration** → **General settings** → **Stack settings**

```bash
Startup Command: bash startup.sh
```

**startup.sh** does:
```bash
python -m flask db upgrade  # Run migrations
gunicorn --bind=0.0.0.0:8000 --timeout 600 run:app  # Start server
```

---

### 2. Azure Key Vault Setup

#### Create Key Vault (Portal)
1. **Create a resource** → **Key Vault**
2. **Name**: `flask-keyvault-kshitij`
3. **Region**: Canada Central
4. **Pricing**: Standard
5. **Access configuration**: RBAC (Role-Based Access Control)

#### Grant App Service Access
1. Key Vault → **Access control (IAM)** → **+ Add role assignment**
2. **Role**: `Key Vault Secrets User`
3. **Assign access to**: Managed Identity
4. **Select members**: Choose **App Service** → `flask-azure-app-kshitij`
5. Click **Review + assign**

#### Add Secrets
1. Key Vault → **Objects** → **Secrets** → **+ Generate/Import**
2. Add these secrets:

| Secret Name | Value | How to Generate |
|-------------|-------|-----------------|
| `DATABASE-URL` | `postgresql://user:pass@host:5432/db?ssl=require` | From Neon.tech dashboard |
| `SECRET-KEY` | `64-char hex string` | `python -c "import secrets; print(secrets.token_hex(32))"` |

⚠️ **Important**: Secret names use hyphens (`-`), not underscores!

---

### 3. Application Insights Setup

#### Create Application Insights (Portal)
1. **Create a resource** → **Application Insights**
2. **Name**: `flask-app-insights`
3. **Resource Group**: `flask-azure-rg`
4. **Region**: Canada Central

#### Get Connection String
1. Application Insights → **Overview**
2. Copy **Connection String**
3. Add to App Service environment variables as `APPLICATIONINSIGHTS_CONNECTION_STRING`

#### Implementation
```python
# app/__init__.py
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.instrumentation.flask import FlaskInstrumentor

configure_azure_monitor(connection_string=appinsights_connection_string)
FlaskInstrumentor().instrument_app(app)
```

---

### 4. Blob Storage Setup (Avatar Uploads)

#### Create Storage Account (Portal)
1. **Create a resource** → **Storage accounts** → **+ Create**
2. **Name**: `flaskstoragekvyas` (globally unique, lowercase)
3. **Performance**: Standard
4. **Redundancy**: LRS (Locally-redundant)
5. **Region**: Canada Central

#### Create Container
1. Storage Account → **Data storage** → **Containers** → **+ Container**
2. **Name**: `images`
3. **Public access level**: Private

#### Grant Managed Identity Access
1. Storage Account → **Access Control (IAM)** → **+ Add role assignment**
2. **Role**: `Storage Blob Data Contributor`
3. **Assign access to**: Managed Identity
4. **Select members**: **App Service** → `flask-azure-app-kshitij`
5. Click **Review + assign**

#### Implementation
```python
# app/services/storage_service.py
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(
    account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
    credential=credential
)
```

---

### 5. Queue Storage Setup (Async Messaging)

#### Create Queue
1. Storage Account (`flaskstoragekvyas`) → **Data storage** → **Queues** → **+ Queue**
2. **Name**: `user-notifications`

#### Grant Access (Already done if Blob access granted)
**Role**: `Storage Queue Data Contributor`

#### Implementation
```python
# app/services/queue_service.py
from azure.storage.queue import QueueClient
from azure.identity import DefaultAzureCredential

queue_client = QueueClient(
    account_url=f"https://{STORAGE_ACCOUNT_NAME}.queue.core.windows.net",
    queue_name="user-notifications",
    credential=DefaultAzureCredential()
)
```

---

### 6. Redis Cache Setup (Performance Optimization)

#### Create Redis Cache (Portal)
1. **Create a resource** → **Azure Cache for Redis**
2. **Name**: `flask-redis-kshitij`
3. **Cache type**: Basic C0 (250MB)
4. **Region**: Canada Central

#### Get Connection String
1. Redis Cache → **Settings** → **Access keys**
2. Copy **Primary connection string**
3. Convert format from:
   ```
   rediss://:PASSWORD@HOST:6380
   ```
   To:
   ```
   rediss://:PASSWORD@HOST:6380/0?ssl_cert_reqs=required
   ```

#### Enable Azure Services Access
1. Redis Cache → **Settings** → **Networking/Firewall**
2. **Enable**: ☑️ Allow access from Azure services

⚠️ **Current Status**: Implementation complete, but networking access blocked. Enable firewall rule to activate.

---

### 7. Azure Functions Setup (Queue Processor)

#### Local Testing Setup
```bash
cd azure_functions
pip install -r requirements.txt
```

#### Get Storage Connection String
1. Storage Account → **Security + networking** → **Access keys**
2. Under **key1**, click **Show** → Copy **Connection string**

#### Configure local.settings.json
```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "<PASTE_CONNECTION_STRING_HERE>"
  }
}
```

#### Run Locally
```bash
func start
```

You should see:
```
Functions:
  process_user_notifications: queueTrigger
```

#### Deploy to Azure (Future)
```bash
# Create Function App
az functionapp create \
  --name flask-queue-processor-kshitij \
  --storage-account flaskstoragekvyas \
  --resource-group flask-azure-rg \
  --consumption-plan-location canadacentral \
  --runtime python --runtime-version 3.12 \
  --functions-version 4

# Deploy
func azure functionapp publish flask-queue-processor-kshitij
```

---

## 🚀 Deployment Process

### GitHub Actions CI/CD Pipeline

#### Workflow File
**Location**: `.github/workflows/azure-deploy.yml`

**Triggered by**: Push to `main` branch

**Process**:
1. **Build Job**:
   - Checkout code
   - Setup Python 3.12
   - Install dependencies
   - Create deployment zip (excludes venv, .git, __pycache__)
   - Upload artifact

2. **Deploy Job**:
   - Download artifact
   - Unzip package
   - Deploy to Azure App Service using publish profile

#### Setup Deployment

##### Option 1: Deployment Center (Automatic)
1. App Service → **Deployment** → **Deployment Center**
2. **Source**: GitHub
3. **Organization**: kshitijvyas
4. **Repository**: flask_azure
5. **Branch**: main
6. Click **Save**

##### Option 2: Manual Setup with Publish Profile
1. App Service → **Get publish profile** (download)
2. GitHub repo → **Settings** → **Secrets and variables** → **Actions**
3. **New repository secret**:
   - **Name**: `AZUREAPPSERVICE_PUBLISHPROFILE`
   - **Value**: Paste entire contents of .PublishSettings file
4. Push workflow file to trigger deployment

#### Monitor Deployment
- **GitHub**: https://github.com/kshitijvyas/flask_azure/actions
- **Azure**: App Service → **Deployment** → **Deployment Center** → **Logs**

---

## 🐛 Troubleshooting Guide

### Common Issues

#### 1. "Column does not exist" Error
**Symptom**: `column "avatar_url" does not exist`

**Cause**: Migration not run on Azure

**Solution**:
- Ensure `startup.sh` contains: `python -m flask db upgrade`
- Check App Service logs: **Monitoring** → **Log stream**

---

#### 2. SSL Connection Error (Neon PostgreSQL)
**Symptom**: `SSL connection has been closed unexpectedly`

**Solution**: Add SSL config in `app/config.py`:
```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'connect_args': {
        'sslmode': 'require',
        'connect_timeout': 10
    },
    'pool_pre_ping': True,
    'pool_recycle': 300
}
```

---

#### 3. GitHub Actions Artifact Deprecated
**Symptom**: Warning about `actions/upload-artifact@v3`

**Solution**: Update workflow to use `v4`:
```yaml
- uses: actions/upload-artifact@v4
- uses: actions/download-artifact@v4
```

---

#### 4. Blob Storage ContentSettings Error
**Symptom**: `ContentSettings() got an unexpected keyword argument 'content_type'`

**Solution**: Import and use `ContentSettings` properly:
```python
from azure.storage.blob import ContentSettings

blob_client.upload_blob(
    file_data,
    overwrite=True,
    content_settings=ContentSettings(content_type=content_type)
)
```

---

#### 5. Redis Connection Timeout
**Symptom**: `ERROR - Redis connection failed: Timeout connecting to server`

**Solution**:
1. Redis Cache → **Networking** → Enable "Allow access from Azure services"
2. Restart App Service

---

#### 6. Queue Service 500 Error
**Symptom**: 500 error when creating users

**Cause**: Timestamp serialization or missing error handling

**Solution**: Already implemented - queue service has graceful fallback

---

### Viewing Logs

#### Azure App Service Logs
**Location**: App Service → **Monitoring** → **Log stream**

**What you'll see**:
- Application startup logs
- Gunicorn worker logs
- Custom logging (logger.info/error)
- Application Insights telemetry

#### Application Insights
**Location**: Application Insights → **Monitoring** → **Logs**

**Sample Query**:
```kql
requests
| where timestamp > ago(1h)
| summarize count() by resultCode
| render piechart
```

---

## 📝 Commands Reference

### Git Commands
```bash
# Commit and deploy
git add .
git commit -m "Your message"
git push  # Triggers GitHub Actions deployment

# View commit history
git log --oneline -n 10

# Check status
git status
```

### Flask Migration Commands
```bash
# Create migration
flask db migrate -m "Description"

# Apply migrations
flask db upgrade

# Rollback
flask db downgrade
```

### Docker Commands
```bash
# Start PostgreSQL
docker-compose -f compose.yaml up -d

# Stop PostgreSQL
docker-compose -f compose.yaml down

# View logs
docker-compose logs -f
```

### Azure Functions Commands
```bash
# Initialize project
func init . --python

# Run locally
func start

# Deploy to Azure
func azure functionapp publish <app-name>
```

### API Testing Commands (PowerShell)
```powershell
# GET request
Invoke-WebRequest -Uri "https://flask-azure-app-kshitij-bme9fgf9e4e3chcj.canadacentral-01.azurewebsites.net/api/users/1" `
  -Method GET | Select-Object -ExpandProperty Content

# POST request
Invoke-WebRequest -Uri "https://flask-azure-app-kshitij-bme9fgf9e4e3chcj.canadacentral-01.azurewebsites.net/api/users" `
  -Method POST `
  -Body '{"username":"test","email":"test@example.com","password_hash":"pass123"}' `
  -ContentType "application/json" | Select-Object -ExpandProperty Content

# PUT request
Invoke-WebRequest -Uri "https://flask-azure-app-kshitij-bme9fgf9e4e3chcj.canadacentral-01.azurewebsites.net/api/users/1" `
  -Method PUT `
  -Body '{"username":"updated"}' `
  -ContentType "application/json"
```

---

## 🎯 Project Summary

### Completed Projects

#### ✅ Project 1: Application Insights
- Migrated from opencensus to OpenTelemetry (Flask 3.x compatible)
- Automatic request tracking and telemetry
- Real-time monitoring in Azure Portal

#### ✅ Project 2: Blob Storage  
- Avatar upload functionality  
- Managed Identity authentication  
- Proper MIME type handling  
- Test URL: https://flaskstoragekvyas.blob.core.windows.net/images/92f3558a-579f-4efa-9e54-d558dd812120.jpg

#### ⏸️ Project 3: Redis Cache (Paused)
- Complete implementation with graceful fallback
- Cache keys: `user:{id}` (TTL: 600s), `users:all` (TTL: 300s)
- Cache invalidation on mutations
- **Blocked by**: Network firewall - need to enable Azure services access

#### ✅ Project 4: Queue Storage
- Async messaging for user notifications
- Queue: `user-notifications`
- JSON message serialization
- Managed Identity authentication

#### 🔄 Project 5: Azure Functions (In Progress)
- Queue-triggered function for processing notifications
- Local testing complete
- Simulates welcome email sending
- **Next**: Deploy to Azure Function App

---

## 🔐 Security Best Practices

### ✅ Implemented
- Managed Identity for Azure resources (no connection strings in code)
- Key Vault for sensitive secrets
- SSL/TLS for all connections
- Private blob containers
- RBAC for fine-grained access control

### 🚨 Production Checklist
- [ ] Change default SECRET_KEY
- [ ] Use strong database passwords  
- [ ] Enable Azure DDoS Protection
- [ ] Set up Azure Front Door for WAF
- [ ] Configure custom domain with SSL
- [ ] Enable App Service authentication
- [ ] Set up backup and disaster recovery
- [ ] Configure monitoring alerts
- [ ] Review and rotate access keys regularly

---

## 📚 Additional Resources

### Azure Documentation
- [App Service](https://learn.microsoft.com/en-us/azure/app-service/)
- [Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/)
- [Blob Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/)
- [Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/)
- [Redis Cache](https://learn.microsoft.com/en-us/azure/azure-cache-for-redis/)

### Project Links
- **GitHub Repo**: https://github.com/kshitijvyas/flask_azure
- **Live API**: https://flask-azure-app-kshitij-bme9fgf9e4e3chcj.canadacentral-01.azurewebsites.net
- **API Docs**: {your-api}/api/docs (if Swagger enabled)

---

## 📞 Support & Maintenance

### Regular Tasks
- **Daily**: Monitor Application Insights for errors
- **Weekly**: Review deployment logs, check disk usage
- **Monthly**: Rotate access keys, review security logs
- **Quarterly**: Update Python packages, review Azure costs

### Contact
- **Developer**: Kshitij Vyas
- **GitHub**: @kshitijvyas
- **Project**: Flask Azure Learning - Senior Developer Upskilling

---

**Last Updated**: November 12, 2025  
**Version**: 2.0  
**Status**: Production-ready (with Redis networking pending)

---

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

TO add appinsights:
Go to add resources - app insights add ifo,
Copy insight string add in .env file.
Use in the code.
INitialize the code in init.py

TO Add Blob Storage:
 Create Storage Account (Portal Steps)
Go to Azure Portal → Search "Storage accounts" → Click "+ Create"

Fill in the details:

Resource Group: flask-azure-rg (same as your app)
Storage account name: flaskstoragekvyas (must be globally unique, lowercase, no hyphens)
Region: Canada Central (same as your app)
Performance: Standard
Redundancy: LRS (Locally-redundant storage) ← Cheapest, perfect for learning
Click "Review + Create" → "Create"

After creation, go to the Storage Account -> your account -> datastorage → Click "Containers" (left menu under "Data storage")

Create a container:

Click "+ Container"
Name: avatars
Public access level: Private (we'll use managed identity)
Click "Create"

Perfect! Got it:

Storage Account: flaskstoragekvyas
Container: images
Now let's grant Managed Identity access:

Grant Access (Portal)
Go to Storage Account "flaskstoragekvyas"
Click "Access Control (IAM)" in left sidebar
Click "+ Add" → "Add role assignment"
Role tab:
Search: "Storage Blob Data Contributor"
Select it → Click "Next"
Members tab:
Select "Managed identity"
Click "+ Select members"
Managed identity dropdown: Choose "App Service"
Select: "flask-azure-app-kshitij..."
Click "Select"
Click "Review + assign" → "Review + assign"


***************----------------***********************
Perfect! Now we need to add the storage configuration to Azure App Service environment variables. Let's do that:
Add Storage Config via Portal
Go to Azure Portal → Your App Service (flask-azure-app-kshitij...)

In the left sidebar, find "Settings" section → Click "Environment variables"

Click "+ Add" (under Application settings)

Add these two settings:

First setting:

Name: STORAGE_ACCOUNT_NAME
Value: flaskstoragekvyas
Click "Apply"
Second setting:

Name: STORAGE_CONTAINER_NAME
Value: images
Click "Apply"
Click "Apply" at the bottom of the page

Click "Confirm" when prompted (this will restart your app)

If you are using startup.sh then you need to add this in your stach settings options under Settings -> configuration -> Stack settings

Implement Redis on azure:
Search for Azure Cache for Redis

To run any webservice from terminal
Invoke-WebRequest -Uri "https://flask-azure-app-kshitij-bme9fgf9e4e3chcj.canadacentral-01.azurewebsites.net/api/users/1" -Method GET | Select-Object -ExpandProperty Content

Azure Queues for 
Created the queue ✅
Granted the IAM role ✅
 Azure Storage Queues for async messaging
✅ Managed Identity authentication for queues
✅ Decoupling user creation from notifications
✅ Message serialization with JSON


To make azure function:
1. func init . --python
2. create a queue-triggered function
3. func new --name ProcessUserNotifications --template "Azure Queue Storage trigger" --authlevel "function"
4. func templates list

Next Steps to Test Azure Functions:
1. Get Storage Account Connection String
Azure Portal → flaskstoragekvyas
Left sidebar → Access keys
Click Show next to Connection string under key1
Copy the entire connection string
2. Update local.settings.json
Open local.settings.json and paste the connection string in the AzureWebJobsStorage value.

3. Install Function Dependencies
4. Run the Function Locally
to start the function
func start
You should see: