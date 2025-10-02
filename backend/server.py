from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Query
from fastapi.responses import Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta, date
import jwt
from passlib.hash import bcrypt
import base64
import csv
import io
from collections import defaultdict
import asyncio
from urllib.parse import quote_plus

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

load_dotenv()

# -------------------------
# Criação do FastAPI app
# -------------------------
app = FastAPI(title="Sistema de Controle de Presença - IOS")

# Middleware CORS - configurado para desenvolvimento e produção
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://sistema-ios-chamada.vercel.app",  # 🎯 URL específica do Vercel
    "https://front-end-sistema-qbl0lhxig-jesielamarojunior-makers-projects.vercel.app",
    "https://front-end-sistema.vercel.app",
    "https://sistema-ios-frontend.vercel.app",
    "https://sistema-ios-backend.onrender.com",  # 🚀 URL do próprio backend Render
    "*"  # 🚨 EMERGENCY: Permitir todas as origens para resolver CORS
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 🚀 Middleware personalizado CORS - EMERGENCY FIX
@app.middleware("http")
async def cors_handler(request, call_next):
    """Middleware personalizado para resolver problemas CORS em produção"""
    
    # Headers CORS básicos
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "accept, accept-encoding, authorization, content-type, dnt, origin, user-agent, x-csrftoken, x-requested-with",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Max-Age": "86400"
    }
    
    # Resposta direta para OPTIONS
    if request.method == "OPTIONS":
        response = Response(status_code=200)
        for key, value in cors_headers.items():
            response.headers[key] = value
        return response
    
    try:
        # Processar requisição normal
        response = await call_next(request)
        
        # Adicionar headers CORS na resposta
        for key, value in cors_headers.items():
            response.headers[key] = value
            
        return response
        
    except Exception as e:
        # Em caso de erro, ainda retornar headers CORS
        print(f"❌ Erro no middleware CORS: {e}")
        response = Response(status_code=500, content=f"Internal Server Error: {str(e)}")
        for key, value in cors_headers.items():
            response.headers[key] = value
        return response

# Log da configuração CORS para debug
print(f"🔧 CORS configurado para origins: {origins}")
print(f"🌍 Ambiente: RENDER={os.environ.get('RENDER')}, RAILWAY={os.environ.get('RAILWAY_ENVIRONMENT')}")

# -------------------------
# MongoDB connection
# -------------------------
username = quote_plus("jesielamarojunior_db_user")
password = quote_plus("admin123")

MONGO_URL = f"mongodb+srv://{username}:{password}@cluster0.vuho6l7.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority"
DB_NAME = "IOS-SISTEMA-CHAMADA"

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# -------------------------
# Teste de conexão MongoDB
# -------------------------
async def test_connection():
    try:
        await client.admin.command('ping')
        print("Conectado ao MongoDB Atlas ✅")
    except Exception as e:
        print("Erro ao conectar:", e)

# -------------------------
# Evento de startup
# -------------------------
@app.on_event("startup")
async def startup_event():
    await test_connection()
    await initialize_system()

# -------------------------
# Router e rota de teste
# -------------------------
api_router = APIRouter(prefix="/api")

@api_router.get("/ping")
async def ping():
    return {
        "message": "Backend funcionando!",
        "cors_origins": origins,
        "render_env": os.environ.get("RENDER"),
        "railway_env": os.environ.get("RAILWAY_ENVIRONMENT"),
        "timestamp": datetime.now().isoformat()
    }

@api_router.get("/cors-test")
async def cors_test():
    """Endpoint específico para testar CORS"""
    return {
        "status": "CORS working",
        "message": "Se você consegue ver esta mensagem, o CORS está funcionando!",
        "frontend_allowed": "https://sistema-ios-chamada.vercel.app",
        "all_origins": origins,
        "timestamp": datetime.now().isoformat()
    }

# -------------------------
# Configuração JWT
# -------------------------
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
security = HTTPBearer()

# Inclui o router no app (já criados acima)
app.include_router(api_router)

# Enhanced Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome: str
    email: EmailStr
    senha: str
    tipo: str  # "admin", "instrutor", "pedagogo", "monitor"
    ativo: bool = True
    status: str = "ativo"  # "ativo", "pendente", "inativo"
    primeiro_acesso: bool = True
    token_confirmacao: Optional[str] = None
    unidade_id: Optional[str] = None  # Para instrutores/pedagogos/monitores
    curso_id: Optional[str] = None  # Para instrutores/pedagogos/monitores - curso específico
    telefone: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None

class UserCreate(BaseModel):
    nome: str
    email: EmailStr
    tipo: str
    unidade_id: Optional[str] = None
    curso_id: Optional[str] = None  # Obrigatório para instrutores/pedagogos/monitores
    telefone: Optional[str] = None

class UserUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    ativo: Optional[bool] = None
    unidade_id: Optional[str] = None
    curso_id: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    senha: str

class UserResponse(BaseModel):
    id: str
    nome: str
    email: str
    tipo: str
    ativo: bool
    status: str
    primeiro_acesso: bool
    unidade_id: Optional[str] = None
    curso_id: Optional[str] = None
    telefone: Optional[str] = None
    last_login: Optional[datetime] = None

class PasswordReset(BaseModel):
    senha_atual: str
    nova_senha: str

