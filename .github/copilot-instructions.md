# Sistema de Controle de Presença - IOS

## Arquitetura do Projeto

Este é um sistema full-stack de controle de presença com backend FastAPI e frontend React:

- **Backend**: FastAPI + MongoDB (Motor driver assíncrono) + JWT auth
- **Frontend**: Create React App + shadcn/ui + Tailwind CSS + React Router
- **Banco**: MongoDB com collections: users, units, courses, students, classes, attendances
- **Deploy**: Backend no Render, Frontend no Vercel (ONLINE desde 27/09/2025)

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

#### Backend Models - ATUALIZADO 28/09/2025

```python
# Pattern: Base model + Create/Update variants
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    unidade_id: Optional[str] = None  # Para instrutor/pedagogo/monitor
    curso_id: Optional[str] = None    # NOVO: Obrigatório para não-admin
    # ... outros campos

class UserCreate(BaseModel):
    # Campos obrigatórios na criação
    unidade_id: Optional[str] = None
    curso_id: Optional[str] = None  # NOVO: Validado se tipo != admin

class UserResponse(BaseModel):
    # Campos seguros para retorno (sem senha)
    unidade_id: Optional[str] = None
    curso_id: Optional[str] = None  # NOVO: Retorna associação do curso
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

## Tipos de Usuário e Permissões - ATUALIZADO 28/09/2025

Sistema com 4 tipos de usuário com controle granular por curso:

- `admin`: Acesso total (pode gerenciar qualquer curso/unidade)
- `instrutor`: Gerencia turmas/presenças **APENAS do seu curso específico**
- `pedagogo`: Visualiza relatórios **APENAS do seu curso específico**
- `monitor`: Auxilia em turmas **APENAS do seu curso específico**

**Regras de Associação Curso-Usuário:**

- **Obrigatório**: instrutor/pedagogo/monitor devem ter `unidade_id` + `curso_id`
- **Validação**: Sistema verifica existência do curso e unidade na criação
- **Permissões**: Usuários só acessam dados do seu curso/unidade
- **Admin**: Único tipo sem restrições de curso

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
# Senha temporária retornada na resposta para admin informar pessoalmente

# Reset de senha (admin) - ATUALIZADO 27/09/2025
/api/users/{user_id}/reset-password # Admin reseta senha de qualquer usuário
# Frontend: Botão com ícone de chave no painel de usuários
# Popup seguro mostra senha temporária apenas para admin

# Reset de senha comum
/api/auth/reset-password # Usuário solicita reset (não expõe se email existe)
# Melhor segurança: não mostra informações sensíveis na tela

# Primeiro acesso
/api/auth/first-access # Usuário define senha permanente

# Alteração de senha
/api/auth/change-password # Usuário logado altera própria senha
```

## Pontos de Integração

### Database Schema - ATUALIZADO 28/09/2025 - SISTEMA COMPLETO IMPLEMENTADO

```python
# Collections principais com VALIDAÇÕES RIGOROSAS implementadas:
users: {id, nome, email, tipo, unidade_id, curso_id, ...}  # CURSO_ID OBRIGATÓRIO para instrutor/pedagogo/monitor
units: {id, nome, endereco, responsavel, ...}
courses: {id, nome, carga_horaria, categoria, ...}
students: {id, nome, cpf, data_nascimento, ...}  # ✅ CAMPOS OBRIGATÓRIOS: nome completo + CPF + data nascimento
classes: {id, curso_id, unidade_id, instrutor_id, alunos_ids[], ...}
attendances: {id, turma_id, data, presencas{}, instrutor_id, ...}  # ✅ VALIDAÇÃO DE DATA implementada
```

### 🎯 **SISTEMA COMPLETO FUNCIONANDO - 29/09/2025**

**🚀 ÚLTIMA ATUALIZAÇÃO: Funcionalidades de Download, Desistentes e Atestados Médicos**

**Status do Deploy:**

