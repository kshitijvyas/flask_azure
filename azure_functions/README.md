# Azure Functions - User Notifications Processor

This Azure Function processes messages from the `user-notifications` queue when new users are created.

## Setup Instructions

### 1. Get Storage Account Connection String

1. Go to **Azure Portal**
2. Navigate to **flaskstoragekvyas** storage account
3. Left sidebar → **Access keys**
4. Under **key1**, click **Show** next to **Connection string**
5. Click **Copy** to copy the connection string

### 2. Update local.settings.json

Open `local.settings.json` and paste the connection string:

```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "<PASTE_CONNECTION_STRING_HERE>"
  }
}
```

### 3. Install Dependencies

```bash
cd azure_functions
pip install -r requirements.txt
```

### 4. Run Function Locally

```bash
func start
```

The function will:
- Listen to the `user-notifications` queue
- Process messages when users are created
- Log welcome email simulation

### 5. Test It

1. Keep the function running
2. Create a new user via your Flask API:
   ```bash
   POST /api/users
   {
     "username": "testfunc",
     "email": "func@example.com",
     "password_hash": "password123"
   }
   ```
3. Watch the function logs - you'll see:
   ```
   📧 SENDING WELCOME EMAIL
      To: func@example.com
      Subject: Welcome to our platform, testfunc!
   ✅ Email sent successfully!
   ```

## Deploy to Azure (Later)

```bash
# Create Function App in Azure
az functionapp create --name flask-queue-processor-kshitij \
  --storage-account flaskstoragekvyas \
  --resource-group <your-resource-group> \
  --consumption-plan-location canadacentral \
  --runtime python --runtime-version 3.12 \
  --functions-version 4

# Deploy
func azure functionapp publish flask-queue-processor-kshitij
```

## What This Function Does

- **Trigger**: Queue message in `user-notifications`
- **Action**: Processes user creation events
- **Output**: Logs welcome email (can be extended to send real emails with SendGrid/SES)
- **Scaling**: Automatically scales based on queue depth
- **Cost**: Free tier (1M executions/month)
