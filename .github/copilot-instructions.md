# Sistema de Controle de Presença - IOS

## 🎯 Architecture Overview

This is a production attendance management system for educational institutions with role-based access control:

- **Stack**: FastAPI + MongoDB + React + shadcn/ui
- **Key Pattern**: Single-file architecture for both backend and frontend
- **Role System**: 4 user types (admin/instrutor/pedagogo/monitor) with granular permissions
- **Deploy**: Backend on Render, Frontend on Vercel (Live since 09/2025)
- **Scale**: 4800+ lines backend, 8000+ lines frontend

## 📁 Critical Architecture Patterns

### Backend (`backend/server.py`) - 4800+ lines

- **Monolith Pattern**: Entire API in single file with `api_router = APIRouter(prefix="/api")`
- **DB Pattern**: `db = AsyncIOMotorClient(MONGO_URL)[DB_NAME]` → `await db.collection_name.find_one()`
- **Auth Pattern**: JWT with `@Depends(get_current_user)` and role-based filtering
- **Model Convention**: `UserCreate` (input) → `User` (DB) → `UserResponse` (output)
- **CORS Fix**: Custom middleware required for production (Vercel ↔ Render)

### Frontend (`frontend/src/App.js`) - 8000+ lines

- **Monolith Pattern**: Complete SPA in single file with React Context
- **Auth Context**: `const { user } = useAuth()` provides current user + permissions
- **API Pattern**: `const API = \`\${BACKEND_URL}/api\`` with axios defaults
- **UI Stack**: shadcn/ui + Tailwind + Lucide icons (all imported individually)
- **State Pattern**: Local useState for forms, useEffect for data fetching

## ⚡ Essential Development Patterns

### Role-Based Data Access (CRITICAL)

```python
# Backend: Permission filtering baked into every query
if current_user.tipo == "instrutor":
    query["instrutor_id"] = current_user.id  # Only their classes
elif current_user.tipo == "pedagogo":
    query["tipo_turma"] = "extensao"        # Only extension classes
# Admin sees everything (no filters)
```

### Frontend Permission UX

```javascript
// Always check user type before showing features
{
  user?.tipo !== "admin" && (
    <div className="p-4 bg-orange-50">
      <Info className="h-4 w-4" />
      <span>
        Suas Permissões:{" "}
        {user?.tipo === "instrutor" ? "Apenas seu curso" : "Sua unidade"}
      </span>
    </div>
  );
}
```

### API Error Handling Pattern (CRITICAL)

```javascript
// Backend endpoints don't always exist - check first!
// ❌ BAD: axios.get(`${API}/attendance`) → 405 Method Not Allowed
// ✅ GOOD: axios.get(`${API}/reports/attendance`) → Works
```

## 🔧 Critical Developer Workflows

### Environment Setup (REQUIRED)

```bash
# Backend - MUST create backend/.env first
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/db
DB_NAME=ios_sistema
JWT_SECRET=your-secret-here

# Frontend - MUST set API URL
REACT_APP_BACKEND_URL=https://sistema-ios-backend.onrender.com
```

### Local Development

```powershell
# Backend (requires Python 3.11+)
cd backend; pip install -r requirements.txt; python server.py

# Frontend (requires Node 18+)
cd frontend; npm install; npm start
```

### Production URLs (LIVE SYSTEM)

- **Frontend**: https://sistema-ios-chamada.vercel.app
- **Backend**: https://sistema-ios-backend.onrender.com
- **Database**: MongoDB Atlas cluster

### Common Debug Commands

```powershell
# Test backend directly
curl https://sistema-ios-backend.onrender.com/api/ping

# Check user permissions (PowerShell)
$body = @{"email" = "admin@ios.com.br"; "senha" = "password"} | ConvertTo-Json
$token = (Invoke-WebRequest -Uri "$API/auth/login" -Method POST -Body $body -Headers @{"Content-Type" = "application/json"}).Content | ConvertFrom-Json
```

## 🏗️ Business Logic Essentials

### Role-Based Permissions (ENFORCED IN CODE)

```python
# 4 user types with strict scoping:
# - admin: sees everything
# - instrutor: sees only own course (curso_id must match)
# - pedagogo: sees only own unit (unidade_id must match) + extensao classes only
# - monitor: sees only assigned classes
```

### CSV Import Logic (BUSINESS CRITICAL)

```javascript
// CSV format: nome,cpf,data_nascimento,curso,turma,email,telefone
// Backend auto-validates user scope:
// - Instrutor: only accepts their curso_id from CSV
// - Auto-creates missing turmas for instructors
// - Returns detailed results: {successful, errors, duplicates, unauthorized}
```

### Database Schema (PRODUCTION)

```python
# Key collections:
users: {id, tipo, curso_id, unidade_id}  # curso_id required for non-admin
students: {id, nome, cpf, data_nascimento}  # CPF + data_nascimento required
classes: {id, curso_id, instrutor_id, alunos_ids[]}  # Array relationship
attendances: {id, turma_id, data, presencas{}}  # Date validation enforced
```

## 🔌 Integration Points

### Key API Endpoints (PRODUCTION)

```python
# Auth endpoints
POST /api/auth/login              # Returns JWT token
GET  /api/auth/me                 # Current user profile
POST /api/auth/first-access       # Set permanent password

# CRUD endpoints (all have role-based filtering)
GET  /api/students                # Filtered by user.curso_id automatically
GET  /api/classes                 # Filtered by user permissions
POST /api/students/import-csv     # CSV bulk upload with validation
GET  /api/reports/attendance      # NOT /api/attendance (405 error)

# File uploads
POST /api/upload/atestado         # Medical certificates (PDF/JPG/PNG)
POST /api/dropouts               # Student dropout registration
```

## 🚀 Production System Status

### Live URLs (October 2025)

- **Frontend**: https://sistema-ios-chamada.vercel.app
- **Backend**: https://sistema-ios-backend.onrender.com
- **Database**: MongoDB Atlas cluster

### Common Issues & Solutions

#### CORS Errors

- **Symptom**: "Access-Control-Allow-Origin" blocked
- **Solution**: Backend has custom CORS middleware - check `@app.middleware("http")` section

#### 405 Method Not Allowed

- **Symptom**: `axios.get('/api/attendance')` fails
- **Solution**: Use `/api/reports/attendance` instead - not all endpoints exist

#### React DOM Errors

- **Symptom**: "removeChild" errors after state updates
- **Solution**: Sequential state clearing with timeouts to prevent race conditions

#### Role-Based Data Missing

- **Symptom**: User sees no data despite correct login
- **Solution**: Check user.curso_id matches expected course - backend filters by this

### Development Tips

- Use single-file architecture patterns when extending
- Always validate user permissions before showing UI elements
- Backend filters are automatic - don't duplicate filtering in frontend
- Production environment variables are critical for CORS
- CSV imports respect user scoping automatically