- ✅ Frontend: Build compilado com sucesso (148.1 kB)
- ✅ Backend: Importação e validação sem erros
- ✅ Integração: Sistema completo funcional
- ✅ Git: Código versionado e documentado (commit 2d94322)

**✅ IMPLEMENTAÇÕES CRÍTICAS FINALIZADAS:**

#### **0. Sistema de Permissões para Gerenciamento de Alunos - COMPLETO 28/09/2025**

```javascript
// Frontend: Interface contextual baseada no tipo de usuário
const AlunosManager = () => {
  const { user } = useAuth();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Gerenciamento de Alunos</CardTitle>
        <CardDescription>
          {user?.tipo === "admin"
            ? "Gerencie todos os alunos cadastrados no sistema"
            : `Gerencie alunos das suas turmas (${
                user?.curso_nome || "seu curso"
              })`}
        </CardDescription>
      </CardHeader>

      {/* Card de permissões para não-admin */}
      {user?.tipo !== "admin" && (
        <div className="mx-6 mb-4 p-4 bg-orange-50 border border-orange-200 rounded-lg">
          <div className="flex items-center gap-2 text-orange-800">
            <Info className="h-4 w-4" />
            <span className="text-sm font-medium">Suas Permissões:</span>
          </div>
          <div className="mt-2 text-sm text-orange-700">
            <p>
              • <strong>Tipo:</strong> Instrutor/Pedagogo/Monitor
            </p>
            <p>
              • <strong>Unidade:</strong> Nome da Unidade
            </p>
            <p>
              • <strong>Curso:</strong> Nome do Curso
            </p>
            <p>
              • <strong>Permissão:</strong> Criar e gerenciar alunos apenas das
              suas turmas
            </p>
          </div>
        </div>
      )}
    </Card>
  );
};

// ✅ Backend: Permissões granulares implementadas
// ✅ Frontend: Interface contextual e responsiva
// ✅ UX: Feedback claro sobre escopo de permissões
// ✅ Integração: Sistema completo funcionando
```

#### **1. Sistema de Cadastro de Alunos Robusto**

```python
# Backend: Campos obrigatórios implementados
class AlunoCreate(BaseModel):
    nome: str  # OBRIGATÓRIO - Nome completo (não aceita mais "Aluno 1")
    cpf: str   # OBRIGATÓRIO - CPF válido
    data_nascimento: date  # OBRIGATÓRIO - Data de nascimento

# Frontend: Formulário reorganizado com campos obrigatórios em destaque
- Nome Completo (primeiro campo, obrigatório)
- Data de Nascimento (segundo campo, obrigatório)
- CPF (terceiro campo, obrigatório)
- Campos complementares agrupados abaixo
```

#### **2. Sistema de Chamada com Validação de Data**

```python
# Backend: Validações rigorosas implementadas
@api_router.post("/attendance")
async def create_chamada(chamada_create: ChamadaCreate, current_user):
    # ✅ VALIDAÇÃO: Só permite chamada do dia atual
    if chamada_create.data != date.today():
        raise HTTPException(400, "Só é possível fazer chamada da data atual")

    # ✅ VALIDAÇÃO: Bloqueia múltiplas chamadas no mesmo dia
    chamada_existente = await db.chamadas.find_one({
        "turma_id": chamada_create.turma_id,
        "data": date.today().isoformat()
    })
    if chamada_existente:
        raise HTTPException(400, "Chamada já foi realizada hoje")

# Frontend: Comportamento inteligente
- Remove turma da lista após chamada feita
- Não permite chamada repetida no mesmo dia
- Feedback claro: "Já foi feita chamada hoje para esta turma"
```

#### **3. Relatórios Dinâmicos e Auto-Atualizados**

