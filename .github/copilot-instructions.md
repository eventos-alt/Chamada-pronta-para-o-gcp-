# Sistema de Controle de Presença - IOS

## Arquitetura do Projeto

Este é um sistema full-stack de controle de presença com backend FastAPI e frontend React:

- **Backend**: FastAPI + MongoDB (Motor driver assíncrono) + JWT auth
- **Frontend**: Create React App + shadcn/ui + Tailwind CSS + React Router
- **Banco**: MongoDB com collections: users, units, courses, students, classes, attendances

## Estrutura e Padrões

### Backend (`backend/server.py`)

- **Single-file architecture**: Todo o backend está em um arquivo de 1000+ linhas
- **Router pattern**: Usa `APIRouter` com prefixo `/api`, não FastAPI diretamente
- **Models pattern**: Pydantic models seguem convenção `Model` (DB) + `ModelCreate`/`ModelUpdate` (requests) + `ModelResponse` (responses)
- **Auth**: JWT bearer tokens, middleware de CORS habilitado
- **Database**: Motor AsyncIOMotorClient, collections acessadas via `db[collection_name]`

### Frontend (`frontend/src/App.js`)

- **Single-file app**: Toda a aplicação React está em `App.js` (2600+ linhas)
- **Authentication**: Context pattern com `AuthProvider` e `useAuth` hook
- **UI Components**: shadcn/ui components em `src/components/ui/`
- **Styling**: Tailwind + CSS variables para temas, configurado via `tailwind.config.js`
- **Icons**: Lucide React icons importados individualmente

### Convenções de Código

#### Backend Models

```python
# Pattern: Base model + Create/Update variants
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # ... campos completos

class UserCreate(BaseModel):
    # Apenas campos obrigatórios na criação

class UserResponse(BaseModel):
    # Campos seguros para retorno (sem senha)
```

#### Frontend Components

```javascript
// Pattern: Functional components com hooks
const ComponentName = () => {
  const { user } = useAuth();
  const { toast } = useToast();

  // Estado local e effects
  // Handlers de eventos
  // Return JSX
};
```

#### API Integration

```javascript
// Pattern: axios com base URL e token automático
const API = `${BACKEND_URL}/api`;
axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
```

## Workflows de Desenvolvimento

### Configuração do Ambiente (.env)

**Arquivo obrigatório**: `backend/.env`

```env
# MongoDB Atlas connection
MONGO_URL=mongodb+srv://user:pass@cluster0.vuho6l7.mongodb.net/ios_sistema?retryWrites=true&w=majority
DB_NAME=ios_sistema
JWT_SECRET=umsegredoforte123
PORT=8000
```

**Pattern de configuração no server.py**:

```python
from dotenv import load_dotenv
import os

# Carrega variáveis do .env
load_dotenv()

# Configuração MongoDB
mongo_url = os.environ['MONGO_URL']  # ou os.getenv('MONGO_URL')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT
JWT_SECRET = os.environ.get('JWT_SECRET', 'fallback-secret')

print(f"Conectado ao MongoDB: {db.name}")
```

**Frontend environment**: `frontend/.env`

```env
# Backend API URL
REACT_APP_BACKEND_URL=http://localhost:8000
```

**Usage no App.js**:

```javascript
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;
```

### Executar Localmente

```bash
# Backend
cd backend
pip install -r requirements.txt
# Criar arquivo .env com as variáveis acima
python server.py

# Frontend
cd frontend
npm install
# Configurar REACT_APP_BACKEND_URL=http://localhost:8000
npm start
```

### Testing

- **Backend**: `backend_test.py` - testes automatizados de todos endpoints
- **Frontend**: Sem testes implementados (usa react-scripts padrão)

### Build/Deploy

- **Backend**: FastAPI app em `server.py`, ready para Uvicorn
- **Frontend**: `npm run build` gera build otimizado
- **Config**: CRACO config desabilita hot reload opcionalmente

## Tipos de Usuário e Permissões

Sistema com 4 tipos de usuário:

- `admin`: Acesso total
- `instrutor`: Gerencia turmas/presenças
- `pedagogo`: Visualiza relatórios
- `monitor`: Auxilia em turmas

Autenticação via JWT, middleware verifica tokens em rotas protegidas.

### Sistema de Senhas

**Padrão de Criação de Senhas**:

