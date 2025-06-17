# SSO Authentication System - Complete Setup Guide

This project consists of a React frontend with a Python Flask backend that supports Google and Microsoft SSO authentication.

## Project Structure

```
wfpuiexp/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── config.py
│   └── .env
└── frontend/
    ├── src/
    │   ├── components/
    │   │   └── Auth.jsx
    │   ├── App.jsx
    │   └── index.js
    ├── package.json
    └── public/
        └── index.html
```

## Backend Setup (Python Flask)

### 1. Create Backend Directory and Files

First, create the backend directory and navigate to it:

```bash
mkdir sso-auth-project
cd sso-auth-project
mkdir backend
cd backend
```

### 2. Install Python Dependencies

Create `requirements.txt`:

```
Flask==2.3.3
Flask-CORS==4.0.0
python-dotenv==1.0.0
requests==2.31.0
PyJWT==2.8.0
cryptography==41.0.4
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Create `.env` file:

```
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
MICROSOFT_CLIENT_ID=your_microsoft_client_id_here
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret_here
JWT_SECRET_KEY=your_super_secret_jwt_key_here
FLASK_SECRET_KEY=your_flask_secret_key_here
```

### 4. Run Backend

```bash
python app.py
```

The backend will run on `http://localhost:5000`

## Frontend Setup (React)

### 1. Create Frontend Directory

From the project root:

```bash
mkdir frontend
cd frontend
```

### 2. Initialize React App

```bash
npx create-react-app . --template minimal
```

### 3. Install Additional Dependencies

```bash
npm install axios react-router-dom
```

### 4. Run Frontend

```bash
npm start
```

The frontend will run on `http://localhost:3000`

## OAuth App Configuration

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Set authorized redirect URIs:
   - `http://localhost:5000/auth/google/callback`
6. Copy Client ID and Client Secret to backend `.env`

### Microsoft OAuth Setup

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" → "App registrations"
3. Click "New registration"
4. Set redirect URI: `http://localhost:5000/auth/microsoft/callback`
5. Go to "Certificates & secrets" → create new client secret
6. Copy Application (client) ID and client secret to backend `.env`

## API Endpoints

### Authentication Endpoints

- `GET /auth/google` - Initiate Google OAuth
- `GET /auth/google/callback` - Google OAuth callback
- `GET /auth/microsoft` - Initiate Microsoft OAuth
- `GET /auth/microsoft/callback` - Microsoft OAuth callback
- `POST /auth/verify` - Verify JWT token
- `POST /auth/logout` - Logout user

### Response Format

Successful authentication returns:

```json
{
  "success": true,
  "token": "jwt_token_here",
  "user": {
    "id": "user_id",
    "name": "User Name",
    "email": "user@example.com",
    "provider": "google|microsoft"
  }
}
```

## Running the Complete Application

1. **Start Backend** (Terminal 1):

```bash
cd backend
python app.py
```

2. **Start Frontend** (Terminal 2):

```bash
cd frontend
npm start
```

3. **Access Application**:
   - Frontend: `http://localhost:3000`
   - Backend API: `http://localhost:5000`

## Security Notes

- Store sensitive credentials in `.env` file (never commit to version control)
- Use HTTPS in production
- Implement proper CORS policies for production
- Add rate limiting and input validation
- Use secure JWT secret keys
- Implement token refresh mechanism for production use

## Production Deployment

### Backend (Python)

- Use WSGI server like Gunicorn
- Set up proper environment variables
- Configure HTTPS
- Use production database

### Frontend (React)

- Build optimized bundle: `npm run build`
- Serve static files through CDN or web server
- Update API endpoints to production URLs

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure Flask-CORS is properly configured
2. **OAuth Redirect Mismatch**: Verify redirect URIs in OAuth app settings
3. **Environment Variables**: Check `.env` file is loaded correctly
4. **Port Conflicts**: Ensure ports 3000 and 5000 are available

### Debug Mode

Enable debug mode in Flask for development:

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```