```python
# Backend: Novo endpoint completo
@api_router.get("/reports/teacher-stats")
async def get_dynamic_teacher_stats(current_user):
    """📊 RELATÓRIOS DINÂMICOS: Cálculos em tempo real"""
    # ✅ Cálculo automático de presenças/faltas por aluno
    # ✅ Top 3 maiores presenças e faltas dinâmicos
    # ✅ Resumo por turma com métricas reais
    # ✅ Filtros automáticos por tipo de usuário e curso

    return {
        "taxa_media_presenca": f"{taxa_media}%",
        "total_alunos": len(alunos_stats),
        "alunos_em_risco": len(alunos_risco),
        "maiores_presencas": [...],  # Dados reais do banco
        "maiores_faltas": [...],     # Dados reais do banco
        "resumo_turmas": [...]       # Métricas por turma
    }

# Frontend: Auto-refresh implementado
useEffect(() => {
    fetchDynamicStats();
    // 🔄 AUTO-REFRESH: Atualizar a cada 30 segundos
    const interval = setInterval(fetchDynamicStats, 30000);
    return () => clearInterval(interval);
}, [user]);
```

#### **4. Gerenciamento de Alunos Funcional**

```javascript
// Frontend: API calls corretas implementadas
const handleAddAlunoToTurma = async (alunoId) => {
    await axios.put(`${API}/classes/${selectedTurmaForAlunos.id}/students/${alunoId}`);
    fetchData(); // ✅ Atualização automática
};

const handleRemoveAlunoFromTurma = async (alunoId) => {
    await axios.delete(`${API}/classes/${selectedTurmaForAlunos.id}/students/${alunoId}`);
    fetchData(); // ✅ Atualização automática
};

// Backend: Permissões granulares implementadas
- Admin: pode gerenciar qualquer turma
- Instrutor: só suas próprias turmas
- Pedagogo/Monitor: apenas turmas do seu curso/unidade
```

**Associação Curso-Usuário Implementada:**

- `instrutor`: Associado a 1 curso específico + 1 unidade (só pode criar turmas desse curso)
- `pedagogo`: Associado a 1 curso específico + 1 unidade (vê turmas do curso)
- `monitor`: Associado a 1 curso específico + 1 unidade (auxilia no curso)
- `admin`: Sem restrições de curso (acesso total)

**🎯 Fluxo Completo de Permissões para Gerenciamento de Alunos - IMPLEMENTADO 28/09/2025:**

```javascript
// 1. Login do usuário → Sistema identifica tipo e curso/unidade
// 2. Acesso à aba "Alunos" → Interface mostra contexto específico
// 3. Card de permissões → Usuário vê claramente seu escopo
// 4. Criação de aluno → Backend valida permissões automaticamente
// 5. Listagem → Apenas alunos das turmas permitidas aparecem

// ✅ Para Admin: Acesso total a todos os alunos
// ✅ Para Instrutor: Apenas alunos das suas turmas
// ✅ Para Pedagogo: Apenas alunos do seu curso/unidade
// ✅ Para Monitor: Apenas alunos do seu curso/unidade
```

### 🔧 **CORREÇÕES CRÍTICAS DE PRODUÇÃO - 28/09/2025**

#### **1. CORS Policy Error - RESOLVIDO**

```python
# Backend: Configuração CORS para Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Desenvolvimento
        "https://front-end-sistema-qbl0lhxig-jesielamarojunior-makers-projects.vercel.app",
        "https://front-end-sistema.vercel.app",
        "https://sistema-ios-frontend.vercel.app"
    ],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ❌ Erro antes: Access-Control-Allow-Origin header not present
# ✅ Agora: Frontend Vercel acessa backend Render sem problemas
```

#### **4. Interface Contextual para Permissões - IMPLEMENTADO 28/09/2025**