- **Senha Temporária Automática**: Sistema gera senha temporária de 8 caracteres (`str(uuid.uuid4())[:8]`)
- **Hash bcrypt**: Todas as senhas são hasheadas com `bcrypt.hash()`
- **Primeiro Acesso**: Flag `primeiro_acesso: True` força alteração da senha temporária
- **Status Pendente**: Novos usuários criados com `status: "pendente"`

**Fluxos de Senha**:

```python
# Criação de usuário (admin only)
temp_password = str(uuid.uuid4())[:8]
hashed_password = bcrypt.hash(temp_password)
# TODO: Enviar senha por email (atualmente retorna na resposta)

# Reset de senha (admin)
/api/users/{user_id}/reset-password # Gera nova senha temporária

# Primeiro acesso
/api/auth/first-access # Usuário define senha permanente

# Alteração de senha
/api/auth/change-password # Usuário logado altera própria senha
```

## Pontos de Integração

### Database Schema

```python
# Collections principais:
users: {id, nome, email, tipo, unidade_id, ...}
units: {id, nome, endereco, responsavel, ...}
courses: {id, nome, carga_horaria, categoria, ...}
students: {id, nome, cpf, endereco, ...}
classes: {id, curso_id, unidade_id, instrutor_id, ...}
attendances: {id, turma_id, aluno_id, data, presente, ...}
```

### API Endpoints Pattern

```python
# Pattern: CRUD completo para cada entidade
@api_router.post("/entity") # Create
@api_router.get("/entity")  # List all
@api_router.put("/entity/{id}") # Update
@api_router.delete("/entity/{id}") # Delete
```

**Endpoints de Autenticação Críticos**:

```python
# Login (retorna JWT token)
@api_router.post("/auth/login")

# Primeiro acesso (usuário define senha permanente)
@api_router.post("/auth/first-access")

# Perfil do usuário logado
@api_router.get("/auth/me")

# Alterar senha (usuário logado)
@api_router.post("/auth/change-password")

# Admin: criar usuário com senha temporária
@api_router.post("/users")

# Admin: resetar senha de usuário
@api_router.post("/users/{user_id}/reset-password")

# Admin: aprovar usuário pendente (gera nova senha)
@api_router.put("/users/{user_id}/approve")
```

### Component Props Flow

- Dados carregados no componente pai via API
- Estado passado como props ou via Context
- Mutações via handlers que fazem requests e atualizam estado local

## Debugging e Logs

- **Backend**: Logging configurado, exceptions retornam HTTPException
- **Frontend**: Console.error para debugging, toast notifications para usuário
- **Network**: Axios interceptors não configurados (usar browser dev tools)

### Problemas Comuns e Soluções

#### "function already defined" no server.py

**Sintoma**: Python reporta função duplicada na linha X
**Causa**: Single-file architecture com 1000+ linhas pode ter duplicações acidentais
**Solução**:

```python
# Verificar duplicações de:
- app = FastAPI() # Deve ter apenas 1
- api_router = APIRouter() # Deve ter apenas 1
- @api_router.get("/ping") # Deve ter apenas 1
- JWT_SECRET = ... # Deve ter apenas 1
- CORS middleware # Deve ter apenas 1
```

#### Erro de conexão MongoDB

**Sintoma**: "Error ao conectar" na inicialização
**Causa**: Variáveis .env incorretas ou MongoDB Atlas não configurado
**Solução**:

```bash
# Verificar arquivo backend/.env existe
# Testar MONGO_URL no MongoDB Compass
# Verificar whitelist IP no Atlas (0.0.0.0/0 para dev)
```

#### CORS error no frontend

**Sintoma**: "Access-Control-Allow-Origin" error no browser
**Causa**: Frontend não está nas origins permitidas
**Solução**:

```python
# Adicionar URL do frontend em origins
origins = [
    "http://localhost:3000",  # React dev server
    "https://seu-frontend.vercel.app"  # Produção
]
```

## Deploy e Hospedagem

### Recomendação para Este Projeto

**Stack Recomendada para Produção**:

- **Database**: MongoDB Atlas (plano gratuito 512MB)
- **Backend**: Railway ou Render (FastAPI com Docker)
- **Frontend**: Vercel (build estático React)

### 1. Database (MongoDB Atlas)

```bash
# Setup obrigatório
1. Criar cluster no MongoDB Atlas
2. Configurar usuário/senha
3. Whitelist IPs (0.0.0.0/0 para desenvolvimento)
4. Obter MONGO_URL: mongodb+srv://user:pass@cluster.mongodb.net/dbname
```