class Unidade(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome: str
    endereco: str
    telefone: Optional[str] = None
    responsavel: Optional[str] = None
    email: Optional[str] = None
    ativo: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UnidadeCreate(BaseModel):
    nome: str
    endereco: str
    telefone: Optional[str] = None
    responsavel: Optional[str] = None
    email: Optional[str] = None

class UnidadeUpdate(BaseModel):
    nome: Optional[str] = None
    endereco: Optional[str] = None
    telefone: Optional[str] = None
    responsavel: Optional[str] = None
    email: Optional[str] = None

class Curso(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome: str
    descricao: Optional[str] = None
    carga_horaria: int
    categoria: Optional[str] = None
    pre_requisitos: Optional[str] = None
    dias_aula: List[str] = ["segunda", "terca", "quarta", "quinta"]  # 📅 Dias de aula padrão
    ativo: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CursoCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    carga_horaria: int
    categoria: Optional[str] = None
    pre_requisitos: Optional[str] = None
    dias_aula: List[str] = ["segunda", "terca", "quarta", "quinta"]  # 📅 Dias de aula

class CursoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    carga_horaria: Optional[int] = None
    categoria: Optional[str] = None
    pre_requisitos: Optional[str] = None
    dias_aula: Optional[List[str]] = None  # 📅 Dias de aula

class Aluno(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome: str  # OBRIGATÓRIO - Nome completo
    cpf: str   # OBRIGATÓRIO - CPF válido
    data_nascimento: Optional[date] = None  # OPCIONAL para compatibilidade com dados existentes
    rg: Optional[str] = None
    genero: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    endereco: Optional[str] = None
    nome_responsavel: Optional[str] = None
    telefone_responsavel: Optional[str] = None
    observacoes: Optional[str] = None
    ativo: bool = True
    status: str = "ativo"  # "ativo", "desistente", "concluido", "suspenso"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AlunoCreate(BaseModel):
    nome: str  # OBRIGATÓRIO - Nome completo
    cpf: str   # OBRIGATÓRIO - CPF válido
    data_nascimento: date  # OBRIGATÓRIO - Data de nascimento
    rg: Optional[str] = None
    genero: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    endereco: Optional[str] = None
    nome_responsavel: Optional[str] = None
    telefone_responsavel: Optional[str] = None
    observacoes: Optional[str] = None

class AlunoUpdate(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    endereco: Optional[str] = None
    nome_responsavel: Optional[str] = None
    telefone_responsavel: Optional[str] = None
    observacoes: Optional[str] = None
    status: Optional[str] = None

class Turma(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome: str
    unidade_id: str
    curso_id: str
    instrutor_id: str
    pedagogo_id: Optional[str] = None
    monitor_id: Optional[str] = None
    alunos_ids: List[str] = []
    data_inicio: date
    data_fim: date
    horario_inicio: str  # "08:00"
    horario_fim: str     # "17:00"
    dias_semana: List[str] = []  # ["segunda", "terca", "quarta", "quinta", "sexta"]
    vagas_total: int = 30
    vagas_ocupadas: int = 0
    ciclo: Optional[str] = None  # "01/2025", "02/2025" - Opcional para compatibilidade
    ativo: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TurmaCreate(BaseModel):
    nome: str
    unidade_id: str
    curso_id: str
    instrutor_id: str
    pedagogo_id: Optional[str] = None
    monitor_id: Optional[str] = None
    data_inicio: date
    data_fim: date
    horario_inicio: str
    horario_fim: str
    dias_semana: List[str]
    vagas_total: int = 30
    ciclo: Optional[str] = None

class TurmaUpdate(BaseModel):
    nome: Optional[str] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    horario_inicio: Optional[str] = None
    horario_fim: Optional[str] = None
    dias_semana: Optional[List[str]] = None
    vagas_total: Optional[int] = None

class Chamada(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    turma_id: str
    instrutor_id: str
    data: date
    horario: str
    observacoes_aula: Optional[str] = None
    presencas: Dict[str, Dict[str, Any]]  # aluno_id -> {presente: bool, justificativa: str, atestado_id: str}
    total_presentes: int = 0
    total_faltas: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChamadaCreate(BaseModel):
    turma_id: str
    data: date
    horario: str
    observacoes_aula: Optional[str] = None
    presencas: Dict[str, Dict[str, Any]]

class Desistente(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    aluno_id: str
    turma_id: Optional[str] = None  # Tornar opcional para permitir desistência sem turma específica
    data_desistencia: date
    motivo: str
    observacoes: Optional[str] = None
    registrado_por: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DesistenteCreate(BaseModel):
    aluno_id: str
    turma_id: Optional[str] = None  # Tornar opcional para permitir desistência sem turma específica
    data_desistencia: date
    motivo: str
    observacoes: Optional[str] = None

# Helper Functions
def prepare_for_mongo(data):
    """Convert date objects to ISO strings for MongoDB storage"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, date):
                data[key] = value.isoformat()
            elif isinstance(value, datetime):
                data[key] = value.isoformat()
    return data

def parse_from_mongo(item):
    """Parse ISO strings back to date objects from MongoDB"""
    if isinstance(item, dict):
        # Remove MongoDB ObjectId field if present
        if '_id' in item:
            del item['_id']
            
        for key, value in item.items():
            if isinstance(value, str) and key in ['data_inicio', 'data_fim', 'data', 'data_nascimento', 'data_desistencia']:
                try:
                    item[key] = datetime.fromisoformat(value).date()
                except (ValueError, AttributeError):
                    pass
    return item

# JWT Token Functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_email: str = payload.get("sub")
        if user_email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        user = await db.usuarios.find_one({"email": user_email})
        if user is None:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")
        
        return UserResponse(**user)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

def check_admin_permission(current_user: UserResponse):
    if current_user.tipo != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem realizar esta ação")

# AUTH ROUTES
@api_router.post("/auth/login")
async def login(user_login: UserLogin):
    user = await db.usuarios.find_one({"email": user_login.email})
    if not user or not bcrypt.verify(user_login.senha, user["senha"]):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    
    if not user["ativo"]:
        raise HTTPException(status_code=401, detail="Usuário inativo")
    
    if user.get("status") == "pendente":
        raise HTTPException(status_code=401, detail="Usuário aguardando aprovação do administrador")
    
    # Update last login
    await db.usuarios.update_one(
        {"id": user["id"]},
        {"$set": {"last_login": datetime.now(timezone.utc)}}
    )
    
    access_token = create_access_token(data={"sub": user["email"], "tipo": user["tipo"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(**user)
    }

@api_router.post("/auth/first-access")
async def first_access_request(user_data: dict):
    # Check if user already exists
    existing_user = await db.usuarios.find_one({"email": user_data["email"]})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Generate temporary password
    temp_password = str(uuid.uuid4())[:8]
    hashed_password = bcrypt.hash(temp_password)
    
    user_obj = User(
        nome=user_data["nome"],
        email=user_data["email"],
        senha=hashed_password,
        tipo=user_data["tipo"],
        status="pendente",
        primeiro_acesso=True
    )
    
    await db.usuarios.insert_one(user_obj.dict())
    
    return {"message": "Solicitação de acesso enviada com sucesso", "temp_password": temp_password}

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user

@api_router.post("/auth/change-password")
async def change_password(password_reset: PasswordReset, current_user: UserResponse = Depends(get_current_user)):
    user = await db.usuarios.find_one({"id": current_user.id})
    if not bcrypt.verify(password_reset.senha_atual, user["senha"]):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")
    
    hashed_password = bcrypt.hash(password_reset.nova_senha)
    await db.usuarios.update_one(
        {"id": current_user.id},
        {"$set": {"senha": hashed_password, "primeiro_acesso": False}}
    )
    
    return {"message": "Senha alterada com sucesso"}

# USER MANAGEMENT ROUTES
@api_router.post("/users", response_model=UserResponse)
async def create_user(user_create: UserCreate, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    # Check if user already exists
    existing_user = await db.usuarios.find_one({"email": user_create.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Validação específica para instrutores, pedagogos e monitores
    if user_create.tipo in ["instrutor", "pedagogo", "monitor"]:
        if not user_create.unidade_id:
            raise HTTPException(status_code=400, detail="Unidade é obrigatória para instrutores, pedagogos e monitores")
        
        if not user_create.curso_id:
            raise HTTPException(status_code=400, detail="Curso é obrigatório para instrutores, pedagogos e monitores")
        
        # Verificar se unidade existe
        unidade = await db.unidades.find_one({"id": user_create.unidade_id})
        if not unidade:
            raise HTTPException(status_code=400, detail="Unidade não encontrada")
        
        # Verificar se curso existe
        curso = await db.cursos.find_one({"id": user_create.curso_id})
        if not curso:
            raise HTTPException(status_code=400, detail="Curso não encontrado")
    
    # Generate temporary password and confirmation token
    temp_password = str(uuid.uuid4())[:8]
    hashed_password = bcrypt.hash(temp_password)
    confirmation_token = str(uuid.uuid4())
    
    user_dict = user_create.dict()
    user_dict.update({
        "senha": hashed_password,
        "status": "pendente",
        "primeiro_acesso": True,
        "token_confirmacao": confirmation_token
    })
    
    user_obj = User(**user_dict)
    await db.usuarios.insert_one(user_obj.dict())
    
    # Log da criação para auditoria (removido temporariamente - função não implementada)
    # TODO: Implement log_admin_action function for audit trail
    print(f"👤 Admin {current_user.email} criou usuário {user_create.tipo}: {user_create.nome} ({user_create.email})")
    
    response = UserResponse(**user_obj.dict())
    return response

@api_router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0, 
    limit: int = 100,
    tipo: Optional[str] = None,
    status: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    # Admin can see all users, others can see basic user info
    if current_user.tipo != "admin" and current_user.tipo not in ["instrutor", "pedagogo"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    query = {}
    if tipo:
        query["tipo"] = tipo
    if status:
        query["status"] = status
        
    users = await db.usuarios.find(query).skip(skip).limit(limit).to_list(limit)
    return [UserResponse(**user) for user in users]

@api_router.get("/users/pending", response_model=List[UserResponse])
async def get_pending_users(current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    users = await db.usuarios.find({"status": "pendente"}).to_list(100)
    return [UserResponse(**user) for user in users]

@api_router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_update: UserUpdate, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado para atualizar")
    
    result = await db.usuarios.update_one({"id": user_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    updated_user = await db.usuarios.find_one({"id": user_id})
    return UserResponse(**updated_user)

@api_router.post("/auth/reset-password-request")
async def reset_password_request(email_data: dict):
    """
    Reset de senha para usuário comum
    🔐 SEGURANÇA: Não expõe se email existe ou não
    📧 TODO: Implementar envio por email
    """
    email = email_data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email é obrigatório")
    
    # Check if user exists
    user = await db.usuarios.find_one({"email": email})
    
    if user:
        # Generate new temporary password
        temp_password = str(uuid.uuid4())[:8]
        hashed_password = bcrypt.hash(temp_password)
        
        # Update user password
        await db.usuarios.update_one(
            {"email": email},
            {"$set": {"senha": hashed_password, "primeiro_acesso": True}}
        )
        
        # TODO: Enviar por email
        # send_password_email(email, temp_password)
        print(f"🔐 SENHA TEMPORÁRIA PARA {email}: {temp_password}")
    
    # ✅ SEGURANÇA: Sempre retorna sucesso (não expõe se email existe)
    return {"message": "Se o email estiver cadastrado, uma nova senha será enviada"}

@api_router.post("/users/{user_id}/reset-password")
async def admin_reset_user_password(user_id: str, current_user: UserResponse = Depends(get_current_user)):
    """
    Reset de senha administrativo
    👨‍💼 ADMIN: Pode resetar senha de qualquer usuário
    🔐 SEGURANÇA: Retorna senha para admin informar pessoalmente
    """
    check_admin_permission(current_user)
    
    # Buscar dados do usuário
    user = await db.usuarios.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Generate new temporary password
    temp_password = str(uuid.uuid4())[:8]
    hashed_password = bcrypt.hash(temp_password)
    
    # Update user password
    result = await db.usuarios.update_one(
        {"id": user_id},
        {"$set": {"senha": hashed_password, "primeiro_acesso": True}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Erro ao atualizar senha")
    
    # Log da ação administrativa
    print(f"🔐 ADMIN {current_user.email} resetou senha de {user['email']}: {temp_password}")
    
    return {
        "message": "Senha resetada com sucesso", 
        "temp_password": temp_password,
        "user_email": user["email"],
        "user_name": user["nome"]
    }

@api_router.put("/users/{user_id}/approve")
async def approve_user(user_id: str, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    # Generate a new temporary password for the approved user
    temp_password = str(uuid.uuid4())[:8]
    hashed_password = bcrypt.hash(temp_password)
    
    result = await db.usuarios.update_one(
        {"id": user_id}, 
        {"$set": {"status": "ativo", "senha": hashed_password}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return {"message": "Usuário aprovado com sucesso", "temp_password": temp_password}

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    result = await db.usuarios.update_one({"id": user_id}, {"$set": {"ativo": False}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return {"message": "Usuário desativado com sucesso"}

# UNIDADES ROUTES
@api_router.post("/units", response_model=Unidade)
async def create_unidade(unidade_create: UnidadeCreate, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    unidade_obj = Unidade(**unidade_create.dict())
    await db.unidades.insert_one(unidade_obj.dict())
    return unidade_obj

@api_router.get("/units", response_model=List[Unidade])
async def get_unidades(current_user: UserResponse = Depends(get_current_user)):
    unidades = await db.unidades.find({"ativo": True}).to_list(1000)
    return [Unidade(**unidade) for unidade in unidades]

@api_router.put("/units/{unidade_id}", response_model=Unidade)
async def update_unidade(unidade_id: str, unidade_update: UnidadeUpdate, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    update_data = {k: v for k, v in unidade_update.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado para atualizar")
    
    result = await db.unidades.update_one({"id": unidade_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Unidade não encontrada")
    
    updated_unidade = await db.unidades.find_one({"id": unidade_id})
    return Unidade(**updated_unidade)

@api_router.delete("/units/{unidade_id}")
async def delete_unidade(unidade_id: str, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    result = await db.unidades.update_one({"id": unidade_id}, {"$set": {"ativo": False}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Unidade não encontrada")
    
    return {"message": "Unidade desativada com sucesso"}

# CURSOS ROUTES
@api_router.post("/courses", response_model=Curso)
async def create_curso(curso_create: CursoCreate, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    curso_obj = Curso(**curso_create.dict())
    await db.cursos.insert_one(curso_obj.dict())
    return curso_obj

@api_router.get("/courses", response_model=List[Curso])
async def get_cursos(current_user: UserResponse = Depends(get_current_user)):
    cursos = await db.cursos.find({"ativo": True}).to_list(1000)
    return [Curso(**curso) for curso in cursos]

@api_router.get("/users/{user_id}/details")
async def get_user_details(user_id: str, current_user: UserResponse = Depends(get_current_user)):
    # Admin pode ver detalhes de qualquer usuário
    if current_user.tipo != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    user = await db.usuarios.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    user_response = UserResponse(**user)
    details = {"user": user_response}
    
    # Buscar informações da unidade
    if user.get("unidade_id"):
        unidade = await db.unidades.find_one({"id": user["unidade_id"]})
        details["unidade"] = unidade
    
    # Buscar informações do curso
    if user.get("curso_id"):
        curso = await db.cursos.find_one({"id": user["curso_id"]})
        details["curso"] = curso
    
    return details

@api_router.put("/courses/{curso_id}", response_model=Curso)
async def update_curso(curso_id: str, curso_update: CursoUpdate, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    update_data = {k: v for k, v in curso_update.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado para atualizar")
    
    result = await db.cursos.update_one({"id": curso_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    
    updated_curso = await db.cursos.find_one({"id": curso_id})
    return Curso(**updated_curso)

@api_router.delete("/courses/{curso_id}")
async def delete_curso(curso_id: str, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    result = await db.cursos.update_one({"id": curso_id}, {"$set": {"ativo": False}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Curso não encontrado")
    
    return {"message": "Curso desativado com sucesso"}

# ALUNOS ROUTES
@api_router.post("/students", response_model=Aluno)
async def create_aluno(aluno_create: AlunoCreate, current_user: UserResponse = Depends(get_current_user)):
    """📖 CADASTRO DE ALUNO - LÓGICA REFINADA 29/09/2025
    
    👨‍🏫 Instrutor: Cadastra apenas no seu curso
    📊 Pedagogo: Cadastra em qualquer curso da sua unidade  
    👩‍💻 Monitor: NÃO pode cadastrar alunos
    👑 Admin: Cadastra em qualquer lugar
    """
    
    # 🔒 MONITOR: Não pode cadastrar alunos
    if current_user.tipo == "monitor":
        raise HTTPException(
            status_code=403, 
            detail="Monitores não podem cadastrar alunos. Apenas visualizar."
        )
    
    # 👑 ADMIN: Pode cadastrar qualquer aluno
    if current_user.tipo == "admin":
        print(f"👑 Admin {current_user.email} cadastrando aluno: {aluno_create.nome}")
        
    # 👨‍🏫 INSTRUTOR: Apenas no seu curso específico
    elif current_user.tipo == "instrutor":
        if not current_user.curso_id or not current_user.unidade_id:
            raise HTTPException(
                status_code=403, 
                detail="Instrutor deve ter curso e unidade atribuídos"
            )
        
        # Aluno será automaticamente vinculado ao curso do instrutor
        print(f"👨‍🏫 Instrutor {current_user.email} cadastrando aluno no curso {current_user.curso_id}")
        
    # 📊 PEDAGOGO: Qualquer curso da sua unidade
    elif current_user.tipo == "pedagogo":
        if not current_user.unidade_id:
            raise HTTPException(
                status_code=403, 
                detail="Pedagogo deve ter unidade atribuída"
            )
        
        # Pedagogo pode escolher curso da unidade dele (validado no frontend)
        print(f"📊 Pedagogo {current_user.email} cadastrando aluno na unidade {current_user.unidade_id}")
        
    else:
        raise HTTPException(status_code=403, detail="Tipo de usuário não autorizado para cadastrar alunos")
    
    # ✅ VALIDAÇÃO: CPF único no sistema
    existing_aluno = await db.alunos.find_one({"cpf": aluno_create.cpf})
    if existing_aluno:
        raise HTTPException(status_code=400, detail="CPF já cadastrado no sistema")
    
    # ✅ VALIDAÇÃO: Nome completo obrigatório (não aceita "Aluno 1", "Aluno 2")
    if len(aluno_create.nome.strip()) < 3 or aluno_create.nome.strip().lower().startswith("aluno"):
        raise HTTPException(
            status_code=400, 
            detail="Nome completo é obrigatório. Não é permitido 'Aluno 1', 'Aluno 2', etc."
        )
    
    aluno_dict = prepare_for_mongo(aluno_create.dict())
    aluno_obj = Aluno(**aluno_dict)
    
    # ✅ REGISTRAR QUEM CRIOU O ALUNO
    mongo_data = prepare_for_mongo(aluno_obj.dict())
    mongo_data["created_by"] = current_user.id  # ID do usuário que criou
    mongo_data["created_by_name"] = current_user.nome  # Nome do usuário que criou
    mongo_data["created_by_type"] = current_user.tipo  # Tipo do usuário que criou
    
    print(f"🔍 Criando aluno '{aluno_create.nome}' por {current_user.nome} (ID: {current_user.id})")
    print(f"   created_by: {mongo_data['created_by']}")
    print(f"   created_by_name: {mongo_data['created_by_name']}")
    
    await db.alunos.insert_one(mongo_data)
    
    return aluno_obj

@api_router.get("/students", response_model=List[Aluno])
async def get_alunos(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """🎯 LISTAGEM DE ALUNOS: Filtrada por permissões do usuário"""
    
    print(f"🔍 Buscando alunos para usuário: {current_user.email} (tipo: {current_user.tipo})")
    print(f"   Curso ID: {current_user.curso_id}")
    print(f"   Unidade ID: {current_user.unidade_id}")
    
    # 👁️ FILTROS POR TIPO DE USUÁRIO - LÓGICA DETALHADA 29/09/2025
    if current_user.tipo == "admin":
        # 👑 Admin: vê TODOS os alunos (inclusive inativos para debug)
        print("👑 Admin visualizando todos os alunos (ativos e inativos)")
        query = {}
        if status:
            query["status"] = status
    elif current_user.tipo == "instrutor":
        # 👨‍🏫 INSTRUTOR: VÊ APENAS ALUNOS DAS TURMAS QUE ELE LECIONA
        # NOVA LÓGICA: Similar ao pedagogo, mas filtrado por curso específico do instrutor
        
        if not current_user.curso_id or not current_user.unidade_id:
            print("❌ Instrutor sem curso ou unidade definida")
            return []
            
        # Buscar todas as turmas do curso específico do instrutor na sua unidade
        turmas_instrutor = await db.turmas.find({
            "curso_id": current_user.curso_id,
            "unidade_id": current_user.unidade_id,
            "instrutor_id": current_user.id,  # Apenas turmas que ele leciona
            "ativo": True
        }).to_list(1000)
        
        print(f"🔍 Instrutor {current_user.email} leciona {len(turmas_instrutor)} turmas")
        
        # Coletar IDs de todos os alunos das turmas do instrutor
        aluno_ids = set()
        for turma in turmas_instrutor:
            turma_alunos = turma.get("alunos_ids", [])
            aluno_ids.update(turma_alunos)
            print(f"   Turma '{turma['nome']}': {len(turma_alunos)} alunos")
        
        if aluno_ids:
            query = {"id": {"$in": list(aluno_ids)}, "ativo": True}
            print(f"👨‍🏫 Instrutor vendo {len(aluno_ids)} alunos das suas turmas")
        else:
            print("👨‍🏫 Instrutor: nenhum aluno nas turmas lecionadas")
            return []
            
    elif current_user.tipo == "pedagogo":
        # 📊 Pedagogo: vê todos os cursos da unidade
        if not current_user.unidade_id:
            print("❌ Pedagogo sem unidade definida")
            return []
            
        # Buscar todas as turmas da unidade
        turmas_unidade = await db.turmas.find({
            "unidade_id": current_user.unidade_id,
            "ativo": True
        }).to_list(1000)
        
        # Coletar IDs de todos os alunos da unidade
        aluno_ids = set()
        for turma in turmas_unidade:
            aluno_ids.update(turma.get("alunos_ids", []))
        
        if aluno_ids:
            query = {"id": {"$in": list(aluno_ids)}, "ativo": True}
            print(f"📊 Pedagogo vendo {len(aluno_ids)} alunos da unidade {current_user.unidade_id}")
        else:
            print("📊 Pedagogo: nenhum aluno nas turmas da unidade")
            return []
            
    elif current_user.tipo == "monitor":
        # 👩‍💻 MONITOR: VÊ TODOS OS ALUNOS DA UNIDADE (igual ao pedagogo)
        if not current_user.unidade_id:
            print("❌ Monitor sem unidade definida")
            return []
            
        # Buscar todas as turmas da unidade (igual lógica do pedagogo)
        turmas_unidade = await db.turmas.find({
            "unidade_id": current_user.unidade_id,
            "ativo": True
        }).to_list(1000)
        
        print(f"🔍 Monitor {current_user.email} da unidade {current_user.unidade_id}")
        print(f"   Turmas na unidade: {len(turmas_unidade)}")
        
        # Coletar IDs de todos os alunos da unidade
        aluno_ids = set()
        for turma in turmas_unidade:
            turma_alunos = turma.get("alunos_ids", [])
            aluno_ids.update(turma_alunos)
            nome_turma = turma.get("nome", "N/A")
            print(f"   Turma '{nome_turma}': {len(turma_alunos)} alunos")
        
        if aluno_ids:
            query = {"id": {"$in": list(aluno_ids)}, "ativo": True}
            print(f"👩‍💻 Monitor vendo {len(aluno_ids)} alunos da unidade")
        else:
            print("👩‍💻 Monitor: nenhum aluno nas turmas da unidade")
            return []
    else:
        # Outros tipos de usuário não podem ver alunos
        print(f"❌ Tipo de usuário {current_user.tipo} não autorizado")
        return []
        
    print(f"🔍 Query final para alunos: {query}")
    alunos = await db.alunos.find(query).skip(skip).limit(limit).to_list(limit)
    print(f"📊 Total de alunos encontrados: {len(alunos)}")
    
    # ✅ CORREÇÃO 422: Tratamento seguro de dados de alunos
    result_alunos = []
    for aluno in alunos:
        try:
            parsed_aluno = parse_from_mongo(aluno)
            # Garantir campos obrigatórios para compatibilidade
            if 'data_nascimento' not in parsed_aluno or parsed_aluno['data_nascimento'] is None:
                parsed_aluno['data_nascimento'] = None  # Garantir campo existe
            
            aluno_obj = Aluno(**parsed_aluno)
            result_alunos.append(aluno_obj)
        except Exception as e:
            # Log do erro mas não quebra a listagem
            print(f"⚠️ Erro ao processar aluno {aluno.get('id', 'SEM_ID')}: {e}")
            continue
    
    return result_alunos

@api_router.put("/students/{aluno_id}", response_model=Aluno)
async def update_aluno(aluno_id: str, aluno_update: AlunoUpdate, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    update_data = {k: v for k, v in aluno_update.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado para atualizar")
    
    result = await db.alunos.update_one({"id": aluno_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    updated_aluno = await db.alunos.find_one({"id": aluno_id})
    return Aluno(**parse_from_mongo(updated_aluno))

@api_router.post("/students/cleanup-orphans")
async def cleanup_orphan_students(current_user: UserResponse = Depends(get_current_user)):
    """🧹 LIMPEZA DE ALUNOS ÓRFÃOS - Remove alunos não vinculados a turmas
    
    🚨 APENAS ADMIN pode executar esta operação
    Remove alunos que não estão em nenhuma turma ativa
    """
    check_admin_permission(current_user)
    
    print(f"🧹 Iniciando limpeza de alunos órfãos por {current_user.email}")
    
    # Buscar todas as turmas ativas
    turmas_ativas = await db.turmas.find({"ativo": True}).to_list(10000)
    
    # Coletar todos os IDs de alunos que estão em turmas
    alunos_em_turmas = set()
    for turma in turmas_ativas:
        alunos_em_turmas.update(turma.get("alunos_ids", []))
    
    print(f"📊 {len(alunos_em_turmas)} alunos estão vinculados a turmas ativas")
    
    # Buscar alunos órfãos (não estão em alunos_em_turmas)
    query_orfaos = {
        "ativo": True,
        "id": {"$nin": list(alunos_em_turmas)}
    }
    
    alunos_orfaos = await db.alunos.find(query_orfaos).to_list(10000)
    print(f"🚨 {len(alunos_orfaos)} alunos órfãos encontrados")
    
    if not alunos_orfaos:
        return {
            "message": "Nenhum aluno órfão encontrado",
            "orphans_found": 0,
            "orphans_removed": 0
        }
    
    # Log dos alunos que serão removidos
    orphan_names = [aluno.get("nome", "SEM_NOME") for aluno in alunos_orfaos]
    print(f"📝 Alunos órfãos: {', '.join(orphan_names[:10])}{'...' if len(orphan_names) > 10 else ''}")
    
    # Marcar alunos órfãos como inativos (soft delete)
    orphan_ids = [aluno["id"] for aluno in alunos_orfaos]
    result = await db.alunos.update_many(
        {"id": {"$in": orphan_ids}},
        {"$set": {"ativo": False, "removed_reason": "orphan_cleanup", "removed_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    print(f"✅ {result.modified_count} alunos órfãos marcados como inativos")
    
    return {
        "message": f"Limpeza concluída: {result.modified_count} alunos órfãos removidos",
        "orphans_found": len(alunos_orfaos),
        "orphans_removed": result.modified_count,
        "orphan_names": orphan_names[:20]  # Máximo 20 nomes no retorno
    }

@api_router.post("/students/fix-created-by")
async def fix_alunos_created_by(current_user: UserResponse = Depends(get_current_user)):
    """🔧 MIGRAÇÃO: Corrigir alunos sem created_by associando aos instrutores das turmas
    
    Este endpoint resolve o problema de alunos antigos que não aparecem para instrutores
    porque foram criados antes da implementação do campo created_by.
    """
    
    # 🔒 VERIFICAÇÃO: Apenas admin pode executar migração
    if current_user.tipo != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Apenas administradores podem executar migração de dados"
        )
    
    try:
        # 1. Buscar alunos sem created_by
        alunos_sem_created_by = await db.alunos.find({
            "$or": [
                {"created_by": {"$exists": False}},
                {"created_by": None},
                {"created_by": ""}
            ],
            "ativo": True
        }).to_list(1000)
        
        print(f"🔍 Encontrados {len(alunos_sem_created_by)} alunos sem created_by")
        
        if not alunos_sem_created_by:
            return {
                "message": "Nenhum aluno precisa de correção",
                "alunos_corrigidos": 0,
                "detalhes": []
            }
        
        # 2. Buscar todas as turmas ativas
        turmas = await db.turmas.find({"ativo": True}).to_list(1000)
        turmas_dict = {turma["id"]: turma for turma in turmas}
        
        # 3. Buscar instrutores para cada turma
        instrutores = await db.usuarios.find({
            "tipo": "instrutor",
            "status": "ativo"
        }).to_list(1000)
        instrutores_dict = {instrutor["id"]: instrutor for instrutor in instrutores}
        
        detalhes = []
        alunos_corrigidos = 0
        
        # 4. Para cada aluno sem created_by
        for aluno in alunos_sem_created_by:
            turma_id = aluno.get("turma_id")
            
            if turma_id and turma_id in turmas_dict:
                # Aluno está em uma turma - associar ao instrutor da turma
                turma = turmas_dict[turma_id]
                instrutor_id = turma.get("instrutor_id")
                
                if instrutor_id and instrutor_id in instrutores_dict:
                    instrutor = instrutores_dict[instrutor_id]
                    
                    # Atualizar aluno com dados do instrutor
                    await db.alunos.update_one(
                        {"id": aluno["id"]},
                        {
                            "$set": {
                                "created_by": instrutor_id,
                                "created_by_name": instrutor["nome"],
                                "created_by_type": "instrutor"
                            }
                        }
                    )
                    
                    alunos_corrigidos += 1
                    detalhes.append({
                        "aluno": aluno["nome"],
                        "cpf": aluno.get("cpf", "N/A"),
                        "turma": turma["nome"],
                        "instrutor": instrutor["nome"],
                        "acao": "associado_ao_instrutor_da_turma"
                    })
                    
                    print(f"✅ {aluno['nome']} → instrutor {instrutor['nome']} (turma {turma['nome']})")
                else:
                    detalhes.append({
                        "aluno": aluno["nome"],
                        "cpf": aluno.get("cpf", "N/A"),
                        "turma": turma["nome"],
                        "problema": "turma_sem_instrutor",
                        "acao": "nao_corrigido"
                    })
            else:
                # Aluno não está em turma - manter sem created_by (será removido na limpeza)
                detalhes.append({
                    "aluno": aluno["nome"],
                    "cpf": aluno.get("cpf", "N/A"),
                    "problema": "sem_turma",
                    "acao": "nao_corrigido"
                })
        
        return {
            "message": f"Migração concluída: {alunos_corrigidos} alunos associados a instrutores",
            "total_encontrados": len(alunos_sem_created_by),
            "alunos_corrigidos": alunos_corrigidos,
            "detalhes": detalhes[:50]  # Máximo 50 no retorno
        }
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno na migração: {str(e)}"
        )

@api_router.post("/database/reset-all")
async def reset_all_database(current_user: UserResponse = Depends(get_current_user)):
    """🚨 RESET TOTAL: Apaga TODOS os alunos e turmas do banco
    
    ⚠️ CUIDADO: Esta operação não pode ser desfeita!
    """
    
    # 🔒 VERIFICAÇÃO: Apenas admin pode executar
    if current_user.tipo != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Apenas administradores podem resetar o banco"
        )
    
    try:
        # Contar antes da limpeza
        alunos_count = await db.alunos.count_documents({})
        turmas_count = await db.turmas.count_documents({})
        chamadas_count = await db.chamadas.count_documents({})
        
        print(f"🚨 RESET TOTAL INICIADO por {current_user.email}")
        print(f"   Alunos a serem removidos: {alunos_count}")
        print(f"   Turmas a serem removidas: {turmas_count}")
        print(f"   Chamadas a serem removidas: {chamadas_count}")
        
        # APAGAR TUDO
        result_alunos = await db.alunos.delete_many({})
        result_turmas = await db.turmas.delete_many({})
        result_chamadas = await db.chamadas.delete_many({})
        
        print(f"✅ RESET CONCLUÍDO:")
        print(f"   Alunos removidos: {result_alunos.deleted_count}")
        print(f"   Turmas removidas: {result_turmas.deleted_count}")
        print(f"   Chamadas removidas: {result_chamadas.deleted_count}")
        
        return {
            "message": "🚨 BANCO RESETADO COMPLETAMENTE",
            "removidos": {
                "alunos": result_alunos.deleted_count,
                "turmas": result_turmas.deleted_count,
                "chamadas": result_chamadas.deleted_count
            },
            "status": "BANCO LIMPO - PRONTO PARA RECOMEÇAR"
        }
        
    except Exception as e:
        print(f"❌ Erro no reset: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro no reset do banco: {str(e)}"
        )

@api_router.get("/debug/students/{user_id}")
async def debug_students_for_user(user_id: str, current_user: UserResponse = Depends(get_current_user)):
    """🔍 DEBUG: Verificar exatamente quais alunos um usuário deveria ver"""
    
    if current_user.tipo != "admin":
        raise HTTPException(status_code=403, detail="Apenas admin pode usar debug")
    
    # Buscar o usuário
    user = await db.usuarios.find_one({"id": user_id})
    if not user:
        return {"error": "Usuário não encontrado"}
    
    # Buscar TODOS os alunos
    todos_alunos = await db.alunos.find({}).to_list(1000)
    
    # Filtrar por created_by
    alunos_created_by = [a for a in todos_alunos if a.get("created_by") == user_id]
    
    # Filtrar por ativo=True
    alunos_ativos = [a for a in todos_alunos if a.get("ativo") == True]
    
    # Filtrar por created_by E ativo
    alunos_filtrados = [a for a in todos_alunos if a.get("created_by") == user_id and a.get("ativo") == True]
    
    # 🔍 ANÁLISE DETALHADA: Encontrar alunos com created_by diferente
    alunos_outros_created_by = [a for a in todos_alunos if a.get("created_by") and a.get("created_by") != user_id]
    alunos_sem_created_by = [a for a in todos_alunos if not a.get("created_by")]
    
    return {
        "usuario": {
            "id": user["id"],
            "nome": user["nome"],
            "tipo": user["tipo"],
            "curso_id": user.get("curso_id"),
            "unidade_id": user.get("unidade_id")
        },
        "totais": {
            "todos_alunos": len(todos_alunos),
            "alunos_created_by": len(alunos_created_by),
            "alunos_ativos": len(alunos_ativos),
            "alunos_filtrados": len(alunos_filtrados),
            "alunos_sem_created_by": len(alunos_sem_created_by),
            "alunos_outros_created_by": len(alunos_outros_created_by)
        },
        "alunos_created_by": [
            {
                "id": a["id"],
                "nome": a["nome"],
                "cpf": a.get("cpf"),
                "ativo": a.get("ativo"),
                "created_by": a.get("created_by"),
                "created_by_name": a.get("created_by_name")
            } for a in alunos_created_by
        ],
        "alunos_filtrados": [
            {
                "id": a["id"],
                "nome": a["nome"],
                "cpf": a.get("cpf"),
                "ativo": a.get("ativo"),
                "created_by": a.get("created_by"),
                "created_by_name": a.get("created_by_name")
            } for a in alunos_filtrados
        ],
        "alunos_sem_created_by": [
            {
                "id": a["id"],
                "nome": a["nome"],
                "cpf": a.get("cpf"),
                "ativo": a.get("ativo"),
                "created_by": a.get("created_by"),
                "created_by_name": a.get("created_by_name")
            } for a in alunos_sem_created_by[:10]  # Máximo 10
        ],
        "alunos_outros_created_by": [
            {
                "id": a["id"],
                "nome": a["nome"],
                "cpf": a.get("cpf"),
                "ativo": a.get("ativo"),
                "created_by": a.get("created_by"),
                "created_by_name": a.get("created_by_name")
            } for a in alunos_outros_created_by[:10]  # Máximo 10
        ]
    }

@api_router.post("/students/import-csv")
async def import_students_csv(
    file: UploadFile = File(...), 
    current_user: UserResponse = Depends(get_current_user)
):
    """📑 IMPORTAÇÃO CSV - LÓGICA REFINADA 29/09/2025
    
    CSV deve conter: nome,cpf,data_nascimento,curso,turma,email,telefone
    
    👨‍🏫 Instrutor: Só aceita curso/unidade dele
    📊 Pedagogo: Só aceita cursos da unidade dele  
    👩‍💻 Monitor: NÃO pode importar
    👑 Admin: Aceita qualquer curso/unidade
    """
    
    # 🔒 MONITOR: Não pode importar alunos
    if current_user.tipo == "monitor":
        raise HTTPException(
            status_code=403, 
            detail="Monitores não podem importar alunos CSV"
        )
    
    # Verificar se arquivo é CSV
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser CSV")
    
    # Ler conteúdo do arquivo
    contents = await file.read()
    
    # 🔧 CORREÇÃO: Detectar encoding e separador automaticamente
    try:
        # Tentar UTF-8 primeiro
        csv_content = contents.decode('utf-8')
    except UnicodeDecodeError:
        try:
            # Fallback para Windows-1252 (comum em arquivos Excel brasileiros)
            csv_content = contents.decode('windows-1252')
        except UnicodeDecodeError:
            # Último recurso: ISO-8859-1
            csv_content = contents.decode('iso-8859-1')
    
    # 🔧 CORREÇÃO: Detectar separador (vírgula ou ponto e vírgula)
    delimiter = ',' if ',' in csv_content.split('\n')[0] else ';'
    print(f"🔍 CSV Delimiter detectado: '{delimiter}'")
    
    csv_reader = csv.DictReader(io.StringIO(csv_content), delimiter=delimiter)
    
    # Validar campos obrigatórios no CSV
    required_fields = ['nome', 'cpf', 'data_nascimento', 'curso']
    if not all(field in csv_reader.fieldnames for field in required_fields):
        raise HTTPException(
            status_code=400, 
            detail=f"CSV deve conter campos: {', '.join(required_fields)}"
        )
    
    # Processar linhas do CSV
    results = {
        'success': [],
        'errors': [],
        'duplicates': [],
        'unauthorized': [],
        'warnings': []  # Para alunos sem turma definida
    }
    
    # Buscar cursos e turmas para validação
    cursos = await db.cursos.find({}).to_list(1000)
    cursos_dict = {curso['nome']: curso for curso in cursos}
    
    # Buscar turmas do usuário para validação de permissões
    turmas = await db.turmas.find({}).to_list(1000)
    turmas_dict = {}
    for turma in turmas:
        key = f"{turma.get('curso_id', '')}_{turma['nome']}"
        turmas_dict[key] = turma
    
    for row_num, row in enumerate(csv_reader, start=2):  # Linha 2+ (header = linha 1)
        try:
            # 🔧 LIMPEZA: Remover caracteres especiais (BOM, �, etc)
            nome_limpo = row['nome'].strip().lstrip('\ufeff').lstrip('�').strip()
            cpf_limpo = row['cpf'].strip().lstrip('\ufeff').lstrip('�').strip()
            data_nascimento_limpa = row['data_nascimento'].strip().lstrip('\ufeff').lstrip('�').strip()
            curso_limpo = row['curso'].strip().lstrip('\ufeff').lstrip('�').strip()
            
            print(f"🔍 Processando linha {row_num}:")
            print(f"   Nome: '{nome_limpo}'")
            print(f"   CPF: '{cpf_limpo}'")
            print(f"   Data: '{data_nascimento_limpa}'")
            print(f"   Curso: '{curso_limpo}'")
            
            # Validar campos obrigatórios
            if not nome_limpo or not cpf_limpo or not data_nascimento_limpa:
                results['errors'].append(f"Linha {row_num}: Campos obrigatórios em branco")
                continue
            
            # 🔧 CORREÇÃO: Converter data de dd/mm/yyyy para yyyy-mm-dd
            try:
                if '/' in data_nascimento_limpa:
                    # Formato brasileiro: dd/mm/yyyy
                    day, month, year = data_nascimento_limpa.split('/')
                    data_nascimento_iso = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                else:
                    # Já está em formato ISO
                    data_nascimento_iso = data_nascimento_limpa
            except ValueError:
                results['errors'].append(f"Linha {row_num}: Data de nascimento inválida: {data_nascimento_limpa}")
                continue
            
            # Validar se curso existe
            if curso_limpo not in cursos_dict:
                # 💡 MELHORIA: Sugerir cursos disponíveis
                cursos_disponiveis = list(cursos_dict.keys())[:5]  # Máximo 5 sugestões
                sugestoes = ", ".join(f"'{c}'" for c in cursos_disponiveis)
                results['errors'].append(
                    f"Linha {row_num}: Curso '{curso_limpo}' não encontrado. " +
                    f"Cursos disponíveis: {sugestoes}{'...' if len(cursos_dict) > 5 else ''}"
                )
                continue
            
            curso = cursos_dict[curso_limpo]
            
            # 🔒 VALIDAÇÃO POR TIPO DE USUÁRIO
            if current_user.tipo == "instrutor":
                # Instrutor: só aceita seu curso
                if curso['id'] != current_user.curso_id:
                    results['unauthorized'].append(
                        f"Linha {row_num}: Instrutor não pode importar alunos para curso '{curso['nome']}'"
                    )
                    continue
                    
            elif current_user.tipo == "pedagogo":
                # Pedagogo: só aceita cursos da sua unidade
                if curso.get('unidade_id') != current_user.unidade_id:
                    results['unauthorized'].append(
                        f"Linha {row_num}: Pedagogo não pode importar alunos para curso fora da sua unidade"
                    )
                    continue
            
            # Admin: aceita qualquer curso (sem restrições)
            
            # Verificar duplicado (CPF já existe)
            existing_aluno = await db.alunos.find_one({"cpf": cpf_limpo})
            if existing_aluno:
                results['duplicates'].append(f"Linha {row_num}: CPF {cpf_limpo} já cadastrado")
                continue
            
            # 🎯 LÓGICA DE TURMA
            turma_nome = row.get('turma', '').strip()
            turma_id = None
            status_turma = "nao_alocado"  # Default para alunos sem turma
            
            if turma_nome:
                # Buscar turma específica do curso
                turma_key = f"{curso['id']}_{turma_nome}"
                if turma_key in turmas_dict:
                    turma_id = turmas_dict[turma_key]['id']
                    status_turma = "alocado"
                else:
                    # Turma não existe - criar automaticamente se usuário tem permissão
                    if current_user.tipo in ["admin", "instrutor"]:
                        # Criar turma automaticamente
                        nova_turma = {
                            'id': str(uuid.uuid4()),
                            'nome': turma_nome,
                            'curso_id': curso['id'],
                            'unidade_id': curso.get('unidade_id', current_user.unidade_id),
                            'instrutor_id': current_user.id if current_user.tipo == "instrutor" else None,
                            'alunos_ids': [],
                            'ativa': True,
                            'created_at': datetime.now(timezone.utc).isoformat()
                        }
                        await db.turmas.insert_one(nova_turma)
                        turma_id = nova_turma['id']
                        status_turma = "alocado"
                        results['warnings'].append(f"Linha {row_num}: Turma '{turma_nome}' criada automaticamente")
                    else:
                        results['warnings'].append(f"Linha {row_num}: Turma '{turma_nome}' não existe - aluno será marcado como 'não alocado'")
            else:
                results['warnings'].append(f"Linha {row_num}: Sem turma definida - aluno será marcado como 'não alocado'")
            
            # Criar aluno com dados limpos
            aluno_data = {
                'id': str(uuid.uuid4()),
                'nome': nome_limpo,
                'cpf': cpf_limpo,
                'data_nascimento': data_nascimento_iso,
                'email': row.get('email', '').strip().lstrip('\ufeff').lstrip('�').strip(),
                'telefone': row.get('telefone', '').strip().lstrip('\ufeff').lstrip('�').strip(),
                'curso_id': curso['id'],
                'turma_id': turma_id,
                'status_turma': status_turma,
                'status': 'ativo',
                'ativo': True,  # ✅ CRÍTICO: Campo ativo para filtro
                'created_by': current_user.id,  # ID do usuário que importou
                'created_by_name': current_user.nome,  # Nome do usuário que importou
                'created_by_type': current_user.tipo,  # Tipo do usuário que importou
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            print(f"🔍 CSV Import - Criando aluno: {nome_limpo}")
            print(f"   created_by: {aluno_data['created_by']}")
            print(f"   created_by_name: {aluno_data['created_by_name']}")
            
            # Inserir aluno no banco
            await db.alunos.insert_one(aluno_data)
            
            # Se turma existe, adicionar aluno à lista de alunos da turma
            if turma_id:
                await db.turmas.update_one(
                    {"id": turma_id},
                    {"$addToSet": {"alunos_ids": aluno_data['id']}}
                )
            
            results['success'].append(f"Linha {row_num}: {nome_limpo} cadastrado com sucesso")
            
        except Exception as e:
            results['errors'].append(f"Linha {row_num}: Erro interno - {str(e)}")
    
    return {
        "message": f"Importação concluída: {len(results['success'])} sucessos, {len(results['errors']) + len(results['duplicates']) + len(results['unauthorized'])} falhas",
        "details": results,
        "summary": {
            "total_processed": len(results['success']) + len(results['errors']) + len(results['duplicates']) + len(results['unauthorized']),
            "successful": len(results['success']),
            "errors": len(results['errors']),
            "duplicates": len(results['duplicates']),
            "unauthorized": len(results['unauthorized']),
            "warnings": len(results['warnings'])
        }
    }

# TURMAS ROUTES
@api_router.post("/classes", response_model=Turma)
async def create_turma(turma_create: TurmaCreate, current_user: UserResponse = Depends(get_current_user)):
    # Admin pode criar qualquer turma
    if current_user.tipo == "admin":
        # Validar se instrutor existe e está ativo
        if turma_create.instrutor_id:
            instrutor = await db.usuarios.find_one({"id": turma_create.instrutor_id, "tipo": "instrutor", "status": "ativo"})
            if not instrutor:
                raise HTTPException(status_code=400, detail="Instrutor não encontrado ou inativo")
    
    # Instrutor só pode criar turmas do seu próprio curso e unidade
    elif current_user.tipo == "instrutor":
        if not current_user.curso_id or not current_user.unidade_id:
            raise HTTPException(status_code=400, detail="Instrutor deve estar associado a um curso e unidade")
        
        # Validar se a turma é do curso e unidade do instrutor
        if turma_create.curso_id != current_user.curso_id:
            raise HTTPException(status_code=403, detail="Instrutor só pode criar turmas do seu curso")
        
        if turma_create.unidade_id != current_user.unidade_id:
            raise HTTPException(status_code=403, detail="Instrutor só pode criar turmas da sua unidade")
        
        # Definir instrutor automaticamente
        turma_create.instrutor_id = current_user.id
    
    else:
        raise HTTPException(status_code=403, detail="Apenas admins e instrutores podem criar turmas")
    
    # Validar se curso e unidade existem
    curso = await db.cursos.find_one({"id": turma_create.curso_id})
    if not curso:
        raise HTTPException(status_code=400, detail="Curso não encontrado")
    
    unidade = await db.unidades.find_one({"id": turma_create.unidade_id})
    if not unidade:
        raise HTTPException(status_code=400, detail="Unidade não encontrada")
    
    turma_dict = prepare_for_mongo(turma_create.dict())
    turma_obj = Turma(**turma_dict)
    
    mongo_data = prepare_for_mongo(turma_obj.dict())
    await db.turmas.insert_one(mongo_data)
    return turma_obj

@api_router.get("/classes", response_model=List[Turma])
async def get_turmas(current_user: UserResponse = Depends(get_current_user)):
    if current_user.tipo == "admin":
        turmas_raw = await db.turmas.find({"ativo": True}).to_list(1000)
        # Processar turmas admin e garantir compatibilidade
        result_turmas = []
        for turma in turmas_raw:
            try:
                parsed_turma = parse_from_mongo(turma)
                if 'ciclo' not in parsed_turma or parsed_turma['ciclo'] is None:
                    parsed_turma['ciclo'] = None
                turma_obj = Turma(**parsed_turma)
                result_turmas.append(turma_obj)
            except Exception as e:
                print(f"⚠️ Admin - Erro ao processar turma {turma.get('id', 'SEM_ID')}: {e}")
                parsed_turma = parse_from_mongo(turma)
                parsed_turma['ciclo'] = None
                try:
                    turma_obj = Turma(**parsed_turma)
                    result_turmas.append(turma_obj)
                except Exception as e2:
                    print(f"❌ Admin - Erro crítico turma {turma.get('id', 'SEM_ID')}: {e2}")
                    continue
        return result_turmas
    else:
        # Instrutor, pedagogo ou monitor vê turmas do seu curso e unidade
        query = {"ativo": True}
        
        if current_user.tipo == "instrutor":
            # Instrutor vê suas próprias turmas do curso
            query["instrutor_id"] = current_user.id
            if current_user.curso_id:
                query["curso_id"] = current_user.curso_id
            if current_user.unidade_id:
                query["unidade_id"] = current_user.unidade_id
        
        elif current_user.tipo in ["pedagogo", "monitor"]:
            # Pedagogo e monitor veem turmas do seu curso e unidade
            if current_user.curso_id:
                query["curso_id"] = current_user.curso_id
            if current_user.unidade_id:
                query["unidade_id"] = current_user.unidade_id
        
        turmas = await db.turmas.find(query).to_list(1000)
    
    # Processar turmas e garantir compatibilidade com dados antigos
    result_turmas = []
    for turma in turmas:
        try:
            parsed_turma = parse_from_mongo(turma)
            # Garantir que campo ciclo existe (compatibilidade com dados antigos)
            if 'ciclo' not in parsed_turma or parsed_turma['ciclo'] is None:
                parsed_turma['ciclo'] = None
            turma_obj = Turma(**parsed_turma)
            result_turmas.append(turma_obj)
        except Exception as e:
            print(f"⚠️ Erro ao processar turma {turma.get('id', 'SEM_ID')}: {e}")
            # Adicionar campos faltantes para compatibilidade
            parsed_turma = parse_from_mongo(turma)
            parsed_turma['ciclo'] = None  # Campo obrigatório faltante
            try:
                turma_obj = Turma(**parsed_turma)
                result_turmas.append(turma_obj)
            except Exception as e2:
                print(f"❌ Erro crítico ao processar turma {turma.get('id', 'SEM_ID')}: {e2}")
                continue
    
    return result_turmas

@api_router.put("/classes/{turma_id}/students/{aluno_id}")
async def add_aluno_to_turma(turma_id: str, aluno_id: str, current_user: UserResponse = Depends(get_current_user)):
    # Check if turma exists
    turma = await db.turmas.find_one({"id": turma_id})
    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    
    # Verificar permissões baseadas no curso/unidade
    if current_user.tipo == "admin":
        # Admin pode adicionar qualquer aluno
        pass
    elif current_user.tipo == "instrutor":
        # Instrutor só pode adicionar alunos em suas próprias turmas
        if turma["instrutor_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Instrutor só pode gerenciar suas próprias turmas")
    elif current_user.tipo in ["pedagogo", "monitor"]:
        # Pedagogo/monitor só pode adicionar em turmas do seu curso e unidade
        if (current_user.curso_id and turma["curso_id"] != current_user.curso_id) or \
           (current_user.unidade_id and turma["unidade_id"] != current_user.unidade_id):
            raise HTTPException(status_code=403, detail="Acesso negado: turma fora do seu curso/unidade")
    else:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    if len(turma.get("alunos_ids", [])) >= turma.get("vagas_total", 30):
        raise HTTPException(status_code=400, detail="Turma está lotada")
    
    # Verificar se aluno existe
    aluno = await db.alunos.find_one({"id": aluno_id})
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    # Add aluno to turma
    await db.turmas.update_one(
        {"id": turma_id},
        {
            "$addToSet": {"alunos_ids": aluno_id},
            "$inc": {"vagas_ocupadas": 1}
        }
    )
    
    return {"message": "Aluno adicionado à turma"}

@api_router.delete("/classes/{turma_id}/students/{aluno_id}")
async def remove_aluno_from_turma(turma_id: str, aluno_id: str, current_user: UserResponse = Depends(get_current_user)):
    check_admin_permission(current_user)
    
    await db.turmas.update_one(
        {"id": turma_id},
        {
            "$pull": {"alunos_ids": aluno_id},
            "$inc": {"vagas_ocupadas": -1}
        }
    )
    
    return {"message": "Aluno removido da turma"}

@api_router.delete("/classes/{turma_id}")
async def delete_turma(turma_id: str, current_user: UserResponse = Depends(get_current_user)):
    """🗑️ DELETAR TURMA - Apenas Admin pode deletar turmas"""
    
    # 🔒 VERIFICAÇÃO: Apenas admin pode deletar turmas
    if current_user.tipo != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Apenas administradores podem deletar turmas"
        )
    
    # Verificar se turma existe
    turma = await db.turmas.find_one({"id": turma_id})
    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    
    # ⚠️ VERIFICAÇÃO: Turma tem alunos matriculados?
    if turma.get('alunos_ids') and len(turma.get('alunos_ids', [])) > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Não é possível deletar turma com {len(turma['alunos_ids'])} aluno(s) matriculado(s). Remova os alunos primeiro."
        )
    
    # 🔍 VERIFICAÇÃO: Turma tem chamadas registradas?
    chamadas_count = await db.chamadas.count_documents({"turma_id": turma_id})
    if chamadas_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Não é possível deletar turma com {chamadas_count} chamada(s) registrada(s). Histórico de presença será perdido."
        )
    
    # 🗑️ DELETAR TURMA
    result = await db.turmas.delete_one({"id": turma_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=500, detail="Erro ao deletar turma")
    
    print(f"🗑️ Admin {current_user.nome} deletou turma: {turma.get('nome', 'SEM_NOME')} (ID: {turma_id})")
    
    return {
        "message": f"Turma '{turma.get('nome', 'SEM_NOME')}' deletada com sucesso",
        "turma_deletada": {
            "id": turma_id,
            "nome": turma.get('nome'),
            "curso_nome": turma.get('curso_nome', 'N/A'),
            "instrutor_nome": turma.get('instrutor_nome', 'N/A')
        }
    }

# CHAMADA ROUTES
@api_router.post("/attendance", response_model=Chamada)
async def create_chamada(chamada_create: ChamadaCreate, current_user: UserResponse = Depends(get_current_user)):
    # 🔒 VALIDAÇÃO DE DATA: Só pode fazer chamada do dia atual
    data_chamada = chamada_create.data
    data_hoje = date.today()
    
    if data_chamada != data_hoje:
        raise HTTPException(
            status_code=400, 
            detail=f"Só é possível fazer chamada da data atual ({data_hoje.strftime('%d/%m/%Y')})"
        )
    
    # 🔒 VALIDAÇÃO: Verificar se já existe chamada para esta turma hoje
    chamada_existente = await db.chamadas.find_one({
        "turma_id": chamada_create.turma_id,
        "data": data_hoje.isoformat()
    })
    
    if chamada_existente:
        raise HTTPException(
            status_code=400,
            detail=f"Chamada já foi realizada para esta turma hoje ({data_hoje.strftime('%d/%m/%Y')})"
        )
    
    # Verificar permissões da turma
    turma = await db.turmas.find_one({"id": chamada_create.turma_id})
    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    
    # Verificar se o usuário pode fazer chamada nesta turma
    if current_user.tipo == "instrutor":
        if turma["instrutor_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Você só pode fazer chamada das suas turmas")
    elif current_user.tipo in ["pedagogo", "monitor"]:
        if (current_user.curso_id and turma["curso_id"] != current_user.curso_id) or \
           (current_user.unidade_id and turma["unidade_id"] != current_user.unidade_id):
            raise HTTPException(status_code=403, detail="Acesso negado: turma fora do seu curso/unidade")
    elif current_user.tipo != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    # 🕐 Adicionar hora de registro para alunos presentes
    hora_atual = datetime.now().strftime("%H:%M")
    presencas_com_hora = {}
    
    for aluno_id, dados_presenca in chamada_create.presencas.items():
        presencas_com_hora[aluno_id] = {
            "presente": dados_presenca.get("presente", False),
            "justificativa": dados_presenca.get("justificativa", ""),
            "atestado_id": dados_presenca.get("atestado_id", ""),
            # 📝 Registrar hora apenas se estiver presente
            "hora_registro": hora_atual if dados_presenca.get("presente", False) else ""
        }
    
    # Calculate totals
    total_presentes = sum(1 for p in presencas_com_hora.values() if p.get("presente", False))
    total_faltas = len(presencas_com_hora) - total_presentes
    
    chamada_dict = prepare_for_mongo(chamada_create.dict())
    chamada_dict.update({
        "instrutor_id": current_user.id,
        "total_presentes": total_presentes,
        "total_faltas": total_faltas,
        "presencas": presencas_com_hora  # 🕐 Usar presencas com hora
    })
    
    chamada_obj = Chamada(**chamada_dict)
    mongo_data = prepare_for_mongo(chamada_obj.dict())
    await db.chamadas.insert_one(mongo_data)
    
    return chamada_obj

@api_router.get("/classes/{turma_id}/attendance", response_model=List[Chamada])
async def get_chamadas_turma(turma_id: str, current_user: UserResponse = Depends(get_current_user)):
    chamadas = await db.chamadas.find({"turma_id": turma_id}).to_list(1000)
    return [Chamada(**parse_from_mongo(chamada)) for chamada in chamadas]

@api_router.get("/classes/{turma_id}/students")
async def get_turma_students(turma_id: str, current_user: UserResponse = Depends(get_current_user)):
    turma = await db.turmas.find_one({"id": turma_id})
    if not turma:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    
    aluno_ids = turma.get("alunos_ids", [])
    if not aluno_ids:
        return []
    
    alunos = await db.alunos.find({"id": {"$in": aluno_ids}, "ativo": True}).to_list(1000)
    
    # Clean up MongoDB-specific fields and parse dates
    result = []
    for aluno in alunos:
        # Remove MongoDB ObjectId field
        if '_id' in aluno:
            del aluno['_id']
        # Parse dates and clean up the data
        cleaned_aluno = parse_from_mongo(aluno)
        result.append(cleaned_aluno)
    
    return result

# UPLOAD ROUTES
@api_router.post("/upload/atestado")
async def upload_atestado(file: UploadFile = File(...), current_user: UserResponse = Depends(get_current_user)):
    if file.content_type not in ["image/jpeg", "image/png", "application/pdf"]:
        raise HTTPException(status_code=400, detail="Formato de arquivo não suportado")
    
    # Convert file to base64 for storage (simple solution)
    contents = await file.read()
    file_base64 = base64.b64encode(contents).decode('utf-8')
    
    file_id = str(uuid.uuid4())
    file_data = {
        "id": file_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "data": file_base64,
        "uploaded_by": current_user.id,
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.atestados.insert_one(file_data)
    return {"file_id": file_id, "filename": file.filename}

# DESISTENTES ROUTES
@api_router.post("/dropouts", response_model=Desistente)
async def create_desistente(desistente_create: DesistenteCreate, current_user: UserResponse = Depends(get_current_user)):
    # 🔒 VALIDAÇÃO DE PERMISSÕES: Verificar se usuário pode registrar desistência deste aluno
    if current_user.tipo not in ["admin", "instrutor", "pedagogo"]:
        raise HTTPException(status_code=403, detail="Apenas admin, instrutor e pedagogo podem registrar desistências")
    
    # Verificar se o aluno existe
    aluno = await db.alunos.find_one({"id": desistente_create.aluno_id})
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    # Para não-admin: verificar se o aluno está nas turmas do usuário
    if current_user.tipo != "admin":
        # Buscar turmas que contêm este aluno
        turmas_aluno = await db.turmas.find({
            "alunos_ids": desistente_create.aluno_id,
            "ativo": True
        }).to_list(1000)
        
        # Verificar permissões baseadas no tipo de usuário
        tem_permissao = False
        
        if current_user.tipo == "instrutor":
            # Instrutor: pode registrar desistência de alunos das suas turmas
            for turma in turmas_aluno:
                if turma.get("instrutor_id") == current_user.id:
                    tem_permissao = True
                    break
                    
        elif current_user.tipo == "pedagogo":
            # Pedagogo: pode registrar desistência de alunos da sua unidade
            for turma in turmas_aluno:
                if turma.get("unidade_id") == current_user.unidade_id:
                    tem_permissao = True
                    break
        
        if not tem_permissao:
            raise HTTPException(
                status_code=403, 
                detail="Você só pode registrar desistência de alunos das suas turmas/unidade"
            )
    
    desistente_dict = prepare_for_mongo(desistente_create.dict())
    desistente_dict["registrado_por"] = current_user.id
    
    desistente_obj = Desistente(**desistente_dict)
    mongo_data = prepare_for_mongo(desistente_obj.dict())
    await db.desistentes.insert_one(mongo_data)
    
    # Update aluno status
    await db.alunos.update_one(
        {"id": desistente_create.aluno_id},
        {"$set": {"status": "desistente"}}
    )
    
    return desistente_obj

@api_router.get("/dropouts", response_model=List[Desistente])
async def get_desistentes(
    skip: int = 0,
    limit: int = 100,
    turma_id: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    query = {}
    if turma_id:
        query["turma_id"] = turma_id
        
    desistentes = await db.desistentes.find(query).skip(skip).limit(limit).to_list(limit)
    return [Desistente(**parse_from_mongo(desistente)) for desistente in desistentes]

# REPORTS AND CSV EXPORT
@api_router.get("/reports/attendance")
async def get_attendance_report(
    turma_id: Optional[str] = None,
    unidade_id: Optional[str] = None,
    curso_id: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    export_csv: bool = False,
    current_user: UserResponse = Depends(get_current_user)
):
    query = {}
    
    # 🔒 FILTROS DE PERMISSÃO POR TIPO DE USUÁRIO
    if current_user.tipo == "instrutor":
        # Instrutor só pode ver suas próprias turmas
        turmas_instrutor = await db.turmas.find({"instrutor_id": current_user.id}).to_list(1000)
        turmas_ids = [turma["id"] for turma in turmas_instrutor]
        
        if turmas_ids:
            query["turma_id"] = {"$in": turmas_ids}
        else:
            # Se não tem turmas, retorna vazio
            return [] if not export_csv else {"csv_data": ""}
            
    elif current_user.tipo in ["pedagogo", "monitor"]:
        # Pedagogo/Monitor só vê turmas do seu curso/unidade
        turmas_query = {}
        if current_user.curso_id:
            turmas_query["curso_id"] = current_user.curso_id
        if current_user.unidade_id:
            turmas_query["unidade_id"] = current_user.unidade_id
            
        turmas_permitidas = await db.turmas.find(turmas_query).to_list(1000)
        turmas_ids = [turma["id"] for turma in turmas_permitidas]
        
        if turmas_ids:
            query["turma_id"] = {"$in": turmas_ids}
        else:
            # Se não tem turmas permitidas, retorna vazio
            return [] if not export_csv else {"csv_data": ""}
    
    # Filtro por turma específica (aplicado após filtros de permissão)
    if turma_id:
        if "turma_id" in query:
            # Se já há filtro de permissão, verifica se a turma específica está permitida
            if isinstance(query["turma_id"], dict) and "$in" in query["turma_id"]:
                if turma_id not in query["turma_id"]["$in"]:
                    raise HTTPException(status_code=403, detail="Acesso negado a esta turma")
            query["turma_id"] = turma_id
        else:
            query["turma_id"] = turma_id
    
    # Filtros para admin: unidade e curso
    if current_user.tipo == "admin":
        if unidade_id or curso_id:
            # Buscar turmas que atendem aos critérios
            turmas_query = {}
            if unidade_id:
                turmas_query["unidade_id"] = unidade_id
            if curso_id:
                turmas_query["curso_id"] = curso_id
                
            turmas = await db.turmas.find(turmas_query).to_list(1000)
            turmas_ids = [turma["id"] for turma in turmas]
            
            if turmas_ids:
                query["turma_id"] = {"$in": turmas_ids}
            else:
                # Se não há turmas que atendem aos critérios, retorna vazio
                return [] if not export_csv else {"csv_data": ""}
    
    # Filtro por data
    if data_inicio and data_fim:
        query["data"] = {"$gte": data_inicio.isoformat(), "$lte": data_fim.isoformat()}
    elif data_inicio:
        query["data"] = {"$gte": data_inicio.isoformat()}
    elif data_fim:
        query["data"] = {"$lte": data_fim.isoformat()}
    
    chamadas = await db.chamadas.find(query).to_list(1000)
    
    if export_csv:
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 📊 FORMATO CSV COMPLETO CONFORME ESPECIFICAÇÃO
        writer.writerow([
            "Aluno", "CPF", "Matricula", "Turma", "Curso", "Data", 
            "Hora_Inicio", "Hora_Fim", "Status", "Hora_Registro", 
            "Professor", "Unidade", "Observacoes"
        ])
        
        # Coletar dados completos para cada chamada
        for chamada in chamadas:
            try:
                # Buscar dados da turma
                turma = await db.turmas.find_one({"id": chamada.get("turma_id")})
                if not turma:
                    continue
                
                # Buscar dados do curso
                curso = await db.cursos.find_one({"id": turma.get("curso_id")}) if turma.get("curso_id") else None
                
                # Buscar dados da unidade
                unidade = await db.unidades.find_one({"id": turma.get("unidade_id")}) if turma.get("unidade_id") else None
                
                # Buscar dados do instrutor
                instrutor = await db.usuarios.find_one({"id": turma.get("instrutor_id")}) if turma.get("instrutor_id") else None
                
                # Dados da chamada
                data_chamada = chamada.get("data", "")
                presencas = chamada.get("presencas", {})
                observacoes_gerais = chamada.get("observacoes", "")
                
                # Horários da turma (se disponível)
                hora_inicio = turma.get("horario_inicio", "08:00")
                hora_fim = turma.get("horario_fim", "12:00")
                
                # Para cada aluno na chamada
                for aluno_id, dados_presenca in presencas.items():
                    try:
                        # Buscar dados completos do aluno
                        aluno = await db.alunos.find_one({"id": aluno_id})
                        if not aluno:
                            continue
                        
                        # Determinar status detalhado
                        presente = dados_presenca.get("presente", False)
                        justificativa = dados_presenca.get("justificativa", "")
                        hora_registro = dados_presenca.get("hora_registro", "")
                        
                        # Status mais detalhado
                        if presente:
                            if hora_registro and hora_registro > hora_inicio:
                                status = "Atrasado"
                            else:
                                status = "Presente"
                        else:
                            if justificativa and ("atestado" in justificativa.lower() or "justificada" in justificativa.lower()):
                                status = "Justificado"
                            else:
                                status = "Ausente"
                        
                        # Observações combinadas
                        obs_final = []
                        if justificativa:
                            obs_final.append(justificativa)
                        if observacoes_gerais:
                            obs_final.append(f"Obs. turma: {observacoes_gerais}")
                        observacoes_texto = "; ".join(obs_final)
                        
                        # Escrever linha do CSV
                        writer.writerow([
                            aluno.get("nome", ""),                          # Aluno
                            aluno.get("cpf", ""),                           # CPF
                            aluno.get("matricula", aluno.get("id", "")),    # Matricula (usa ID se não tiver)
                            turma.get("nome", ""),                          # Turma
                            curso.get("nome", "") if curso else "",         # Curso
                            data_chamada,                                   # Data
                            hora_inicio,                                    # Hora_Inicio
                            hora_fim,                                       # Hora_Fim
                            status,                                         # Status
                            hora_registro,                                  # Hora_Registro
                            instrutor.get("nome", "") if instrutor else "", # Professor
                            unidade.get("nome", "") if unidade else "",     # Unidade
                            observacoes_texto                               # Observacoes
                        ])
                        
                    except Exception as e:
                        print(f"Erro ao processar aluno {aluno_id}: {e}")
                        continue
                        
            except Exception as e:
                print(f"Erro ao processar chamada {chamada.get('id', 'unknown')}: {e}")
                continue
        
        output.seek(0)
        return {"csv_data": output.getvalue()}
    
    return [parse_from_mongo(chamada) for chamada in chamadas]

# � Função auxiliar para verificar dias de aula
def eh_dia_de_aula(data_verificar: date, dias_aula: List[str]) -> bool:
    """Verifica se uma data específica é dia de aula baseado na configuração do curso"""
    dias_semana = {
        0: "segunda",
        1: "terca", 
        2: "quarta",
        3: "quinta", 
        4: "sexta",
        5: "sabado",
        6: "domingo"
    }
    
    dia_da_semana = data_verificar.weekday()
    nome_dia = dias_semana.get(dia_da_semana, "")
    
    return nome_dia in dias_aula

# �🚨 SISTEMA DE NOTIFICAÇÕES - Chamadas Pendentes (Personalizado por Curso)
@api_router.get("/notifications/pending-calls")
async def get_pending_calls(current_user: UserResponse = Depends(get_current_user)):
    """Verificar chamadas não realizadas baseado nos dias de aula do curso"""
    
    # Data atual
    hoje = date.today()
    ontem = hoje - timedelta(days=1)
    anteontem = hoje - timedelta(days=2)
    
    # Query para turmas baseado no tipo de usuário
    query_turmas = {"ativo": True}
    
    if current_user.tipo == "instrutor":
        query_turmas["instrutor_id"] = current_user.id
    elif current_user.tipo in ["pedagogo", "monitor"]:
        if current_user.curso_id:
            query_turmas["curso_id"] = current_user.curso_id
        if current_user.unidade_id:
            query_turmas["unidade_id"] = current_user.unidade_id
    # Admin vê todas as turmas
    
    turmas = await db.turmas.find(query_turmas).to_list(1000)
    chamadas_pendentes = []
    
    for turma in turmas:
        try:
            # 📅 Buscar dados do curso para verificar dias de aula
            curso = await db.cursos.find_one({"id": turma.get("curso_id")})
            dias_aula = curso.get("dias_aula", ["segunda", "terca", "quarta", "quinta"]) if curso else ["segunda", "terca", "quarta", "quinta"]
            
            # Buscar dados do instrutor, unidade e curso
            instrutor = await db.usuarios.find_one({"id": turma.get("instrutor_id")}) if turma.get("instrutor_id") else None
            unidade = await db.unidades.find_one({"id": turma.get("unidade_id")}) if turma.get("unidade_id") else None
            
            instrutor_nome = instrutor.get("nome", "Instrutor não encontrado") if instrutor else "Sem instrutor"
            unidade_nome = unidade.get("nome", "Unidade não encontrada") if unidade else "Sem unidade"
            curso_nome = curso.get("nome", "Curso não encontrado") if curso else "Sem curso"
            
            # 📅 HOJE: Verificar se hoje é dia de aula e se tem chamada
            if eh_dia_de_aula(hoje, dias_aula):
                chamada_hoje = await db.chamadas.find_one({
                    "turma_id": turma["id"],
                    "data": hoje.isoformat()
                })
                
                if not chamada_hoje:
                    chamadas_pendentes.append({
                        "turma_id": turma["id"],
                        "turma_nome": turma["nome"],
                        "instrutor_id": turma.get("instrutor_id"),
                        "instrutor_nome": instrutor_nome,
                        "unidade_nome": unidade_nome,
                        "curso_nome": curso_nome,
                        "data_faltante": hoje.isoformat(),
                        "prioridade": "alta",
                        "motivo": f"Chamada não realizada hoje ({hoje.strftime('%d/%m/%Y')})",
                        "dias_aula": dias_aula
                    })
            
            # 📅 ONTEM: Verificar se ontem era dia de aula e se tem chamada
            if eh_dia_de_aula(ontem, dias_aula):
                chamada_ontem = await db.chamadas.find_one({
                    "turma_id": turma["id"],
                    "data": ontem.isoformat()
                })
                
                if not chamada_ontem:
                    chamadas_pendentes.append({
                        "turma_id": turma["id"],
                        "turma_nome": turma["nome"],
                        "instrutor_id": turma.get("instrutor_id"),
                        "instrutor_nome": instrutor_nome,
                        "unidade_nome": unidade_nome,
                        "curso_nome": curso_nome,
                        "data_faltante": ontem.isoformat(),
                        "prioridade": "media",
                        "motivo": f"Chamada não realizada ontem ({ontem.strftime('%d/%m/%Y')})",
                        "dias_aula": dias_aula
                    })
            
            # 📅 ANTEONTEM: Verificar se anteontem era dia de aula e se tem chamada
            if eh_dia_de_aula(anteontem, dias_aula):
                chamada_anteontem = await db.chamadas.find_one({
                    "turma_id": turma["id"],
                    "data": anteontem.isoformat()
                })
                
                if not chamada_anteontem:
                    chamadas_pendentes.append({
                        "turma_id": turma["id"],
                        "turma_nome": turma["nome"],
                        "instrutor_id": turma.get("instrutor_id"),
                        "instrutor_nome": instrutor_nome,
                        "unidade_nome": unidade_nome,
                        "curso_nome": curso_nome,
                        "data_faltante": anteontem.isoformat(),
                        "prioridade": "baixa",
                        "motivo": f"Chamada não realizada em {anteontem.strftime('%d/%m/%Y')}",
                        "dias_aula": dias_aula
                    })
                    
        except Exception as e:
            print(f"Erro ao processar turma {turma.get('id', 'unknown')}: {e}")
            continue
    
    return {
        "total_pendentes": len(chamadas_pendentes),
        "chamadas_pendentes": chamadas_pendentes,
        "data_verificacao": hoje.isoformat()
    }

# 📊 DASHBOARD PERSONALIZADO POR USUÁRIO
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: UserResponse = Depends(get_current_user)):
    hoje = date.today()
    primeiro_mes = hoje.replace(day=1)
    
    if current_user.tipo == "admin":
        # 👑 ADMIN: Visão geral completa
        total_unidades = await db.unidades.count_documents({"ativo": True})
        total_cursos = await db.cursos.count_documents({"ativo": True})
        total_alunos = await db.alunos.count_documents({"ativo": True})
        total_turmas = await db.turmas.count_documents({"ativo": True})
        
        alunos_ativos = await db.alunos.count_documents({"status": "ativo"})
        alunos_desistentes = await db.alunos.count_documents({"status": "desistente"})
        chamadas_hoje = await db.chamadas.count_documents({"data": hoje.isoformat()})
        
        # Stats mensais
        chamadas_mes = await db.chamadas.find({"data": {"$gte": primeiro_mes.isoformat()}}).to_list(1000)
        total_presencas_mes = sum(c.get("total_presentes", 0) for c in chamadas_mes)
        total_faltas_mes = sum(c.get("total_faltas", 0) for c in chamadas_mes)
        
        return {
            "total_unidades": total_unidades,
            "total_cursos": total_cursos,
            "total_alunos": total_alunos,
            "total_turmas": total_turmas,
            "alunos_ativos": alunos_ativos,
            "alunos_desistentes": alunos_desistentes,
            "chamadas_hoje": chamadas_hoje,
            "presencas_mes": total_presencas_mes,
            "faltas_mes": total_faltas_mes,
            "taxa_presenca_mes": round((total_presencas_mes / (total_presencas_mes + total_faltas_mes) * 100) if (total_presencas_mes + total_faltas_mes) > 0 else 0, 1)
        }
    
    elif current_user.tipo == "instrutor":
        # 👨‍🏫 INSTRUTOR: Apenas suas turmas
        minhas_turmas = await db.turmas.find({"instrutor_id": current_user.id, "ativo": True}).to_list(1000)
        turmas_ids = [turma["id"] for turma in minhas_turmas]
        
        # Contar alunos únicos das suas turmas
        alunos_unicos = set()
        alunos_ativos = 0
        alunos_desistentes = 0
        
        for turma in minhas_turmas:
            for aluno_id in turma.get("alunos_ids", []):
                alunos_unicos.add(aluno_id)
                # Buscar status do aluno
                aluno = await db.alunos.find_one({"id": aluno_id})
                if aluno:
                    if aluno.get("status") == "ativo":
                        alunos_ativos += 1
                    elif aluno.get("status") == "desistente":
                        alunos_desistentes += 1
        
        # Chamadas do instrutor
        chamadas_hoje = await db.chamadas.count_documents({
            "turma_id": {"$in": turmas_ids},
            "data": hoje.isoformat()
        })
        
        # Stats mensais das suas turmas
        chamadas_mes = await db.chamadas.find({
            "turma_id": {"$in": turmas_ids},
            "data": {"$gte": primeiro_mes.isoformat()}
        }).to_list(1000)
        
        total_presencas_mes = sum(c.get("total_presentes", 0) for c in chamadas_mes)
        total_faltas_mes = sum(c.get("total_faltas", 0) for c in chamadas_mes)
        
        # Buscar dados do curso do instrutor
        curso_nome = "Seu Curso"
        unidade_nome = "Sua Unidade"
        
        if current_user.curso_id:
            curso = await db.cursos.find_one({"id": current_user.curso_id})
            if curso:
                curso_nome = curso.get("nome", "Seu Curso")
        
        if current_user.unidade_id:
            unidade = await db.unidades.find_one({"id": current_user.unidade_id})
            if unidade:
                unidade_nome = unidade.get("nome", "Sua Unidade")
        
        return {
            "total_unidades": 1,  # Sua unidade
            "total_cursos": 1,    # Seu curso
            "total_alunos": len(alunos_unicos),
            "total_turmas": len(minhas_turmas),
            "alunos_ativos": alunos_ativos,
            "alunos_desistentes": alunos_desistentes,
            "chamadas_hoje": chamadas_hoje,
            "presencas_mes": total_presencas_mes,
            "faltas_mes": total_faltas_mes,
            "taxa_presenca_mes": round((total_presencas_mes / (total_presencas_mes + total_faltas_mes) * 100) if (total_presencas_mes + total_faltas_mes) > 0 else 0, 1),
            "curso_nome": curso_nome,
            "unidade_nome": unidade_nome,
            "tipo_usuario": "Instrutor"
        }
    
    elif current_user.tipo in ["pedagogo", "monitor"]:
        # 👩‍🎓 PEDAGOGO/MONITOR: Turmas do seu curso/unidade
        query_turmas = {"ativo": True}
        if current_user.curso_id:
            query_turmas["curso_id"] = current_user.curso_id
        if current_user.unidade_id:
            query_turmas["unidade_id"] = current_user.unidade_id
        
        turmas_permitidas = await db.turmas.find(query_turmas).to_list(1000)
        turmas_ids = [turma["id"] for turma in turmas_permitidas]
        
        # Contar alunos únicos das turmas permitidas
        alunos_unicos = set()
        alunos_ativos = 0
        alunos_desistentes = 0
        
        for turma in turmas_permitidas:
            for aluno_id in turma.get("alunos_ids", []):
                alunos_unicos.add(aluno_id)
                aluno = await db.alunos.find_one({"id": aluno_id})
                if aluno:
                    if aluno.get("status") == "ativo":
                        alunos_ativos += 1
                    elif aluno.get("status") == "desistente":
                        alunos_desistentes += 1
        
        # Chamadas das turmas permitidas
        chamadas_hoje = await db.chamadas.count_documents({
            "turma_id": {"$in": turmas_ids},
            "data": hoje.isoformat()
        })
        
        # Stats mensais
        chamadas_mes = await db.chamadas.find({
            "turma_id": {"$in": turmas_ids},
            "data": {"$gte": primeiro_mes.isoformat()}
        }).to_list(1000)
        
        total_presencas_mes = sum(c.get("total_presentes", 0) for c in chamadas_mes)
        total_faltas_mes = sum(c.get("total_faltas", 0) for c in chamadas_mes)
        
        # Buscar dados do curso/unidade
        curso_nome = "Seu Curso"
        unidade_nome = "Sua Unidade"
        
        if current_user.curso_id:
            curso = await db.cursos.find_one({"id": current_user.curso_id})
            if curso:
                curso_nome = curso.get("nome", "Seu Curso")
        
        if current_user.unidade_id:
            unidade = await db.unidades.find_one({"id": current_user.unidade_id})
            if unidade:
                unidade_nome = unidade.get("nome", "Sua Unidade")
        
        return {
            "total_unidades": 1,  # Sua unidade
            "total_cursos": 1,    # Seu curso
            "total_alunos": len(alunos_unicos),
            "total_turmas": len(turmas_permitidas),
            "alunos_ativos": alunos_ativos,
            "alunos_desistentes": alunos_desistentes,
            "chamadas_hoje": chamadas_hoje,
            "presencas_mes": total_presencas_mes,
            "faltas_mes": total_faltas_mes,
            "taxa_presenca_mes": round((total_presencas_mes / (total_presencas_mes + total_faltas_mes) * 100) if (total_presencas_mes + total_faltas_mes) > 0 else 0, 1),
            "curso_nome": curso_nome,
            "unidade_nome": unidade_nome,
            "tipo_usuario": current_user.tipo.title()
        }

# MIGRAÇÃO DE DADOS - Corrigir alunos sem data_nascimento
@api_router.post("/migrate/fix-students")
async def fix_students_migration(current_user: UserResponse = Depends(get_current_user)):
    """🔧 MIGRAÇÃO: Adiciona data_nascimento padrão para alunos existentes"""
    check_admin_permission(current_user)
    
    try:
        # Buscar alunos sem data_nascimento
        alunos_sem_data = await db.alunos.find({
            "$or": [
                {"data_nascimento": {"$exists": False}},
                {"data_nascimento": None}
            ]
        }).to_list(1000)
        
        if not alunos_sem_data:
            return {"message": "Todos os alunos já possuem data_nascimento", "migrated": 0}
        
        # Atualizar com data padrão (1 de janeiro de 2000)
        data_padrao = date(2000, 1, 1)
        migrated_count = 0
        
        for aluno in alunos_sem_data:
            await db.alunos.update_one(
                {"id": aluno["id"]},
                {"$set": {"data_nascimento": data_padrao.isoformat()}}
            )
            migrated_count += 1
        
        return {
            "message": f"Migração concluída! {migrated_count} alunos atualizados",
            "migrated": migrated_count,
            "data_padrao_usada": data_padrao.isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na migração: {str(e)}")

# INITIALIZE SYSTEM
@api_router.post("/init")
async def initialize_system():
    # Create default admin user
    admin_exists = await db.usuarios.find_one({"tipo": "admin"})
    if not admin_exists:
        admin_user = User(
            nome="Administrador",
            email="admin@ios.com.br",
            senha=bcrypt.hash("admin123"),
            tipo="admin",
            status="ativo",
            primeiro_acesso=False
        )
        await db.usuarios.insert_one(admin_user.dict())
    else:
        # Update existing admin user with missing fields
        await db.usuarios.update_one(
            {"email": "admin@ios.com.br"},
            {"$set": {"status": "ativo", "primeiro_acesso": False}}
        )
    
    # Create sample data for testing
    await create_sample_data()
    
    return {"message": "Sistema inicializado com dados de teste"}

async def create_sample_data():
    # Create sample unidades
    unidade1_id = str(uuid.uuid4())
    unidade2_id = str(uuid.uuid4())
    
    unidades_sample = [
        {"id": unidade1_id, "nome": "Unidade Centro", "endereco": "Rua Central, 123", "telefone": "(11) 1234-5678", "ativo": True, "created_at": datetime.now(timezone.utc)},
        {"id": unidade2_id, "nome": "Unidade Norte", "endereco": "Av. Norte, 456", "telefone": "(11) 8765-4321", "ativo": True, "created_at": datetime.now(timezone.utc)}
    ]
    
    for unidade in unidades_sample:
        existing = await db.unidades.find_one({"nome": unidade["nome"]})
        if not existing:
            await db.unidades.insert_one(unidade)
    
    # Create sample cursos
    curso1_id = str(uuid.uuid4())
    curso2_id = str(uuid.uuid4())
    
    cursos_sample = [
        {"id": curso1_id, "nome": "Informática Básica", "descricao": "Curso de informática para iniciantes", "carga_horaria": 80, "categoria": "Tecnologia", "ativo": True, "created_at": datetime.now(timezone.utc)},
        {"id": curso2_id, "nome": "Administração", "descricao": "Curso de administração empresarial", "carga_horaria": 120, "categoria": "Gestão", "ativo": True, "created_at": datetime.now(timezone.utc)}
    ]
    
    for curso in cursos_sample:
        existing = await db.cursos.find_one({"nome": curso["nome"]})
        if not existing:
            await db.cursos.insert_one(curso)
    
    # Create sample instructor
    instrutor_id = str(uuid.uuid4())
    instrutor_exists = await db.usuarios.find_one({"email": "instrutor@ios.com.br"})
    if not instrutor_exists:
        instrutor = User(
            id=instrutor_id,
            nome="Professor Silva",
            email="instrutor@ios.com.br",
            senha=bcrypt.hash("instrutor123"),
            tipo="instrutor",
            unidade_id=unidade1_id,
            curso_id=curso1_id,  # Associado ao curso de Informática Básica
            primeiro_acesso=False
        )
        await db.usuarios.insert_one(instrutor.dict())
    else:
        instrutor_id = instrutor_exists["id"]
        # Atualizar instrutor existente com curso_id se não tiver
        await db.usuarios.update_one(
            {"email": "instrutor@ios.com.br"},
            {"$set": {"curso_id": curso1_id, "unidade_id": unidade1_id}}
        )
    
    # Create sample alunos (30 alunos for each turma)
    alunos_ids = []
    for i in range(60):  # 60 alunos total para 2 turmas de 30 cada
        aluno_id = str(uuid.uuid4())
        aluno = {
            "id": aluno_id,
            "nome": f"Aluno {i+1:02d}",
            "cpf": f"{100000000+i:011d}",
            "telefone": f"(11) 9{1000+i:04d}-{1000+i:04d}",
            "email": f"aluno{i+1:02d}@email.com",
            "ativo": True,
            "status": "ativo",
            "created_at": datetime.now(timezone.utc)
        }
        
        existing = await db.alunos.find_one({"cpf": aluno["cpf"]})
        if not existing:
            await db.alunos.insert_one(aluno)
            alunos_ids.append(aluno_id)
    
    # Create sample turmas
    turma1_id = str(uuid.uuid4())
    turma2_id = str(uuid.uuid4())
    
    turmas_sample = [
        {
            "id": turma1_id,
            "nome": "Informática Turma A",
            "unidade_id": unidade1_id,
            "curso_id": curso1_id,
            "instrutor_id": instrutor_id,
            "alunos_ids": alunos_ids[:30],
            "data_inicio": date.today().isoformat(),
            "data_fim": (date.today() + timedelta(days=90)).isoformat(),
            "horario_inicio": "08:00",
            "horario_fim": "12:00",
            "dias_semana": ["segunda", "terca", "quarta", "quinta", "sexta"],
            "vagas_total": 30,
            "vagas_ocupadas": 30,
            "ciclo": "01/2025",
            "ativo": True,
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": turma2_id,
            "nome": "Administração Turma B",
            "unidade_id": unidade2_id,
            "curso_id": curso2_id,
            "instrutor_id": instrutor_id,
            "alunos_ids": alunos_ids[30:60],
            "data_inicio": date.today().isoformat(),
            "data_fim": (date.today() + timedelta(days=120)).isoformat(),
            "horario_inicio": "14:00",
            "horario_fim": "18:00",
            "dias_semana": ["segunda", "terca", "quarta", "quinta", "sexta"],
            "vagas_total": 30,
            "vagas_ocupadas": 30,
            "ciclo": "01/2025",
            "ativo": True,
            "created_at": datetime.now(timezone.utc)
        }
    ]
    
    for turma in turmas_sample:
        existing = await db.turmas.find_one({"nome": turma["nome"]})
        if not existing:
            await db.turmas.insert_one(turma)

# RELATÓRIOS DINÂMICOS - ENDPOINT COMPLETO
@api_router.get("/reports/teacher-stats")
async def get_dynamic_teacher_stats(
    unidade_id: Optional[str] = None,
    curso_id: Optional[str] = None,
    turma_id: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    """📊 RELATÓRIOS DINÂMICOS: Estatísticas completas e atualizadas automaticamente com filtros para admin"""
    if current_user.tipo not in ["instrutor", "pedagogo", "monitor", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso restrito")
    
    # 🎯 Filtrar turmas baseado no tipo de usuário e filtros
    query_turmas = {"ativo": True}
    
    if current_user.tipo == "admin":
        # Admin pode usar filtros
        if unidade_id:
            query_turmas["unidade_id"] = unidade_id
        if curso_id:
            query_turmas["curso_id"] = curso_id
        if turma_id:
            query_turmas["id"] = turma_id
    elif current_user.tipo == "instrutor":
        query_turmas["instrutor_id"] = current_user.id
    elif current_user.tipo in ["pedagogo", "monitor"]:
        if current_user.curso_id:
            query_turmas["curso_id"] = current_user.curso_id
        if current_user.unidade_id:
            query_turmas["unidade_id"] = current_user.unidade_id
    
    # 📈 Buscar turmas do usuário
    turmas = await db.turmas.find(query_turmas).to_list(1000)
    turma_ids = [turma["id"] for turma in turmas]
    
    if not turma_ids:
        return {
            "taxa_media_presenca": 0,
            "total_alunos": 0,
            "alunos_em_risco": 0,
            "desistentes": 0,
            "maiores_presencas": [],
            "maiores_faltas": [],
            "resumo_turmas": []
        }
    
    # 📊 Calcular estatísticas dinâmicas por aluno
    alunos_stats = []
    for turma in turmas:
        aluno_ids = turma.get("alunos_ids", [])
        if not aluno_ids:
            continue
            
        # Buscar alunos da turma
        alunos = await db.alunos.find({"id": {"$in": aluno_ids}}).to_list(1000)
        
        for aluno in alunos:
            # Contar presenças e faltas do aluno nesta turma com filtro de data
            query_chamadas = {"turma_id": turma["id"]}
            
            # Aplicar filtro de data se fornecido
            if data_inicio and data_fim:
                query_chamadas["data"] = {"$gte": data_inicio.isoformat(), "$lte": data_fim.isoformat()}
            elif data_inicio:
                query_chamadas["data"] = {"$gte": data_inicio.isoformat()}
            elif data_fim:
                query_chamadas["data"] = {"$lte": data_fim.isoformat()}
            
            chamadas = await db.chamadas.find(query_chamadas).to_list(1000)
            
            total_aulas = len(chamadas)
            presencas = 0
            faltas = 0
            
            for chamada in chamadas:
                presencas_dict = chamada.get("presencas", {})
                if aluno["id"] in presencas_dict:
                    if presencas_dict[aluno["id"]].get("presente", False):
                        presencas += 1
                    else:
                        faltas += 1
            
            if total_aulas > 0:
                taxa_presenca = (presencas / total_aulas) * 100
            else:
                taxa_presenca = 0
            
            alunos_stats.append({
                "id": aluno["id"],
                "nome": aluno["nome"],
                "turma": turma["nome"],
                "presencas": presencas,
                "faltas": faltas,
                "total_aulas": total_aulas,
                "taxa_presenca": round(taxa_presenca, 1),
                "status": aluno.get("status", "ativo")
            })
    
    # 📊 Calcular métricas gerais
    if alunos_stats:
        taxa_media = sum(a["taxa_presenca"] for a in alunos_stats) / len(alunos_stats)
        alunos_em_risco = [a for a in alunos_stats if a["taxa_presenca"] < 75]
        desistentes = [a for a in alunos_stats if a["status"] == "desistente"]
        
        # Top 3 maiores presenças
        maiores_presencas = sorted(alunos_stats, key=lambda x: x["taxa_presenca"], reverse=True)[:3]
        
        # Top 3 maiores faltas
        maiores_faltas = sorted(alunos_stats, key=lambda x: x["taxa_presenca"])[:3]
    else:
        taxa_media = 0
        alunos_em_risco = []
        desistentes = []
        maiores_presencas = []
        maiores_faltas = []
    
    # 📋 Resumo por turma
    resumo_turmas = []
    for turma in turmas:
        turma_alunos = [a for a in alunos_stats if a["turma"] == turma["nome"]]
        if turma_alunos:
            media_turma = sum(a["taxa_presenca"] for a in turma_alunos) / len(turma_alunos)
        else:
            media_turma = 0
            
        resumo_turmas.append({
            "nome": turma["nome"],
            "total_alunos": len(turma_alunos),
            "taxa_media": round(media_turma, 1),
            "alunos_risco": len([a for a in turma_alunos if a["taxa_presenca"] < 75])
        })
    
    return {
        "taxa_media_presenca": f"{round(taxa_media, 1)}%",
        "total_alunos": len(alunos_stats),
        "alunos_em_risco": len(alunos_em_risco),
        "desistentes": len(desistentes),
        "maiores_presencas": [
            {
                "nome": a["nome"],
                "turma": a["turma"],
                "taxa_presenca": f"{a['taxa_presenca']}%",
                "aulas_presentes": f"{a['presencas']}/{a['total_aulas']} aulas"
            } for a in maiores_presencas
        ],
        "maiores_faltas": [
            {
                "nome": a["nome"],
                "turma": a["turma"],
                "taxa_presenca": f"{a['taxa_presenca']}%",
                "faltas": f"{a['faltas']}/{a['total_aulas']} faltas"
            } for a in maiores_faltas
        ],
        "resumo_turmas": resumo_turmas
    }

# TEACHER STATS ENDPOINT (MANTER COMPATIBILIDADE)
@api_router.get("/teacher/stats")
async def get_teacher_stats(current_user: UserResponse = Depends(get_current_user)):
    """Retorna estatísticas para professores/instrutores/monitores (compatibilidade)"""
    if current_user.tipo not in ["instrutor", "admin", "monitor"]:
        raise HTTPException(status_code=403, detail="Acesso restrito a instrutores e monitores")
    
    # Lógica adaptada para instrutor e monitor
    if current_user.tipo == "instrutor":
        # Instrutor: turmas que ele leciona
        query_turmas = {"instrutor_id": current_user.id, "ativo": True}
    elif current_user.tipo == "monitor":
        # Monitor: turmas que ele monitora
        query_turmas = {"monitor_id": current_user.id, "ativo": True}
    else:
        # Admin: todas as turmas (ou lógica específica se necessário)
        query_turmas = {"ativo": True}
    
    # Count turmas
    turmas_count = await db.turmas.count_documents(query_turmas)
    
    # Count alunos nas turmas
    turmas = await db.turmas.find(query_turmas).to_list(100)
    turma_ids = [turma["id"] for turma in turmas]
    
    total_alunos = 0
    for turma in turmas:
        total_alunos += len(turma.get("alunos_ids", []))
    
    # Count presenças registradas hoje
    hoje = datetime.now().date()
    presencas_hoje = await db.chamadas.count_documents({
        "turma_id": {"$in": turma_ids},
        "data": hoje.isoformat()
    })
    
    return {
        "total_turmas": turmas_count,
        "total_alunos": total_alunos,
        "presencas_hoje": presencas_hoje,
        "nome_instrutor": current_user.nome
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[
        "http://localhost:3000",  # Desenvolvimento local
        "https://front-end-sistema-qbl0lhxig-jesielamarojunior-makers-projects.vercel.app",  # Vercel deployment
        "https://front-end-sistema.vercel.app",  # Vercel custom domain
        "https://sistema-ios-frontend.vercel.app",  # Possível domínio personalizado
        "*"  # Fallback para desenvolvimento
    ],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# Railway compatibility - run server if executed directly
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)