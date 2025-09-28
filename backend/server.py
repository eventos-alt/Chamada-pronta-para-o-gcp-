from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Query
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
    "https://*.vercel.app",
    "https://*.railway.app",
    "https://seu-frontend.vercel.app"
]

# Para produção, usar variável de ambiente
if os.environ.get("RAILWAY_ENVIRONMENT"):
    origins.append("*")  # Railway permite qualquer origem em produção

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return {"message": "Backend funcionando!"}

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
    ativo: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CursoCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    carga_horaria: int
    categoria: Optional[str] = None
    pre_requisitos: Optional[str] = None

class CursoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    carga_horaria: Optional[int] = None
    categoria: Optional[str] = None
    pre_requisitos: Optional[str] = None

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
    ciclo: str  # "01/2025", "02/2025"
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
    ciclo: str

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
    turma_id: str
    data_desistencia: date
    motivo: str
    observacoes: Optional[str] = None
    registrado_por: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DesistenteCreate(BaseModel):
    aluno_id: str
    turma_id: str
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
    
    # Log da criação para auditoria
    await log_admin_action(
        admin_id=current_user.id,
        action="create_user",
        details=f"Criado usuário {user_create.tipo}: {user_create.nome} ({user_create.email})" + 
                (f" - Unidade: {user_create.unidade_id}, Curso: {user_create.curso_id}" if user_create.tipo != "admin" else ""),
        temp_password=temp_password
    )
    
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
    check_admin_permission(current_user)
    
    # Check if CPF already exists
    existing_aluno = await db.alunos.find_one({"cpf": aluno_create.cpf})
    if existing_aluno:
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    
    aluno_dict = prepare_for_mongo(aluno_create.dict())
    aluno_obj = Aluno(**aluno_dict)
    
    mongo_data = prepare_for_mongo(aluno_obj.dict())
    await db.alunos.insert_one(mongo_data)
    return aluno_obj

@api_router.get("/students", response_model=List[Aluno])
async def get_alunos(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user)
):
    query = {"ativo": True}
    if status:
        query["status"] = status
        
    alunos = await db.alunos.find(query).skip(skip).limit(limit).to_list(limit)
    return [Aluno(**parse_from_mongo(aluno)) for aluno in alunos]

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
        turmas = await db.turmas.find({"ativo": True}).to_list(1000)
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
    
    return [Turma(**parse_from_mongo(turma)) for turma in turmas]

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
    
    # Calculate totals
    total_presentes = sum(1 for p in chamada_create.presencas.values() if p.get("presente", False))
    total_faltas = len(chamada_create.presencas) - total_presentes
    
    chamada_dict = prepare_for_mongo(chamada_create.dict())
    chamada_dict.update({
        "instrutor_id": current_user.id,
        "total_presentes": total_presentes,
        "total_faltas": total_faltas
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
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    export_csv: bool = False,
    current_user: UserResponse = Depends(get_current_user)
):
    query = {}
    if turma_id:
        query["turma_id"] = turma_id
    if data_inicio and data_fim:
        query["data"] = {"$gte": data_inicio.isoformat(), "$lte": data_fim.isoformat()}
    
    chamadas = await db.chamadas.find(query).to_list(1000)
    
    if export_csv:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Data", "Turma", "Total Presentes", "Total Faltas", "Observações"])
        
        for chamada in chamadas:
            writer.writerow([
                chamada.get("data", ""),
                chamada.get("turma_id", ""),
                chamada.get("total_presentes", 0),
                chamada.get("total_faltas", 0),
                chamada.get("observacoes_aula", "")
            ])
        
        output.seek(0)
        return {"csv_data": output.getvalue()}
    
    return [parse_from_mongo(chamada) for chamada in chamadas]

# DASHBOARD STATS
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: UserResponse = Depends(get_current_user)):
    # Basic counts
    total_unidades = await db.unidades.count_documents({"ativo": True})
    total_cursos = await db.cursos.count_documents({"ativo": True})
    total_alunos = await db.alunos.count_documents({"ativo": True})
    total_turmas = await db.turmas.count_documents({"ativo": True})
    
    # Advanced stats
    alunos_ativos = await db.alunos.count_documents({"status": "ativo"})
    alunos_desistentes = await db.alunos.count_documents({"status": "desistente"})
    
    # Recent activity
    hoje = date.today()
    chamadas_hoje = await db.chamadas.count_documents({"data": hoje.isoformat()})
    
    # Attendance stats for current month
    primeiro_mes = hoje.replace(day=1)
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
async def get_dynamic_teacher_stats(current_user: UserResponse = Depends(get_current_user)):
    """📊 RELATÓRIOS DINÂMICOS: Estatísticas completas e atualizadas automaticamente"""
    if current_user.tipo not in ["instrutor", "pedagogo", "monitor", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso restrito")
    
    # 🎯 Filtrar turmas baseado no tipo de usuário
    query_turmas = {"ativo": True}
    if current_user.tipo == "instrutor":
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
            # Contar presenças e faltas do aluno nesta turma
            chamadas = await db.chamadas.find({"turma_id": turma["id"]}).to_list(1000)
            
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
    """Retorna estatísticas para professores/instrutores (compatibilidade)"""
    if current_user.tipo not in ["instrutor", "admin"]:
        raise HTTPException(status_code=403, detail="Acesso restrito a instrutores")
    
    # Count turmas do instrutor
    turmas_count = await db.turmas.count_documents({
        "instrutor_id": current_user.id,
        "ativo": True
    })
    
    # Count alunos nas suas turmas
    turmas = await db.turmas.find({"instrutor_id": current_user.id, "ativo": True}).to_list(100)
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