```javascript
// Frontend: Card de permissões contextual para não-admin
{
  user?.tipo !== "admin" && (
    <div className="mx-6 mb-4 p-4 bg-orange-50 border border-orange-200 rounded-lg">
      <div className="flex items-center gap-2 text-orange-800">
        <Info className="h-4 w-4" />
        <span className="text-sm font-medium">Suas Permissões:</span>
      </div>
      <div className="mt-2 text-sm text-orange-700">
        <p>
          • <strong>Tipo:</strong>{" "}
          {user.tipo?.charAt(0).toUpperCase() + user.tipo?.slice(1)}
        </p>
        <p>
          • <strong>Unidade:</strong> {user?.unidade_nome || "Sua unidade"}
        </p>
        <p>
          • <strong>Curso:</strong> {user?.curso_nome || "Seu curso"}
        </p>
        <p>
          • <strong>Permissão:</strong> Criar e gerenciar alunos apenas das suas
          turmas
        </p>
      </div>
    </div>
  );
}

// ✅ Resultado: Interface contextual mostra escopo de permissões
// ✅ Design: Cores IOS (laranja/branco) para feedback visual
// ✅ UX: Usuários compreendem suas limitações e capacidades
```

### 🚀 **NOVAS FUNCIONALIDADES IMPLEMENTADAS - 29/09/2025**

**🎯 IMPLEMENTAÇÕES CRÍTICAS FINALIZADAS:**

#### **1. Sistema de Download de Relatórios CSV - COMPLETO 29/09/2025**

```javascript
// Frontend: Função de download implementada
const downloadFrequencyReport = async () => {
  try {
    const response = await axios.get(
      `${API}/reports/attendance?export_csv=true`,
      {
        responseType: "blob",
      }
    );

    // Criar blob e download automático
    const blob = new Blob([response.data], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;

    // Nome do arquivo com data
    const today = new Date().toISOString().split("T")[0];
    link.download = `relatorio_frequencia_${today}.csv`;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    toast({ title: "Sucesso", description: "Relatório baixado com sucesso!" });
  } catch (error) {
    toast({
      title: "Erro",
      description: "Erro ao baixar relatório",
      variant: "destructive",
    });
  }
};

// ✅ Funcionalidades Implementadas:
// ✅ Botão de exportação CSV nos relatórios dinâmicos
// ✅ Download automático com nome baseado na data
// ✅ Tratamento de erros e feedback visual
// ✅ Integração com endpoint existente /reports/attendance?export_csv=true
```

#### **2. Sistema de Registro de Desistentes - COMPLETO 29/09/2025**

```javascript
// Frontend: Gerenciamento de desistências implementado
const [dropoutDialog, setDropoutDialog] = useState(false);
const [dropoutStudent, setDropoutStudent] = useState(null);
const [dropoutReason, setDropoutReason] = useState("");

const handleMarkAsDropout = (aluno) => {
  setDropoutStudent(aluno);
  setDropoutDialog(true);
};

const submitDropout = async () => {
  try {
    await axios.post(`${API}/dropouts`, {
      aluno_id: dropoutStudent.id,
      motivo: dropoutReason,
      data_desistencia: new Date().toISOString().split("T")[0],
    });

    // Atualizar status do aluno
    await axios.put(`${API}/students/${dropoutStudent.id}`, {
      ...dropoutStudent,
      status: "desistente",
    });

    toast({
      title: "Sucesso",
      description: "Desistência registrada com sucesso!",
    });
    setDropoutDialog(false);
    setDropoutReason("");
    fetchData(); // Atualizar lista
  } catch (error) {
    toast({
      title: "Erro",
      description: "Erro ao registrar desistência",
      variant: "destructive",
    });
  }
};

// ✅ Funcionalidades Implementadas:
// ✅ Botão "Registrar Desistência" na tabela de alunos
// ✅ Dialog modal para inserir motivo obrigatório
// ✅ Atualização automática do status para 'desistente'
// ✅ Integração com endpoint /dropouts do backend
// ✅ Validação de campos e feedback visual
```

#### **3. Sistema de Upload de Atestados Médicos - COMPLETO 29/09/2025**

