# Google Drive API Integration Setup

## Overview

The chatbot platform can automatically upload processed documents to Google Drive for backup and sharing. This is an **optional feature** that provides additional document management capabilities.

## Benefits

- ✅ **Automatic Backup** - Documents are safely stored in Google Drive
- ✅ **Easy Sharing** - Share documents via Google Drive links
- ✅ **Organization** - Documents organized in dedicated folders
- ✅ **Version Control** - Google Drive handles file versioning
- ✅ **Access Control** - Use Google Drive permissions

## Setup Instructions

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Note your project ID for later

### Step 2: Enable Google Drive API

1. In Google Cloud Console, navigate to **APIs & Services > Library**
2. Search for "Google Drive API"
3. Click on "Google Drive API" and click **Enable**

### Step 3: Create Service Account

1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > Service Account**
3. Fill in the details:
   - **Service account name**: `chatbot-drive-service`
   - **Service account ID**: `chatbot-drive-service`
   - **Description**: `Service account for chatbot document uploads`
4. Click **Create and Continue**
5. Skip the optional steps and click **Done**

### Step 4: Generate Service Account Key

1. In the **Credentials** page, find your service account
2. Click on the service account email
3. Go to the **Keys** tab
4. Click **Add Key > Create new key**
5. Select **JSON** format
6. Click **Create**
7. **Save the downloaded JSON file securely** - you'll need this

### Step 5: Setup Google Drive Folder

#### Option A: Use Existing Folder
1. Open [Google Drive](https://drive.google.com/)
2. Navigate to the folder where you want documents uploaded
3. Copy the folder ID from the URL:
   ```
   https://drive.google.com/drive/folders/1ABCDEFghijklmnop123456789
   ```
   The folder ID is: `1ABCDEFghijklmnop123456789`

#### Option B: Create New Folder Programmatically
The system can create a folder automatically (see configuration below).

### Step 6: Share Folder with Service Account

1. In Google Drive, right-click on your target folder
2. Click **Share**
3. Add the service account email (from Step 3)
   - Format: `chatbot-drive-service@your-project-id.iam.gserviceaccount.com`
4. Set permission to **Editor**
5. Click **Send**

### Step 7: Configure Environment

1. **Place the JSON credentials file** in your backend directory:
   ```bash
   # Example placement
   backend/
   ├── google-drive-credentials.json  # Your downloaded JSON file
   ├── app/
   └── requirements.txt
   ```

2. **Update your `.env` file**:
   ```env
   # Google Drive Integration
   GOOGLE_DRIVE_CREDENTIALS_PATH=./google-drive-credentials.json
   GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
   ```

### Step 8: Test the Integration

```bash
cd backend
python -c "
from app.services.document_service import document_service
import asyncio

async def test_drive():
    # Test service initialization
    if document_service.drive_service:
        print('✅ Google Drive service initialized successfully')
        
        # Test folder creation (optional)
        folder_id = document_service.create_drive_folder('Test Chatbot Documents')
        if folder_id:
            print(f'✅ Created test folder: {folder_id}')
        else:
            print('ℹ️ Using existing folder configuration')
    else:
        print('❌ Google Drive service not available')

asyncio.run(test_drive())
"
```

## Configuration Options

### Environment Variables

Add these to your `.env` file:

```env
# Required: Path to your service account JSON file
GOOGLE_DRIVE_CREDENTIALS_PATH=./google-drive-credentials.json

# Optional: Specific folder ID for uploads
# If not provided, files upload to root directory
GOOGLE_DRIVE_FOLDER_ID=1ABCDEFghijklmnop123456789
```

### Automatic Folder Creation

If you don't specify a `GOOGLE_DRIVE_FOLDER_ID`, you can create one programmatically:

```python
from app.services.document_service import document_service

# Create a new folder for your chatbot
folder_id = document_service.create_drive_folder("My Chatbot Documents")
print(f"Created folder ID: {folder_id}")

# Add this ID to your .env file
```

## File Organization

Documents will be organized as follows:

```
Google Drive/
└── Your Configured Folder/
    ├── document1.pdf
    ├── document2.txt
    ├── document3.docx
    └── ...
```

Each uploaded document includes:
- **Original filename**
- **Upload timestamp** 
- **Automatic Google Drive versioning**

## Security Considerations

### Service Account Security

1. **Keep credentials secure**: Never commit the JSON file to version control
2. **Limit permissions**: Service account only has access to shared folders
3. **Regular rotation**: Rotate service account keys periodically
4. **Environment-specific**: Use different service accounts for dev/prod

### Access Control

1. **Folder permissions**: Only share folders with necessary service accounts
2. **Organization policies**: Follow your organization's Google Workspace policies
3. **Audit logs**: Monitor Google Drive API usage in Cloud Console

## Troubleshooting

### Common Issues

#### "Credentials not found" Error
**Problem**: `GOOGLE_DRIVE_CREDENTIALS_PATH` file doesn't exist
**Solution**:
```bash
# Check file exists
ls -la ./google-drive-credentials.json

# Update path in .env if needed
GOOGLE_DRIVE_CREDENTIALS_PATH=/full/path/to/credentials.json
```

#### "Access denied" Error
**Problem**: Service account doesn't have access to folder
**Solution**:
1. Check folder is shared with service account email
2. Verify service account has "Editor" permissions
3. Ensure folder ID is correct

#### "API not enabled" Error
**Problem**: Google Drive API not enabled in project
**Solution**:
1. Go to Google Cloud Console
2. Enable Google Drive API for your project

#### "Quota exceeded" Error
**Problem**: Too many API requests
**Solution**:
1. Check quotas in Google Cloud Console
2. Implement request throttling if needed
3. Consider upgrading quota limits

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.getLogger('googleapiclient').setLevel(logging.DEBUG)
```

### Validate Setup

```bash
# Test Google Drive API access
python -c "
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

creds = Credentials.from_service_account_file(
    './google-drive-credentials.json',
    scopes=['https://www.googleapis.com/auth/drive']
)

service = build('drive', 'v3', credentials=creds)
results = service.files().list(pageSize=1).execute()
print('✅ Google Drive API access successful')
"
```

## Optional Features

### Advanced File Management

The service supports additional Google Drive features:

1. **File versioning**: Automatic when uploading same filename
2. **Metadata**: Custom properties can be added to files
3. **Sharing**: Programmatic sharing with specific users
4. **Permissions**: Fine-grained access control

### Integration with Other Google Services

- **Google Docs**: Convert documents to Google Docs format
- **Google Sheets**: Export data to spreadsheets
- **Google Apps Script**: Automate workflows

## API Usage Monitoring

Monitor your Google Drive API usage:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services > Dashboard**
3. Click on **Google Drive API**
4. Monitor quotas and usage patterns

### Quota Limits

- **Per-user rate limit**: 1,000 requests per 100 seconds
- **Per-user rate limit**: 100 requests per 100 seconds per user
- **Daily quota**: 20,000 requests per day (default)

For production usage, consider requesting quota increases.

## Summary

After completing this setup:

1. ✅ Documents automatically backup to Google Drive
2. ✅ Organized folder structure
3. ✅ Secure service account access
4. ✅ Optional folder creation capabilities
5. ✅ Integration with existing chatbot workflow

Your chatbot platform now has robust document management with Google Drive integration!