### 2. Backend Deploy no Railway (Passo a Passo)

#### 🚀 **Setup Railway Completo**

**Pré-requisitos:**

1. Conta no GitHub (para conectar repositório)
2. MongoDB Atlas configurado (passo 1 acima)
3. Backend funcionando localmente

**Passo 1: Preparar o projeto**

```bash
# Criar Dockerfile no backend/
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "$PORT"]
```

**Passo 2: Ajustar server.py para Railway**

```python
# No server.py, usar PORT do Railway
import os
PORT = int(os.environ.get("PORT", 8000))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=PORT)
```

**Passo 3: Deploy no Railway**

1. Acesse [railway.app](https://railway.app) e faça login com GitHub
2. Clique "New Project" → "Deploy from GitHub repo"
3. Selecione seu repositório
4. Railway detecta Python e faz build automático
5. **URL pública será gerada**: `https://seu-projeto-production.up.railway.app`

**Passo 4: Configurar Variáveis de Ambiente**
No painel Railway, vá em "Variables" e adicione:

```env
MONGO_URL=mongodb+srv://jesielamarojunior_db_user:admin123@cluster0.vuho6l7.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority
DB_NAME=IOS-SISTEMA-CHAMADA
JWT_SECRET=seu-jwt-secret-super-forte-aqui
PORT=8000
```

**Passo 5: Testar API Online**

```bash
# Teste o endpoint ping
curl https://seu-projeto-production.up.railway.app/api/ping

# Deve retornar: {"message": "Backend funcionando!"}
```

#### 🔧 **Configurações Importantes Railway**

**CORS para produção:**

```python
# Adicionar URL do Railway nas origins
origins = [
    "http://localhost:3000",  # Desenvolvimento
    "https://seu-frontend.vercel.app",  # Frontend produção
    "https://seu-projeto-production.up.railway.app"  # Railway URL
]
```

**Auto-deploy:**

- Railway reconstrói automaticamente a cada push no GitHub
- Logs disponíveis em tempo real no painel
- Domínio customizado disponível no plano pago

### 3. Frontend Deploy (Vercel)

**Build configuração**:

```bash
# Build command
npm run build

# Environment variables
REACT_APP_BACKEND_URL=https://seu-backend.railway.app
```

**Configuração CORS no backend**:

```python
# Adicionar domínio do frontend em origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://seu-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Como os Dados São Salvos Online

#### 📊 **Fluxo Completo de Dados**

```
1. Frontend React (Vercel)
   ↓ POST /api/users (criar usuário)

2. Backend FastAPI (Railway)
   ↓ Recebe request, valida dados
   ↓ bcrypt.hash(senha)

3. MongoDB Atlas (Nuvem)
   ↓ Salva documento na collection "usuarios"

4. Retorna confirmação
   ↑ Backend → Frontend
```

**Exemplo prático - Registrar presença:**

```javascript
// Frontend envia
const response = await axios.post(`${API}/attendance`, {
  turma_id: "123",
  aluno_id: "456",
  presente: true,
  data: "2025-09-26",
});

// Backend processa e salva no MongoDB Atlas
await db.attendances.insert_one({
  id: str(uuid.uuid4()),
  turma_id: "123",
  aluno_id: "456",
  presente: true,
  data: datetime.now(),
  created_at: datetime.now(timezone.utc),
});
```

**✅ Resultado**: Dados ficam salvos permanentemente no MongoDB Atlas, acessíveis de qualquer lugar do mundo!

### 5. Fluxo de Deploy Completo

1. **Database**: MongoDB Atlas configurado ✅
2. **Backend**: Deploy no Railway com variáveis de ambiente ✅
3. **Frontend**: Deploy no Vercel apontando para Railway URL ✅
4. **CORS**: Configurar origins para permitir comunicação ✅
5. **Testes**: Verificar login, CRUD, presença funcionando ✅

### 5. Comandos de Deploy Essenciais

```bash
# Testar backend local com env de produção
cd backend
uvicorn server:app --reload --env-file .env

# Build e teste frontend
cd frontend
npm run build
npx serve -s build

# Deploy via Git (Railway/Render fazem auto-deploy)
git add .
git commit -m "Deploy: sistema de presença v1.0"
git push origin main
```