```javascript
// Frontend: Upload de atestados implementado
const [certificateDialog, setCertificateDialog] = useState(false);
const [certificateStudent, setCertificateStudent] = useState(null);
const [certificateFile, setCertificateFile] = useState(null);

const handleUploadCertificate = (aluno) => {
  setCertificateStudent(aluno);
  setCertificateDialog(true);
};

const submitCertificate = async () => {
  if (!certificateFile) {
    toast({
      title: "Erro",
      description: "Selecione um arquivo",
      variant: "destructive",
    });
    return;
  }

  try {
    const formData = new FormData();
    formData.append("file", certificateFile);
    formData.append("aluno_id", certificateStudent.id);
    formData.append("tipo", "atestado_medico");

    await axios.post(`${API}/upload/atestado`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    toast({ title: "Sucesso", description: "Atestado enviado com sucesso!" });
    setCertificateDialog(false);
    setCertificateFile(null);
    fetchData();
  } catch (error) {
    toast({
      title: "Erro",
      description: "Erro ao enviar atestado",
      variant: "destructive",
    });
  }
};

// ✅ Funcionalidades Implementadas:
// ✅ Upload de atestado na tabela de alunos
// ✅ Upload durante a chamada com integração automática
// ✅ Validação de tipos de arquivo (PDF, JPG, PNG)
// ✅ Justificativa automática: "Falta justificada com atestado médico"
// ✅ Estados específicos para gerenciar uploads
```

#### **4. Integração na Chamada com Atestados - COMPLETO 29/09/2025**

```javascript
// Frontend: Upload de atestado durante a chamada
const [attestUploadDialog, setAttestUploadDialog] = useState(false);
const [attestStudent, setAttestStudent] = useState(null);
const [attestFile, setAttestFile] = useState(null);

const handleAttestUpload = (aluno) => {
  setAttestStudent(aluno);
  setAttestUploadDialog(true);
};

const submitAttestUpload = async () => {
  try {
    // Upload do arquivo
    const formData = new FormData();
    formData.append("file", attestFile);
    formData.append("aluno_id", attestStudent.id);
    formData.append("tipo", "atestado_medico");

    const uploadResponse = await axios.post(
      `${API}/upload/atestado`,
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
      }
    );

    // Atualizar presença com atestado
    const updatedPresencas = {
      ...presencas,
      [attestStudent.id]: {
        presente: false,
        justificativa: "Falta justificada com atestado médico",
        atestado_id: uploadResponse.data.id,
      },
    };

    setPresencas(updatedPresencas);
    toast({
      title: "Sucesso",
      description: "Atestado enviado e falta justificada!",
    });
    setAttestUploadDialog(false);
    setAttestFile(null);
  } catch (error) {
    toast({
      title: "Erro",
      description: "Erro ao enviar atestado",
      variant: "destructive",
    });
  }
};

// ✅ Funcionalidades Implementadas:
// ✅ Botão funcional de upload durante a chamada
// ✅ Justificativa automática ao fazer upload
// ✅ Integração do atestado_id na presença
// ✅ Estados específicos para upload na chamada
// ✅ Feedback visual consistente com sistema
```

#### **5. Melhorias na Interface e UX - COMPLETO 29/09/2025**

```javascript
// Botões contextuais implementados nas tabelas
{
  /* Botão Download nos Relatórios */
}
<Button
  onClick={downloadFrequencyReport}
  className="bg-green-600 hover:bg-green-700"
>
  <Download className="h-4 w-4 mr-2" />
  Exportar CSV
</Button>;

{
  /* Botões na tabela de alunos */
}
<div className="flex gap-2">
  <Button
    onClick={() => handleMarkAsDropout(aluno)}
    variant="destructive"
    size="sm"
  >
    <UserMinus className="h-4 w-4" />
  </Button>
  <Button
    onClick={() => handleUploadCertificate(aluno)}
    variant="outline"
    size="sm"
  >
    <Upload className="h-4 w-4" />
  </Button>
</div>;

{
  /* Botão upload atestado na chamada */
}
{
  !presencas[aluno.id]?.presente && (
    <Button
      onClick={() => handleAttestUpload(aluno)}
      variant="outline"
      size="sm"
      className="ml-2"
    >
      <Upload className="h-4 w-4" />
      Atestado
    </Button>
  );
}

// ✅ Design Implementado:
// ✅ Ícones consistentes (Download, UserMinus, Upload)
// ✅ Cores padronizadas (verde para download, vermelho para desistência)
// ✅ Tooltips e feedback visual
// ✅ Botões contextuais aparecem quando necessário
// ✅ Estados específicos para cada ação
```

