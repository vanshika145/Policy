# Policy Analysis API

A FastAPI backend for uploading and analyzing policy documents with Firebase authentication.

## Features

- 🔐 Firebase Authentication integration
- 📁 File upload support for PDF, DOCX, DOC, and EML files
- 💾 PostgreSQL database with SQLAlchemy ORM
- 🚀 FastAPI with automatic API documentation
- 🔒 Protected routes with JWT token verification

## Setup Instructions

### 1. Install Dependencies

```bash
cd server
pip install -r requirements.txt
```

### 2. Database Setup

1. Install PostgreSQL on your system
2. Create a new database:
   ```sql
   CREATE DATABASE policy_db;
   ```
3. Update the `DATABASE_URL` in your `.env` file

### 3. Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or use existing one
3. Go to Project Settings > Service Accounts
4. Generate a new private key (JSON file)
5. Save the JSON file securely and update `FIREBASE_SERVICE_ACCOUNT_KEY_PATH` in your `.env` file

### 4. Environment Configuration

Copy `env.example` to `.env` and update the values:

```bash
cp env.example .env
```

Update the following variables:
- `DATABASE_URL`: Your PostgreSQL connection string
- `FIREBASE_SERVICE_ACCOUNT_KEY_PATH`: Path to your Firebase service account key

### 5. Run the Application

```bash
# Development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication
All protected endpoints require a Firebase ID token in the Authorization header:
```
Authorization: Bearer <firebase_id_token>
```

### Endpoints

#### `GET /`
- **Description**: Health check
- **Authentication**: None
- **Response**: API status

#### `GET /me`
- **Description**: Get current user information
- **Authentication**: Required
- **Response**: User details (Firebase UID, email, display name)

#### `POST /upload`
- **Description**: Upload a file (PDF, DOCX, DOC, or EML)
- **Authentication**: Required
- **Request**: Multipart form with file
- **Response**: Upload confirmation with file details

#### `GET /files`
- **Description**: Get all files uploaded by current user
- **Authentication**: Required
- **Response**: List of uploaded files

#### `GET /health`
- **Description**: Health check endpoint
- **Authentication**: None
- **Response**: Health status

## Database Schema

### Users Table
- `id` (PK): Auto-incrementing integer
- `firebase_uid` (unique): Firebase user ID
- `display_name`: User's display name
- `email`: User's email address
- `created_at`: Timestamp of account creation

### Uploaded Files Table
- `id` (PK): Auto-incrementing integer
- `user_id` (FK): Reference to users table
- `filename`: Original filename
- `file_type`: File type (pdf, docx, doc, eml)
- `upload_time`: Timestamp of upload
- `file_path`: Path to stored file

## File Upload

### Supported Formats
- **PDF**: `.pdf` files
- **Word Documents**: `.docx` and `.doc` files
- **Email**: `.eml` files

### File Storage
Files are stored in the `uploads/` directory with unique filenames:
```
uploads/{firebase_uid}_{timestamp}.{extension}
```

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid file type, missing parameters)
- `401`: Unauthorized (invalid or missing token)
- `404`: Not found
- `500`: Internal server error

## Development

### Project Structure
```
server/
├── main.py              # FastAPI application
├── database.py          # Database configuration
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── crud.py             # Database operations
├── firebase_auth.py    # Firebase authentication
├── requirements.txt     # Python dependencies
├── env.example         # Environment variables template
├── uploads/            # File storage directory
└── README.md           # This file
```

### Adding New Features

1. **New Models**: Add to `models.py`
2. **New Schemas**: Add to `schemas.py`
3. **New CRUD Operations**: Add to `crud.py`
4. **New Endpoints**: Add to `main.py`

## Security Considerations

- All file uploads are validated for type and size
- Firebase tokens are verified on every protected request
- Files are stored with unique names to prevent conflicts
- CORS is configured for frontend integration

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check PostgreSQL is running
   - Verify `DATABASE_URL` in `.env`
   - Ensure database exists

2. **Firebase Authentication Error**
   - Verify service account key path
   - Check Firebase project configuration
   - Ensure token is valid and not expired

3. **File Upload Error**
   - Check file type is supported
   - Verify `uploads/` directory exists
   - Check file permissions

### Logs
The application logs errors and requests. Check the console output for debugging information. 