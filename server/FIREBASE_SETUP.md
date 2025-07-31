# 🔥 Firebase Service Account Setup Guide

This guide will help you configure Firebase authentication for your Policy Analysis API.

## 📋 Prerequisites

- A Google account
- A Firebase project (or create one)

## 🚀 Step-by-Step Setup

### 1. Create/Select Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project" or select an existing project
3. Follow the setup wizard if creating a new project

### 2. Enable Authentication

1. In Firebase Console, go to **Authentication** in the left sidebar
2. Click **Get started**
3. Go to the **Sign-in method** tab
4. Enable the authentication methods you want to use:
   - **Email/Password** (recommended)
   - **Google** (optional)
   - **GitHub** (optional)

### 3. Generate Service Account Key

1. In Firebase Console, click the **gear icon** ⚙️ (Project Settings)
2. Go to the **Service accounts** tab
3. Click **Firebase Admin SDK**
4. Click **Generate new private key** button
5. Save the downloaded JSON file as `firebase-service-account-key.json` in the `config/` folder

### 4. Configure Your Environment

1. Copy the example environment file:
   ```bash
   cp env.example .env
   ```

2. Update your `.env` file with the correct path:
   ```
   FIREBASE_SERVICE_ACCOUNT_KEY_PATH=config/firebase-service-account-key.json
   ```

### 5. Test the Setup

Run the test script to verify everything is working:

```bash
python test_setup.py
```

## 🔧 Configuration Details

### Service Account Key Structure

Your `firebase-service-account-key.json` should look like this:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40your-project-id.iam.gserviceaccount.com"
}
```

### Security Best Practices

1. **Never commit your service account key** to version control
2. Add `config/firebase-service-account-key.json` to your `.gitignore`
3. Use environment variables in production
4. Rotate keys regularly

## 🧪 Testing Authentication

### Test with Frontend

1. In your React frontend, get a Firebase ID token:
   ```javascript
   import { getAuth, signInWithEmailAndPassword } from 'firebase/auth';
   
   const auth = getAuth();
   const userCredential = await signInWithEmailAndPassword(auth, email, password);
   const idToken = await userCredential.user.getIdToken();
   ```

2. Use the token in API requests:
   ```javascript
   const response = await fetch('/api/me', {
     headers: {
       'Authorization': `Bearer ${idToken}`
     }
   });
   ```

### Test with curl

```bash
# Replace YOUR_ID_TOKEN with an actual Firebase ID token
curl -H "Authorization: Bearer YOUR_ID_TOKEN" http://localhost:8000/me
```

## 🔍 Troubleshooting

### Common Issues

1. **"Invalid service account key"**
   - Check that the JSON file is valid
   - Verify the file path in `.env`

2. **"Invalid ID token"**
   - Ensure the token is fresh (not expired)
   - Check that the Firebase project matches

3. **"Service account not found"**
   - Verify the service account key is in the correct location
   - Check file permissions

### Debug Mode

Enable debug logging by setting:
```
FIREBASE_DEBUG=true
```

## 📚 Additional Resources

- [Firebase Admin SDK Documentation](https://firebase.google.com/docs/admin/setup)
- [Firebase Authentication](https://firebase.google.com/docs/auth)
- [Service Account Best Practices](https://cloud.google.com/iam/docs/service-accounts)

## 🎯 Next Steps

After setting up Firebase:

1. **Test the API**: Run `python test_setup.py`
2. **Start the server**: Run `python start.py`
3. **Integrate with frontend**: Update your React app to use Firebase Auth
4. **Deploy**: Configure environment variables in your production environment 