# Render.com Configuration for Sistema IOS Backend

## Environment Variables Required:

MONGO_URL=mongodb+srv://jesielamarojunior_db_user:admin123@cluster0.vuho6l7.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority
DB_NAME=IOS-SISTEMA-CHAMADA
JWT_SECRET=umsegredoforte123456789
PORT=8000
RENDER=true

## CORS Configuration:

# The backend is configured to allow requests from:

# - https://sistema-ios-chamada.vercel.app (main production frontend)

# - http://localhost:3000 (development)

# - All origins (\*) when RENDER environment variable is set

## Build Command:

pip install -r requirements.txt

## Start Command:

python server.py

## Health Check Endpoint:

GET /api/ping

## Important Notes:

1. Make sure RENDER=true is set in environment variables
2. The CORS middleware will automatically allow all origins in production
3. JWT_SECRET should be a strong secret key
4. MongoDB connection string must be accessible from Render's servers

## Frontend URLs that need CORS access:

- https://sistema-ios-chamada.vercel.app
- Any other Vercel deployment URLs should be added to the origins list

## Deploy Steps:

1. Push code to GitHub
2. Connect Render to GitHub repository
3. Set environment variables in Render dashboard
4. Deploy using the above build/start commands