#### **2. Validação Pydantic - RESOLVIDO**

```python
# Backend: Compatibilidade com dados existentes
class Aluno(BaseModel):
    data_nascimento: Optional[date] = None  # Opcional para dados existentes

class AlunoCreate(BaseModel):
    data_nascimento: date  # Obrigatória para novos cadastros

# ❌ Erro antes: Field 'data_nascimento' required [type=missing]
# ✅ Agora: Compatível com alunos existentes + obrigatório para novos
```

#### **3. Endpoint de Migração de Dados**

```python
# Backend: Migração automática de dados
@api_router.post("/migrate/fix-students")
async def fix_students_migration(current_user):
    # Atualiza alunos sem data_nascimento com data padrão (01/01/2000)
    # Só admin pode executar
    # Não quebra dados existentes
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

# Admin: resetar senha de usuário (ATUALIZADO 27/09/2025)
@api_router.post("/users/{user_id}/reset-password") # Com logs de auditoria

# Reset comum (não expõe se email existe)
@api_router.post("/auth/reset-password") # Melhor segurança

# Admin: aprovar usuário pendente (gera nova senha)
@api_router.put("/users/{user_id}/approve")

# Endpoint para instrutores (ADICIONADO 27/09/2025)
@api_router.get("/teacher/stats") # Estatísticas para instrutores

# Endpoints curso-usuário (ADICIONADO 28/09/2025)
@api_router.get("/users/{user_id}/details") # Detalhes completos do usuário com curso/unidade
@api_router.post("/classes") # Criar turma (instrutor: só do seu curso)
@api_router.get("/classes") # Listar turmas (filtrado por curso do usuário)

# Endpoints funcionalidades avançadas (ADICIONADO 29/09/2025)
@api_router.get("/reports/attendance?export_csv=true") # Download CSV de relatórios
@api_router.post("/dropouts") # Registrar desistência de aluno
@api_router.put("/students/{student_id}") # Atualizar status do aluno
@api_router.post("/upload/atestado") # Upload de atestado médico
@api_router.get("/reports/teacher-stats") # Relatórios dinâmicos para instrutores
```

### Component Props Flow

- Dados carregados no componente pai via API
- Estado passado como props ou via Context
- Mutações via handlers que fazem requests e atualizam estado local

### Sistema de Associação Curso-Usuário - IMPLEMENTADO 28/09/2025

#### **Funcionalidades Principais:**

**1. Validação Backend:**

```python
# Criação de usuário com validação de curso
if user_create.tipo in ["instrutor", "pedagogo", "monitor"]:
    if not user_create.curso_id:
        raise HTTPException(400, "Curso é obrigatório")

    # Verificar existência do curso
    curso = await db.cursos.find_one({"id": user_create.curso_id})
    if not curso:
        raise HTTPException(400, "Curso não encontrado")
```

**2. Controle de Permissões por Curso:**

```python
# Instrutor só pode criar turmas do seu curso
if current_user.tipo == "instrutor":
    if turma_create.curso_id != current_user.curso_id:
        raise HTTPException(403, "Instrutor só pode criar turmas do seu curso")
```

**3. Filtragem de Dados por Curso:**

```python
# Listagem de turmas filtrada por curso do usuário
if current_user.tipo == "instrutor":
    query["instrutor_id"] = current_user.id
    if current_user.curso_id:
        query["curso_id"] = current_user.curso_id
```

**4. Frontend com Seleção de Curso:**

```javascript
// Formulário de usuário com campo curso obrigatório
{
  ["instrutor", "pedagogo", "monitor"].includes(formData.tipo) && (
    <div className="space-y-2">
      <Label>Curso *</Label>
      <Select
        value={formData.curso_id}
        onValueChange={(value) => setFormData({ ...formData, curso_id: value })}
      >
        {cursos.map((curso) => (
          <SelectItem key={curso.id} value={curso.id}>
            {curso.nome}
          </SelectItem>
        ))}
      </Select>
    </div>
  );
}
```

#### **Fluxo de Trabalho:**

**Para Administradores:**

1. Criar unidades e cursos
2. Criar usuários associando-os a curso+unidade específicos
3. Monitorar atividades de todos os cursos

**Para Instrutores:**

1. Login → Acesso apenas ao seu curso
2. Criar turmas → Apenas do curso associado
3. Gerenciar alunos → Apenas das suas turmas

**Para Pedagogos/Monitores:**

1. Login → Visualização do curso associado
2. Relatórios → Apenas do seu curso
3. Suporte → Limitado ao curso/unidade

#### **Endpoints Específicos:**

```python
# Detalhes completos do usuário (incluindo curso/unidade)
@api_router.get("/users/{user_id}/details")

# Validação na criação de turmas
@api_router.post("/classes") # Com verificação de curso do instrutor

# Listagem filtrada por curso
@api_router.get("/classes") # Retorna apenas turmas do curso do usuário
```

### 🎯 **FLUXO COMPLETO DAS NOVAS FUNCIONALIDADES - 29/09/2025**

#### **Fluxo de Trabalho Implementado:**

**Para Relatórios CSV:**

1. Usuário acessa aba "Relatórios" → Clica "Exportar CSV"
2. Frontend chama `/reports/attendance?export_csv=true`
3. Download automático do arquivo `relatorio_frequencia_YYYY-MM-DD.csv`

**Para Desistências:**

1. Usuário acessa aba "Alunos" → Clica ícone de desistência
2. Dialog modal solicita motivo → Submit chama `/dropouts`
3. Status do aluno atualizado para 'desistente' automaticamente

**Para Atestados Médicos:**

1. **Na tabela de alunos**: Clica ícone upload → Seleciona arquivo → `/upload/atestado`
2. **Durante a chamada**: Aluno faltoso → Clica "Atestado" → Upload automático justifica falta

#### **Estados e Validações:**

- ✅ Arquivos aceitos: PDF, JPG, PNG (validação frontend + backend)
- ✅ Campos obrigatórios: Motivo desistência, arquivo atestado
- ✅ Feedback visual: Toast notifications para todas as ações
- ✅ Permissões: Respeitam sistema curso-usuário existente

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

#### 📚 **Exemplo Prático - Sistema Curso-Usuário:**

```javascript
// Admin cria instrutor associado a curso específico
const response = await axios.post(`${API}/users`, {
  nome: "Professor Silva",
  email: "silva@ios.com",
  tipo: "instrutor",
  unidade_id: "unidade_centro_123",
  curso_id: "informatica_basica_456", // OBRIGATÓRIO
});

// Instrutor logado tenta criar turma
const turmaResponse = await axios.post(`${API}/classes`, {
  nome: "Turma Informática A",
  curso_id: "informatica_basica_456", // Deve ser o mesmo do instrutor
  unidade_id: "unidade_centro_123", // Deve ser a mesma do instrutor
});

// Backend valida automaticamente:
// - Se curso_id da turma == curso_id do instrutor ✅
// - Se unidade_id da turma == unidade_id do instrutor ✅
// - Se instrutor tentar criar turma de outro curso ❌ 403 Forbidden
```

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
