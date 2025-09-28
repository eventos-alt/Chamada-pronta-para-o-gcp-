import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./components/ui/card";
import { Label } from "./components/ui/label";
import { Badge } from "./components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./components/ui/select";
import { Textarea } from "./components/ui/textarea";
import { Checkbox } from "./components/ui/checkbox";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./components/ui/table";
import { useToast } from "./hooks/use-toast";
import { Toaster } from "./components/ui/toaster";
import {
  Users,
  GraduationCap,
  Building2,
  BookOpen,
  UserCheck,
  UserX,
  Calendar,
  FileText,
  Upload,
  Download,
  LogOut,
  Plus,
  Eye,
  EyeOff,
  Edit,
  Trash2,
  Key,
  TrendingUp,
  TrendingDown,
  AlertCircle,
  CheckCircle,
  Phone,
  Mail,
  MapPin,
  Clock,
  Save,
  UserPlus,
  Shield,
  BarChart3,
  Copy,
  RefreshCw,
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Authentication Context
const AuthContext = React.createContext();

const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchCurrentUser = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`);
      setUser(response.data);
    } catch (error) {
      console.error("Error fetching user:", error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, senha) => {
    const response = await axios.post(`${API}/auth/login`, { email, senha });
    const { access_token, user: userData } = response.data;

    localStorage.setItem("token", access_token);
    axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
    setToken(access_token);
    setUser(userData);

    return userData;
  };

  const logout = () => {
    localStorage.removeItem("token");
    delete axios.defaults.headers.common["Authorization"];
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

// Login Component
const Login = () => {
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [loading, setLoading] = useState(false);
  const [showFirstAccess, setShowFirstAccess] = useState(false);
  const [showResetPassword, setShowResetPassword] = useState(false);
  const [resetEmail, setResetEmail] = useState("");
  const [resetLoading, setResetLoading] = useState(false);
  const [firstAccessData, setFirstAccessData] = useState({
    nome: "",
    email: "",
    tipo: "instrutor",
  });
  const { login } = useAuth();
  const { toast } = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const userData = await login(email, senha);

      if (userData.primeiro_acesso) {
        toast({
          title: "Primeiro acesso detectado",
          description: "Você precisa alterar sua senha",
        });
        // Redirect to change password
      } else {
        toast({
          title: "Login realizado com sucesso!",
          description: "Bem-vindo ao Sistema de Controle de Presença",
        });
      }
    } catch (error) {
      toast({
        title: "Erro no login",
        description:
          error.response?.data?.detail || "Verifique suas credenciais",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleFirstAccessSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/auth/first-access`, firstAccessData);
      toast({
        title: "Solicitação enviada!",
        description:
          "Aguarde a aprovação do administrador para acessar o sistema.",
      });
      setShowFirstAccess(false);
      setFirstAccessData({ nome: "", email: "", tipo: "instrutor" });
    } catch (error) {
      toast({
        title: "Erro na solicitação",
        description: error.response?.data?.detail || "Tente novamente",
        variant: "destructive",
      });
    }
  };

  const handleResetPasswordSubmit = async (e) => {
    e.preventDefault();
    setResetLoading(true);

    try {
      const response = await axios.post(`${API}/auth/reset-password-request`, {
        email: resetEmail,
      });

      // 🔐 SEGURANÇA: Não mostra mais a senha na tela
      toast({
        title: "Solicitação enviada!",
        description: response.data.message,
        variant: "default",
      });
      setShowResetPassword(false);
      setResetEmail("");
    } catch (error) {
      toast({
        title: "Erro ao resetar senha",
        description: error.response?.data?.detail || "Tente novamente",
        variant: "destructive",
      });
    } finally {
      setResetLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-orange-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-xl border-purple-200">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 p-3 bg-gradient-to-r from-purple-600 to-orange-500 rounded-full w-16 h-16 flex items-center justify-center shadow-lg">
            <GraduationCap className="h-8 w-8 text-white" />
          </div>
          <CardTitle className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-orange-500 bg-clip-text text-transparent">
            Sistema IOS
          </CardTitle>
          <CardDescription className="text-gray-600">
            Controle de Presença - Instituto da Oportunidade Social
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!showFirstAccess && !showResetPassword ? (
            <>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="admin@ios.com.br"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="senha">Senha</Label>
                  <Input
                    id="senha"
                    type="password"
                    value={senha}
                    onChange={(e) => setSenha(e.target.value)}
                    placeholder="Digite sua senha"
                    required
                  />
                </div>
                <Button
                  type="submit"
                  className="w-full bg-gradient-to-r from-purple-600 to-orange-500 hover:from-purple-700 hover:to-orange-600 text-white shadow-lg"
                  disabled={loading}
                >
                  {loading ? "Entrando..." : "Entrar"}
                </Button>
              </form>

              <div className="mt-4 pt-4 border-t border-purple-100 space-y-2">
                <Button
                  variant="outline"
                  className="w-full border-purple-300 text-purple-600 hover:bg-purple-50 hover:text-purple-700"
                  onClick={() => setShowFirstAccess(true)}
                >
                  <UserPlus className="h-4 w-4 mr-2" />
                  Primeiro Acesso
                </Button>

                <Button
                  variant="ghost"
                  className="w-full text-sm text-orange-600 hover:text-orange-700 hover:bg-orange-50"
                  onClick={() => setShowResetPassword(true)}
                >
                  Esqueci minha senha
                </Button>
              </div>
            </>
          ) : showResetPassword ? (
            <form onSubmit={handleResetPasswordSubmit} className="space-y-4">
              <div className="text-center mb-4">
                <h3 className="text-lg font-semibold">Resetar Senha</h3>
                <p className="text-sm text-gray-600">
                  Digite seu email para receber uma nova senha temporária
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="reset-email">Email</Label>
                <Input
                  id="reset-email"
                  type="email"
                  value={resetEmail}
                  onChange={(e) => setResetEmail(e.target.value)}
                  placeholder="seu@email.com"
                  required
                />
              </div>

              <div className="flex space-x-2">
                <Button
                  type="button"
                  variant="outline"
                  className="flex-1 border-purple-300 text-purple-600 hover:bg-purple-50"
                  onClick={() => setShowResetPassword(false)}
                >
                  Voltar
                </Button>
                <Button
                  type="submit"
                  className="flex-1 bg-gradient-to-r from-purple-600 to-orange-500 hover:from-purple-700 hover:to-orange-600 text-white"
                  disabled={resetLoading}
                >
                  {resetLoading ? "Resetando..." : "Resetar Senha"}
                </Button>
              </div>
            </form>
          ) : (
            <form onSubmit={handleFirstAccessSubmit} className="space-y-4">
              <div className="text-center mb-4">
                <h3 className="text-lg font-semibold">
                  Solicitar Primeiro Acesso
                </h3>
                <p className="text-sm text-gray-600">
                  Preencha os dados para solicitar acesso ao sistema
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="nome">Nome Completo</Label>
                <Input
                  id="nome"
                  value={firstAccessData.nome}
                  onChange={(e) =>
                    setFirstAccessData({
                      ...firstAccessData,
                      nome: e.target.value,
                    })
                  }
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={firstAccessData.email}
                  onChange={(e) =>
                    setFirstAccessData({
                      ...firstAccessData,
                      email: e.target.value,
                    })
                  }
                  required
                />
              </div>

              <div className="space-y-2">
                <Label>Tipo de Usuário</Label>
                <Select
                  value={firstAccessData.tipo}
                  onValueChange={(value) =>
                    setFirstAccessData({ ...firstAccessData, tipo: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="instrutor">Instrutor</SelectItem>
                    <SelectItem value="pedagogo">Pedagogo</SelectItem>
                    <SelectItem value="monitor">Monitor</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex space-x-2">
                <Button
                  type="button"
                  variant="outline"
                  className="flex-1 border-purple-300 text-purple-600 hover:bg-purple-50"
                  onClick={() => setShowFirstAccess(false)}
                >
                  Voltar
                </Button>
                <Button
                  type="submit"
                  className="flex-1 bg-gradient-to-r from-purple-600 to-orange-500 hover:from-purple-700 hover:to-orange-600 text-white"
                >
                  Solicitar Acesso
                </Button>
              </div>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// Dashboard Component
const Dashboard = () => {
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const { user, logout } = useAuth();
  const { toast } = useToast();

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/stats`);
      setStats(response.data);
    } catch (error) {
      console.error("Error fetching stats:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    toast({
      title: "Logout realizado",
      description: "Até logo!",
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <GraduationCap className="h-8 w-8 text-blue-600 mr-3" />
              <h1 className="text-xl font-bold text-gray-900">Sistema IOS</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="outline">
                {user?.tipo === "admin"
                  ? "Administrador"
                  : user?.tipo === "instrutor"
                  ? "Instrutor"
                  : user?.tipo === "pedagogo"
                  ? "Pedagogo"
                  : "Monitor"}
              </Badge>
              <span className="text-sm text-gray-700">{user?.nome}</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleLogout}
                className="text-gray-500 hover:text-gray-700"
                title="Sair do sistema"
              >
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {/* Enhanced Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="stats-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Unidades</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {stats.total_unidades || 0}
                  </p>
                </div>
                <Building2 className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="stats-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Cursos</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {stats.total_cursos || 0}
                  </p>
                </div>
                <BookOpen className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="stats-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Turmas</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {stats.total_turmas || 0}
                  </p>
                </div>
                <Users className="h-8 w-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="stats-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Alunos</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {stats.total_alunos || 0}
                  </p>
                </div>
                <UserCheck className="h-8 w-8 text-orange-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Additional Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <div>
                  <p className="text-sm text-gray-600">Alunos Ativos</p>
                  <p className="text-lg font-semibold">
                    {stats.alunos_ativos || 0}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <UserX className="h-5 w-5 text-red-500" />
                <div>
                  <p className="text-sm text-gray-600">Desistentes</p>
                  <p className="text-lg font-semibold">
                    {stats.alunos_desistentes || 0}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5 text-blue-500" />
                <div>
                  <p className="text-sm text-gray-600">Taxa Presença</p>
                  <p className="text-lg font-semibold">
                    {stats.taxa_presenca_mes || 0}%
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center space-x-2">
                <Calendar className="h-5 w-5 text-purple-500" />
                <div>
                  <p className="text-sm text-gray-600">Chamadas Hoje</p>
                  <p className="text-lg font-semibold">
                    {stats.chamadas_hoje || 0}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Management Tabs */}
        <Tabs defaultValue="turmas" className="w-full">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="turmas">Turmas</TabsTrigger>
            <TabsTrigger value="chamada">Chamada</TabsTrigger>
            {user?.tipo === "admin" && (
              <>
                <TabsTrigger value="alunos">Alunos</TabsTrigger>
                <TabsTrigger value="unidades">Unidades</TabsTrigger>
                <TabsTrigger value="cursos">Cursos</TabsTrigger>
                <TabsTrigger value="usuarios">Usuários</TabsTrigger>
              </>
            )}
            <TabsTrigger value="relatorios">Relatórios</TabsTrigger>
          </TabsList>

          <TabsContent value="turmas">
            <TurmasManager />
          </TabsContent>

          <TabsContent value="chamada">
            <ChamadaManager />
          </TabsContent>

          {user?.tipo === "admin" && (
            <>
              <TabsContent value="alunos">
                <AlunosManager />
              </TabsContent>

              <TabsContent value="unidades">
                <UnidadesManager />
              </TabsContent>

              <TabsContent value="cursos">
                <CursosManager />
              </TabsContent>

              <TabsContent value="usuarios">
                <UsuariosManager />
              </TabsContent>
            </>
          )}

          <TabsContent value="relatorios">
            <RelatoriosManager />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

// Sistema de Chamada Component CORRIGIDO
const ChamadaManager = () => {
  const [turmas, setTurmas] = useState([]);
  const [selectedTurma, setSelectedTurma] = useState("");
  const [alunos, setAlunos] = useState([]);
  const [presencas, setPresencas] = useState({});
  const [observacoes, setObservacoes] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingAlunos, setLoadingAlunos] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchTurmas();
  }, []);

  const fetchTurmas = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/classes`);
      setTurmas(response.data);
    } catch (error) {
      console.error("Error fetching turmas:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAlunos = async (turmaId) => {
    try {
      setLoadingAlunos(true);
      console.log("Fetching alunos for turma:", turmaId);
      const response = await axios.get(`${API}/classes/${turmaId}/students`);
      console.log("Alunos response:", response.data);
      setAlunos(response.data);

      // Initialize presencas with all students present by default
      const initialPresencas = {};
      response.data.forEach((aluno) => {
        initialPresencas[aluno.id] = {
          presente: true,
          justificativa: "",
          atestado_id: "",
        };
      });
      setPresencas(initialPresencas);
    } catch (error) {
      console.error("Error fetching alunos:", error);
      toast({
        title: "Erro ao carregar alunos",
        description: "Não foi possível carregar a lista de alunos da turma",
        variant: "destructive",
      });
    } finally {
      setLoadingAlunos(false);
    }
  };

  const handleTurmaChange = (turmaId) => {
    console.log("Turma selected:", turmaId);
    setSelectedTurma(turmaId);
    setAlunos([]);
    setPresencas({});
    if (turmaId) {
      fetchAlunos(turmaId);
    }
  };

  const handlePresencaChange = (alunoId, presente) => {
    setPresencas((prev) => ({
      ...prev,
      [alunoId]: {
        ...prev[alunoId],
        presente,
      },
    }));
  };

  const handleJustificativaChange = (alunoId, justificativa) => {
    setPresencas((prev) => ({
      ...prev,
      [alunoId]: {
        ...prev[alunoId],
        justificativa,
      },
    }));
  };

  const handleSalvarChamada = async () => {
    if (!selectedTurma) {
      toast({
        title: "Erro",
        description: "Selecione uma turma primeiro",
        variant: "destructive",
      });
      return;
    }

    // 🔒 VALIDAÇÃO: Só permite chamada do dia atual
    const hoje = new Date().toISOString().split("T")[0];
    const agora = new Date().toTimeString().split(" ")[0].substring(0, 5);

    // Verificar se é realmente hoje
    const dataAtual = new Date();
    const dataHoje = dataAtual.toISOString().split("T")[0];

    if (hoje !== dataHoje) {
      toast({
        title: "Data inválida",
        description: "Só é possível fazer chamada da data atual",
        variant: "destructive",
      });
      return;
    }

    try {
      await axios.post(`${API}/attendance`, {
        turma_id: selectedTurma,
        data: hoje,
        horario: agora,
        observacoes_aula: observacoes,
        presencas: presencas,
      });

      toast({
        title: "Chamada salva com sucesso!",
        description: `Os dados de presença foram registrados para ${new Date().toLocaleDateString(
          "pt-BR"
        )}`,
      });

      // 🎯 IMPORTANTE: Após salvar, remover a turma da lista (não pode fazer chamada novamente hoje)
      setTurmas((prev) => prev.filter((t) => t.id !== selectedTurma));
      setSelectedTurma("");
      setAlunos([]);
      setPresencas({});
      setObservacoes("");
    } catch (error) {
      toast({
        title: "Erro ao salvar chamada",
        description:
          error.response?.data?.detail ||
          "Já foi feita chamada hoje para esta turma",
        variant: "destructive",
      });
    }
  };

  const totalPresentes = Object.values(presencas).filter(
    (p) => p.presente
  ).length;
  const totalFaltas = Object.values(presencas).filter(
    (p) => !p.presente
  ).length;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <UserCheck className="h-5 w-5 mr-2 text-blue-600" />
          Sistema de Chamada
        </CardTitle>
        <CardDescription>
          Registre a presença dos alunos de forma rápida e eficiente
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label>Selecionar Turma</Label>
          <Select value={selectedTurma} onValueChange={handleTurmaChange}>
            <SelectTrigger>
              <SelectValue placeholder="Selecione uma turma" />
            </SelectTrigger>
            <SelectContent>
              {turmas.map((turma) => (
                <SelectItem key={turma.id} value={turma.id}>
                  {turma.nome} - {turma.ciclo}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {selectedTurma && (
          <div className="grid grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <Users className="h-5 w-5 text-blue-500" />
                  <div>
                    <p className="text-sm text-gray-600">Total de Alunos</p>
                    <p className="text-lg font-semibold">{alunos.length}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <div>
                    <p className="text-sm text-gray-600">Presentes</p>
                    <p className="text-lg font-semibold text-green-600">
                      {totalPresentes}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <AlertCircle className="h-5 w-5 text-red-500" />
                  <div>
                    <p className="text-sm text-gray-600">Faltas</p>
                    <p className="text-lg font-semibold text-red-600">
                      {totalFaltas}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {loadingAlunos && (
          <div className="text-center py-8">
            <div className="loading-spinner mx-auto mb-4"></div>
            <p>Carregando lista de alunos...</p>
          </div>
        )}

        {alunos.length > 0 && !loadingAlunos && (
          <>
            <div className="space-y-4">
              <h3 className="text-lg font-semibold flex items-center">
                <Users className="h-5 w-5 mr-2" />
                Lista de Presença - {new Date().toLocaleDateString()}
              </h3>

              <div className="space-y-3">
                {alunos.map((aluno, index) => (
                  <Card
                    key={aluno.id}
                    className={`p-4 transition-all ${
                      presencas[aluno.id]?.presente
                        ? "border-green-200 bg-green-50"
                        : "border-red-200 bg-red-50"
                    }`}
                  >
                    <div className="flex items-start space-x-4">
                      <div className="flex items-center space-x-3">
                        <span className="font-mono text-sm text-gray-500 w-8">
                          {String(index + 1).padStart(2, "0")}
                        </span>
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            checked={presencas[aluno.id]?.presente || false}
                            onCheckedChange={(checked) =>
                              handlePresencaChange(aluno.id, checked)
                            }
                            className="w-5 h-5"
                          />
                          <label className="text-sm font-medium cursor-pointer">
                            {presencas[aluno.id]?.presente
                              ? "Presente"
                              : "Falta"}
                          </label>
                        </div>
                      </div>

                      <div className="flex-1">
                        <p className="font-medium">{aluno.nome}</p>
                        <p className="text-sm text-gray-500">
                          CPF: {aluno.cpf}
                        </p>
                      </div>

                      {!presencas[aluno.id]?.presente && (
                        <div className="flex-1 space-y-2">
                          <Label className="text-sm">
                            Justificativa da Falta
                          </Label>
                          <Textarea
                            placeholder="Digite o motivo da falta..."
                            value={presencas[aluno.id]?.justificativa || ""}
                            onChange={(e) =>
                              handleJustificativaChange(
                                aluno.id,
                                e.target.value
                              )
                            }
                            className="min-h-16"
                          />
                          <Button
                            variant="outline"
                            size="sm"
                            className="w-full"
                          >
                            <Upload className="h-4 w-4 mr-2" />
                            Upload Atestado
                          </Button>
                        </div>
                      )}
                    </div>
                  </Card>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="observacoes">Observações da Aula</Label>
              <Textarea
                id="observacoes"
                placeholder="Digite observações sobre a aula, conteúdo ministrado, ocorrências..."
                value={observacoes}
                onChange={(e) => setObservacoes(e.target.value)}
              />
            </div>

            <Button
              onClick={handleSalvarChamada}
              className="w-full bg-green-600 hover:bg-green-700 h-12 text-lg"
            >
              <Save className="h-5 w-5 mr-2" />
              Salvar Chamada - {totalPresentes} Presentes, {totalFaltas} Faltas
            </Button>
          </>
        )}

        {selectedTurma && alunos.length === 0 && !loadingAlunos && (
          <div className="text-center py-8 text-gray-500">
            <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>Nenhum aluno encontrado nesta turma</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Usuarios Manager Component CORRIGIDO
const UsuariosManager = () => {
  const [usuarios, setUsuarios] = useState([]);
  const [unidades, setUnidades] = useState([]);
  const [cursos, setCursos] = useState([]);
  const [pendingUsers, setPendingUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [formData, setFormData] = useState({
    nome: "",
    email: "",
    tipo: "",
    telefone: "",
    unidade_id: "",
    curso_id: "",
  });
  const { toast } = useToast();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [usuariosRes, unidadesRes, cursosRes] = await Promise.all([
        axios.get(`${API}/users`),
        axios.get(`${API}/units`),
        axios.get(`${API}/courses`),
      ]);

      setUsuarios(usuariosRes.data);
      setUnidades(unidadesRes.data);
      setCursos(cursosRes.data);

      // Fetch pending users
      try {
        const pendingRes = await axios.get(`${API}/users/pending`);
        setPendingUsers(pendingRes.data);
      } catch (error) {
        console.error("Error fetching pending users:", error);
      }
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingUser) {
        await axios.put(`${API}/users/${editingUser.id}`, formData);
        toast({
          title: "Usuário atualizado com sucesso!",
          description: "As informações do usuário foram atualizadas.",
        });
      } else {
        // When creating user, a temporary password will be generated
        await axios.post(`${API}/users`, formData);
        toast({
          title: "Usuário criado com sucesso!",
          description:
            "Uma senha temporária foi gerada. O usuário deve fazer login e alterá-la.",
        });
      }

      setIsDialogOpen(false);
      setEditingUser(null);
      resetForm();
      fetchData();
    } catch (error) {
      toast({
        title: editingUser
          ? "Erro ao atualizar usuário"
          : "Erro ao criar usuário",
        description: error.response?.data?.detail || "Tente novamente",
        variant: "destructive",
      });
    }
  };

  // 🔐 NOVA FUNÇÃO: Reset de senha administrativo
  const handleResetPassword = async (userId, userName) => {
    try {
      const response = await axios.post(
        `${API}/users/${userId}/reset-password`
      );

      toast({
        title: "Senha resetada com sucesso!",
        description: `Nova senha temporária para ${response.data.user_name}: ${response.data.temp_password}`,
        variant: "default",
      });

      // Mostra alert adicional para garantir que admin veja a senha
      alert(
        `🔐 SENHA TEMPORÁRIA para ${response.data.user_name}:\n\n${response.data.temp_password}\n\nInforme esta senha ao usuário. Ele deverá alterá-la no primeiro acesso.`
      );
    } catch (error) {
      toast({
        title: "Erro ao resetar senha",
        description: error.response?.data?.detail || "Tente novamente",
        variant: "destructive",
      });
    }
  };

  const handleApproveUser = async (userId) => {
    try {
      await axios.put(`${API}/users/${userId}/approve`);
      toast({
        title: "Usuário aprovado!",
        description: "O usuário pode agora acessar o sistema.",
      });
      fetchData();
    } catch (error) {
      toast({
        title: "Erro ao aprovar usuário",
        description: error.response?.data?.detail || "Tente novamente",
        variant: "destructive",
      });
    }
  };

  const resetForm = () => {
    setFormData({
      nome: "",
      email: "",
      tipo: "",
      telefone: "",
      unidade_id: "",
      curso_id: "",
    });
  };

  const handleEdit = (usuario) => {
    setEditingUser(usuario);
    setFormData({
      nome: usuario.nome,
      email: usuario.email,
      tipo: usuario.tipo,
      telefone: usuario.telefone || "",
      unidade_id: usuario.unidade_id || "",
      curso_id: usuario.curso_id || "",
    });
    setIsDialogOpen(true);
  };

  const handleDelete = async (userId) => {
    if (window.confirm("Tem certeza que deseja desativar este usuário?")) {
      try {
        await axios.delete(`${API}/users/${userId}`);
        toast({
          title: "Usuário desativado com sucesso!",
          description: "O usuário foi desativado do sistema.",
        });
        fetchData();
      } catch (error) {
        toast({
          title: "Erro ao desativar usuário",
          description: error.response?.data?.detail || "Tente novamente",
          variant: "destructive",
        });
      }
    }
  };

  const handleOpenDialog = () => {
    setEditingUser(null);
    resetForm();
    setIsDialogOpen(true);
  };

  const getTipoLabel = (tipo) => {
    const tipos = {
      admin: "Administrador",
      instrutor: "Instrutor",
      pedagogo: "Pedagogo",
      monitor: "Monitor",
    };
    return tipos[tipo] || tipo;
  };

  if (loading) return <div>Carregando...</div>;

  return (
    <div className="space-y-6">
      {/* Pending Users Section */}
      {pendingUsers.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Shield className="h-5 w-5 mr-2 text-orange-500" />
              Usuários Pendentes de Aprovação
            </CardTitle>
            <CardDescription>
              Usuários que solicitaram primeiro acesso e aguardam aprovação
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {pendingUsers.map((user) => (
                <div
                  key={user.id}
                  className="flex items-center justify-between p-4 border rounded-lg"
                >
                  <div>
                    <p className="font-medium">{user.nome}</p>
                    <p className="text-sm text-gray-500">
                      {user.email} - {getTipoLabel(user.tipo)}
                    </p>
                  </div>
                  <Button
                    onClick={() => handleApproveUser(user.id)}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Aprovar
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Users Management */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Gerenciamento de Usuários</CardTitle>
              <CardDescription>
                Gerencie usuários do sistema (Admin Master, Instrutor, Pedagogo,
                Monitor)
              </CardDescription>
            </div>
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button
                  onClick={handleOpenDialog}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Novo Usuário
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-md">
                <DialogHeader>
                  <DialogTitle>
                    {editingUser ? "Editar Usuário" : "Criar Novo Usuário"}
                  </DialogTitle>
                  <DialogDescription>
                    {editingUser
                      ? "Atualize os dados do usuário"
                      : "Preencha os dados para criar um novo usuário. Uma senha temporária será gerada."}
                  </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="nome">Nome Completo</Label>
                    <Input
                      id="nome"
                      value={formData.nome}
                      onChange={(e) =>
                        setFormData({ ...formData, nome: e.target.value })
                      }
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={(e) =>
                        setFormData({ ...formData, email: e.target.value })
                      }
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Tipo de Usuário</Label>
                    <Select
                      value={formData.tipo}
                      onValueChange={(value) =>
                        setFormData({ ...formData, tipo: value })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione o tipo de usuário" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="admin">Administrador</SelectItem>
                        <SelectItem value="instrutor">Instrutor</SelectItem>
                        <SelectItem value="pedagogo">Pedagogo</SelectItem>
                        <SelectItem value="monitor">Monitor</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="telefone">Telefone</Label>
                    <Input
                      id="telefone"
                      value={formData.telefone}
                      onChange={(e) =>
                        setFormData({ ...formData, telefone: e.target.value })
                      }
                      placeholder="(11) 99999-9999"
                    />
                  </div>

                  {formData.tipo !== "admin" && (
                    <>
                      <div className="space-y-2">
                        <Label>Unidade</Label>
                        <Select
                          value={formData.unidade_id}
                          onValueChange={(value) =>
                            setFormData({ ...formData, unidade_id: value })
                          }
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Selecione a unidade" />
                          </SelectTrigger>
                          <SelectContent>
                            {unidades.map((unidade) => (
                              <SelectItem key={unidade.id} value={unidade.id}>
                                {unidade.nome}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      {["instrutor", "pedagogo", "monitor"].includes(
                        formData.tipo
                      ) && (
                        <div className="space-y-2">
                          <Label>Curso *</Label>
                          <Select
                            value={formData.curso_id}
                            onValueChange={(value) =>
                              setFormData({ ...formData, curso_id: value })
                            }
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="Selecione o curso" />
                            </SelectTrigger>
                            <SelectContent>
                              {cursos.map((curso) => (
                                <SelectItem key={curso.id} value={curso.id}>
                                  {curso.nome}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      )}
                    </>
                  )}

                  <Button
                    type="submit"
                    className="w-full bg-blue-600 hover:bg-blue-700"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    {editingUser ? "Atualizar Usuário" : "Criar Usuário"}
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        <CardContent>
          <div className="table-container">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Telefone</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {usuarios.map((usuario) => (
                  <TableRow key={usuario.id}>
                    <TableCell className="font-medium">
                      {usuario.nome}
                    </TableCell>
                    <TableCell>{usuario.email}</TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {getTipoLabel(usuario.tipo)}
                      </Badge>
                    </TableCell>
                    <TableCell>{usuario.telefone || "-"}</TableCell>
                    <TableCell>
                      <Badge variant={usuario.ativo ? "default" : "secondary"}>
                        {usuario.ativo ? "Ativo" : "Inativo"}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEdit(usuario)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() =>
                            handleResetPassword(usuario.id, usuario.nome)
                          }
                          className="text-blue-600 hover:text-blue-700"
                          title="Resetar Senha"
                        >
                          <Key className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDelete(usuario.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Turmas Manager Component CORRIGIDO
const TurmasManager = () => {
  const [turmas, setTurmas] = useState([]);
  const [unidades, setUnidades] = useState([]);
  const [cursos, setCursos] = useState([]);
  const [usuarios, setUsuarios] = useState([]);
  const [alunos, setAlunos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isAlunoDialogOpen, setIsAlunoDialogOpen] = useState(false);
  const [editingTurma, setEditingTurma] = useState(null);
  const [selectedTurmaForAlunos, setSelectedTurmaForAlunos] = useState(null);
  const [formData, setFormData] = useState({
    nome: "",
    unidade_id: "",
    curso_id: "",
    instrutor_id: "",
    data_inicio: "",
    data_fim: "",
    horario_inicio: "",
    horario_fim: "",
    dias_semana: [],
    vagas_total: 30,
    ciclo: "01/2025",
  });
  const { toast } = useToast();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      console.log("Fetching turmas data...");
      const [turmasRes, unidadesRes, cursosRes, usuariosRes, alunosRes] =
        await Promise.all([
          axios.get(`${API}/classes`),
          axios.get(`${API}/units`),
          axios.get(`${API}/courses`),
          axios.get(`${API}/users?tipo=instrutor`),
          axios.get(`${API}/students`),
        ]);

      console.log("Turmas:", turmasRes.data);
      console.log("Unidades:", unidadesRes.data);
      console.log("Cursos:", cursosRes.data);
      console.log("Usuarios:", usuariosRes.data);
      console.log("Alunos:", alunosRes.data);

      setTurmas(turmasRes.data);
      setUnidades(unidadesRes.data);
      setCursos(cursosRes.data);
      setUsuarios(usuariosRes.data);
      setAlunos(alunosRes.data);
    } catch (error) {
      console.error("Error fetching data:", error);
      toast({
        title: "Erro ao carregar dados",
        description: "Não foi possível carregar os dados necessários",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingTurma) {
        await axios.put(`${API}/classes/${editingTurma.id}`, formData);
        toast({
          title: "Turma atualizada com sucesso!",
          description: "As informações da turma foram atualizadas.",
        });
      } else {
        await axios.post(`${API}/classes`, formData);
        toast({
          title: "Turma criada com sucesso!",
          description: "A nova turma foi adicionada ao sistema.",
        });
      }

      setIsDialogOpen(false);
      setEditingTurma(null);
      resetForm();
      fetchData();
    } catch (error) {
      toast({
        title: editingTurma ? "Erro ao atualizar turma" : "Erro ao criar turma",
        description: error.response?.data?.detail || "Tente novamente",
        variant: "destructive",
      });
    }
  };

  const resetForm = () => {
    setFormData({
      nome: "",
      unidade_id: "",
      curso_id: "",
      instrutor_id: "",
      data_inicio: "",
      data_fim: "",
      horario_inicio: "",
      horario_fim: "",
      dias_semana: [],
      vagas_total: 30,
      ciclo: "01/2025",
    });
  };

  const handleViewTurma = (turma) => {
    const unidadeNome =
      unidades.find((u) => u.id === turma.unidade_id)?.nome || "N/A";
    const cursoNome =
      cursos.find((c) => c.id === turma.curso_id)?.nome || "N/A";
    const instrutorNome =
      usuarios.find((u) => u.id === turma.instrutor_id)?.nome || "N/A";

    alert(
      `📋 DETALHES DA TURMA\n\n` +
        `Nome: ${turma.nome}\n` +
        `Unidade: ${unidadeNome}\n` +
        `Curso: ${cursoNome}\n` +
        `Instrutor: ${instrutorNome}\n` +
        `Período: ${turma.data_inicio} a ${turma.data_fim}\n` +
        `Horário: ${turma.horario_inicio} às ${turma.horario_fim}\n` +
        `Vagas: ${turma.vagas_ocupadas || 0}/${turma.vagas_total}\n` +
        `Ciclo: ${turma.ciclo}\n` +
        `Status: ${turma.ativo ? "Ativa" : "Inativa"}`
    );
  };

  const handleEdit = (turma) => {
    setEditingTurma(turma);
    setFormData({
      nome: turma.nome,
      unidade_id: turma.unidade_id,
      curso_id: turma.curso_id,
      instrutor_id: turma.instrutor_id,
      data_inicio: turma.data_inicio,
      data_fim: turma.data_fim,
      horario_inicio: turma.horario_inicio,
      horario_fim: turma.horario_fim,
      dias_semana: turma.dias_semana || [],
      vagas_total: turma.vagas_total,
      ciclo: turma.ciclo,
    });
    setIsDialogOpen(true);
  };

  const handleOpenDialog = () => {
    setEditingTurma(null);
    resetForm();
    setIsDialogOpen(true);
  };

  const handleManageAlunos = (turma) => {
    setSelectedTurmaForAlunos(turma);
    setIsAlunoDialogOpen(true);
  };

  const handleAddAlunoToTurma = async (alunoId) => {
    try {
      await axios.put(
        `${API}/classes/${selectedTurmaForAlunos.id}/students/${alunoId}`
      );
      toast({
        title: "Aluno adicionado com sucesso!",
        description: "O aluno foi adicionado à turma.",
      });
      fetchData(); // Atualizar dados
    } catch (error) {
      toast({
        title: "Erro ao adicionar aluno",
        description: error.response?.data?.detail || "Tente novamente",
        variant: "destructive",
      });
    }
  };

  const handleRemoveAlunoFromTurma = async (alunoId) => {
    try {
      await axios.delete(
        `${API}/classes/${selectedTurmaForAlunos.id}/students/${alunoId}`
      );
      toast({
        title: "Aluno removido com sucesso!",
        description: "O aluno foi removido da turma.",
      });
      fetchData(); // Atualizar dados
    } catch (error) {
      toast({
        title: "Erro ao remover aluno",
        description: error.response?.data?.detail || "Tente novamente",
        variant: "destructive",
      });
    }
  };

  if (loading) return <div>Carregando...</div>;

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>Gerenciamento de Turmas</CardTitle>
            <CardDescription>
              Visualize e gerencie todas as turmas do sistema
            </CardDescription>
          </div>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button
                onClick={handleOpenDialog}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                Nova Turma
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>
                  {editingTurma ? "Editar Turma" : "Criar Nova Turma"}
                </DialogTitle>
                <DialogDescription>
                  {editingTurma
                    ? "Atualize os dados da turma"
                    : "Preencha os dados para criar uma nova turma"}
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="nome">Nome da Turma</Label>
                    <Input
                      id="nome"
                      value={formData.nome}
                      onChange={(e) =>
                        setFormData({ ...formData, nome: e.target.value })
                      }
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="ciclo">Ciclo</Label>
                    <Input
                      id="ciclo"
                      value={formData.ciclo}
                      onChange={(e) =>
                        setFormData({ ...formData, ciclo: e.target.value })
                      }
                      placeholder="01/2025"
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Unidade ({unidades.length} disponíveis)</Label>
                    <Select
                      value={formData.unidade_id}
                      onValueChange={(value) =>
                        setFormData({ ...formData, unidade_id: value })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione a unidade" />
                      </SelectTrigger>
                      <SelectContent>
                        {unidades.map((unidade) => (
                          <SelectItem key={unidade.id} value={unidade.id}>
                            {unidade.nome}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Curso ({cursos.length} disponíveis)</Label>
                    <Select
                      value={formData.curso_id}
                      onValueChange={(value) =>
                        setFormData({ ...formData, curso_id: value })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione o curso" />
                      </SelectTrigger>
                      <SelectContent>
                        {cursos.map((curso) => (
                          <SelectItem key={curso.id} value={curso.id}>
                            {curso.nome}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Instrutor ({usuarios.length} disponíveis)</Label>
                  <Select
                    value={formData.instrutor_id}
                    onValueChange={(value) =>
                      setFormData({ ...formData, instrutor_id: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione o instrutor" />
                    </SelectTrigger>
                    <SelectContent>
                      {usuarios.map((usuario) => (
                        <SelectItem key={usuario.id} value={usuario.id}>
                          {usuario.nome}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="data_inicio">Data Início</Label>
                    <Input
                      id="data_inicio"
                      type="date"
                      value={formData.data_inicio}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          data_inicio: e.target.value,
                        })
                      }
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="data_fim">Data Fim</Label>
                    <Input
                      id="data_fim"
                      type="date"
                      value={formData.data_fim}
                      onChange={(e) =>
                        setFormData({ ...formData, data_fim: e.target.value })
                      }
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="horario_inicio">Horário Início</Label>
                    <Input
                      id="horario_inicio"
                      type="time"
                      value={formData.horario_inicio}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          horario_inicio: e.target.value,
                        })
                      }
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="horario_fim">Horário Fim</Label>
                    <Input
                      id="horario_fim"
                      type="time"
                      value={formData.horario_fim}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          horario_fim: e.target.value,
                        })
                      }
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="vagas_total">Vagas Total</Label>
                  <Input
                    id="vagas_total"
                    type="number"
                    value={formData.vagas_total}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        vagas_total: parseInt(e.target.value),
                      })
                    }
                    min="1"
                    required
                  />
                </div>

                <Button
                  type="submit"
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  <Save className="h-4 w-4 mr-2" />
                  {editingTurma ? "Atualizar Turma" : "Criar Turma"}
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </CardHeader>
      <CardContent>
        <div className="table-container">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Ciclo</TableHead>
                <TableHead>Período</TableHead>
                <TableHead>Horário</TableHead>
                <TableHead>Vagas</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {turmas.map((turma) => (
                <TableRow key={turma.id}>
                  <TableCell className="font-medium">{turma.nome}</TableCell>
                  <TableCell>{turma.ciclo}</TableCell>
                  <TableCell>
                    {new Date(turma.data_inicio).toLocaleDateString()} -{" "}
                    {new Date(turma.data_fim).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    {turma.horario_inicio} - {turma.horario_fim}
                  </TableCell>
                  <TableCell>
                    {turma.vagas_ocupadas}/{turma.vagas_total}
                  </TableCell>
                  <TableCell>
                    <Badge variant={turma.ativo ? "default" : "secondary"}>
                      {turma.ativo ? "Ativa" : "Inativa"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleViewTurma(turma)}
                        title="Visualizar detalhes"
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleManageAlunos(turma)}
                        title="Gerenciar alunos"
                        className="text-green-600 hover:text-green-700"
                      >
                        <UserPlus className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleEdit(turma)}
                        title="Editar turma"
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>

      {/* Dialog para gerenciar alunos da turma */}
      <Dialog open={isAlunoDialogOpen} onOpenChange={setIsAlunoDialogOpen}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>
              Gerenciar Alunos - {selectedTurmaForAlunos?.nome}
            </DialogTitle>
            <DialogDescription>
              Adicione ou remova alunos desta turma
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold mb-2">Alunos Disponíveis</h3>
              <div className="max-h-40 overflow-y-auto border rounded p-2">
                {alunos
                  .filter(
                    (aluno) =>
                      !selectedTurmaForAlunos?.alunos_ids?.includes(aluno.id) &&
                      aluno.ativo
                  )
                  .map((aluno) => (
                    <div
                      key={aluno.id}
                      className="flex justify-between items-center p-2 hover:bg-gray-50 rounded"
                    >
                      <div>
                        <span className="font-medium">{aluno.nome}</span>
                        <span className="text-sm text-gray-500 ml-2">
                          {aluno.cpf}
                        </span>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleAddAlunoToTurma(aluno.id)}
                        className="text-green-600 hover:text-green-700"
                      >
                        <Plus className="h-4 w-4 mr-1" />
                        Adicionar
                      </Button>
                    </div>
                  ))}
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-2">
                Alunos na Turma (
                {selectedTurmaForAlunos?.alunos_ids?.length || 0}/
                {selectedTurmaForAlunos?.vagas_total || 0})
              </h3>
              <div className="max-h-40 overflow-y-auto border rounded p-2">
                {alunos
                  .filter((aluno) =>
                    selectedTurmaForAlunos?.alunos_ids?.includes(aluno.id)
                  )
                  .map((aluno) => (
                    <div
                      key={aluno.id}
                      className="flex justify-between items-center p-2 hover:bg-gray-50 rounded"
                    >
                      <div>
                        <span className="font-medium">{aluno.nome}</span>
                        <span className="text-sm text-gray-500 ml-2">
                          {aluno.cpf}
                        </span>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleRemoveAlunoFromTurma(aluno.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4 mr-1" />
                        Remover
                      </Button>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </Card>
  );
};

// 📊 RELATÓRIOS DINÂMICOS - Atualizados Automaticamente
const RelatoriosManager = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDynamicStats();

    // 🔄 AUTO-REFRESH: Atualizar relatórios a cada 30 segundos
    const interval = setInterval(fetchDynamicStats, 30000);

    return () => clearInterval(interval);
  }, [user]);

  const fetchDynamicStats = async () => {
    try {
      // 🎯 NOVO ENDPOINT: Relatórios dinâmicos para todos os tipos de usuário
      const response = await axios.get(`${API}/reports/teacher-stats`);
      setStats(response.data);
    } catch (error) {
      console.error("Error fetching dynamic stats:", error);
      // Fallback para endpoint antigo se necessário
      if (user?.tipo === "instrutor") {
        try {
          const fallbackResponse = await axios.get(`${API}/teacher/stats`);
          setStats(fallbackResponse.data);
        } catch (fallbackError) {
          console.error("Fallback also failed:", fallbackError);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <RefreshCw className="h-5 w-5 animate-spin mr-2" />
            <span>Carregando relatórios dinâmicos...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  // 📊 RELATÓRIOS DINÂMICOS - Interface completamente atualizada
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center">
            <BarChart3 className="h-5 w-5 mr-2" />
            Estatísticas das Minhas Turmas
          </div>
          <div className="flex items-center text-sm text-gray-500">
            <RefreshCw className="h-4 w-4 mr-1 animate-spin" />
            Atualizado automaticamente
          </div>
        </CardTitle>
        <CardDescription>
          Visualize índices de presença e faltas dos seus alunos - Dados em
          tempo real
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 🟢 MAIORES PRESENÇAS - Dados Dinâmicos */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg text-green-600">
                Maiores Presenças
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {stats.maiores_presencas &&
                stats.maiores_presencas.length > 0 ? (
                  stats.maiores_presencas.map((aluno, index) => (
                    <div
                      key={index}
                      className="flex justify-between items-center p-3 bg-green-50 rounded-lg"
                    >
                      <div>
                        <p className="font-medium">{aluno.nome}</p>
                        <p className="text-sm text-gray-500">{aluno.turma}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-green-600">
                          {aluno.taxa_presenca}
                        </p>
                        <p className="text-xs text-gray-500">
                          {aluno.aulas_presentes}
                        </p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-4 text-gray-500">
                    <Users className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p>Nenhum dado de presença disponível ainda</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* 🔴 MAIORES FALTAS - Dados Dinâmicos */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg text-red-600">
                Maiores Faltas
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {stats.maiores_faltas && stats.maiores_faltas.length > 0 ? (
                  stats.maiores_faltas.map((aluno, index) => (
                    <div
                      key={index}
                      className="flex justify-between items-center p-3 bg-red-50 rounded-lg"
                    >
                      <div>
                        <p className="font-medium">{aluno.nome}</p>
                        <p className="text-sm text-gray-500">{aluno.turma}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-red-600">
                          {aluno.taxa_presenca}
                        </p>
                        <p className="text-xs text-gray-500">{aluno.faltas}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-4 text-gray-500">
                    <AlertCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p>Nenhum dado de falta disponível ainda</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* 📊 RESUMO GERAL - Dados Dinâmicos */}
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle className="text-lg">
                Resumo Geral das Suas Turmas
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <p className="text-2xl font-bold text-blue-600">
                    {stats.taxa_media_presenca || "0%"}
                  </p>
                  <p className="text-sm text-gray-600">
                    Taxa Média de Presença
                  </p>
                </div>

                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <p className="text-2xl font-bold text-green-600">
                    {stats.total_alunos || 0}
                  </p>
                  <p className="text-sm text-gray-600">Total de Alunos</p>
                </div>

                <div className="text-center p-4 bg-yellow-50 rounded-lg">
                  <p className="text-2xl font-bold text-yellow-600">
                    {stats.alunos_em_risco || 0}
                  </p>
                  <p className="text-sm text-gray-600">Alunos em Risco</p>
                </div>

                <div className="text-center p-4 bg-red-50 rounded-lg">
                  <p className="text-2xl font-bold text-red-600">
                    {stats.desistentes || 0}
                  </p>
                  <p className="text-sm text-gray-600">Desistentes</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 📋 RESUMO POR TURMA - NOVO */}
          {stats.resumo_turmas && stats.resumo_turmas.length > 0 && (
            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle className="text-lg">Resumo por Turma</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {stats.resumo_turmas.map((turma, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <h4 className="font-medium text-lg mb-2">{turma.nome}</h4>
                      <div className="grid grid-cols-3 gap-2 text-sm">
                        <div>
                          <p className="text-gray-600">Alunos</p>
                          <p className="font-bold">{turma.total_alunos}</p>
                        </div>
                        <div>
                          <p className="text-gray-600">Taxa Média</p>
                          <p className="font-bold text-blue-600">
                            {turma.taxa_media}%
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-600">Em Risco</p>
                          <p className="font-bold text-yellow-600">
                            {turma.alunos_risco}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

// Alunos Manager Component COMPLETO
const AlunosManager = () => {
  const [alunos, setAlunos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingAluno, setEditingAluno] = useState(null);
  const [formData, setFormData] = useState({
    nome: "",
    cpf: "",
    idade: "",
    rg: "",
    data_nascimento: "",
    genero: "",
    telefone: "",
    email: "",
    endereco: "",
    nome_responsavel: "",
    telefone_responsavel: "",
    observacoes: "",
  });
  const { toast } = useToast();

  useEffect(() => {
    fetchAlunos();
  }, []);

  const fetchAlunos = async () => {
    try {
      const response = await axios.get(`${API}/students`);
      setAlunos(response.data);
    } catch (error) {
      console.error("Error fetching alunos:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingAluno) {
        await axios.put(`${API}/students/${editingAluno.id}`, formData);
        toast({
          title: "Aluno atualizado com sucesso!",
          description: "As informações do aluno foram atualizadas.",
        });
      } else {
        await axios.post(`${API}/students`, formData);
        toast({
          title: "Aluno criado com sucesso!",
          description: "O novo aluno foi adicionado ao sistema.",
        });
      }

      setIsDialogOpen(false);
      setEditingAluno(null);
      resetForm();
      fetchAlunos();
    } catch (error) {
      toast({
        title: editingAluno ? "Erro ao atualizar aluno" : "Erro ao criar aluno",
        description: error.response?.data?.detail || "Tente novamente",
        variant: "destructive",
      });
    }
  };

  const resetForm = () => {
    setFormData({
      nome: "",
      cpf: "",
      idade: "",
      rg: "",
      data_nascimento: "",
      genero: "",
      telefone: "",
      email: "",
      endereco: "",
      nome_responsavel: "",
      telefone_responsavel: "",
      observacoes: "",
    });
  };

  const handleViewAluno = (aluno) => {
    alert(
      `👤 DETALHES DO ALUNO\n\n` +
        `📋 DADOS OBRIGATÓRIOS:\n` +
        `Nome: ${aluno.nome}\n` +
        `CPF: ${aluno.cpf}\n` +
        `Idade: ${aluno.idade ? `${aluno.idade} anos` : "N/A"}\n\n` +
        `📄 DADOS COMPLEMENTARES:\n` +
        `RG: ${aluno.rg || "N/A"}\n` +
        `Data Nascimento: ${aluno.data_nascimento || "N/A"}\n` +
        `Gênero: ${aluno.genero || "N/A"}\n` +
        `Telefone: ${aluno.telefone || "N/A"}\n` +
        `Email: ${aluno.email || "N/A"}\n` +
        `Endereço: ${aluno.endereco || "N/A"}\n` +
        `Responsável: ${aluno.nome_responsavel || "N/A"}\n` +
        `Tel. Responsável: ${aluno.telefone_responsavel || "N/A"}\n` +
        `Status: ${aluno.ativo ? "Ativo" : "Inativo"}\n` +
        `Observações: ${aluno.observacoes || "Nenhuma"}`
    );
  };

  const handleEdit = (aluno) => {
    setEditingAluno(aluno);
    setFormData({
      nome: aluno.nome,
      cpf: aluno.cpf,
      idade: aluno.idade || "",
      rg: aluno.rg || "",
      data_nascimento: aluno.data_nascimento || "",
      genero: aluno.genero || "",
      telefone: aluno.telefone || "",
      email: aluno.email || "",
      endereco: aluno.endereco || "",
      nome_responsavel: aluno.nome_responsavel || "",
      telefone_responsavel: aluno.telefone_responsavel || "",
      observacoes: aluno.observacoes || "",
    });
    setIsDialogOpen(true);
  };

  const handleOpenDialog = () => {
    setEditingAluno(null);
    resetForm();
    setIsDialogOpen(true);
  };

  const getStatusColor = (status) => {
    const colors = {
      ativo: "default",
      desistente: "destructive",
      concluido: "secondary",
      suspenso: "outline",
    };
    return colors[status] || "default";
  };

  const getStatusLabel = (status) => {
    const labels = {
      ativo: "Ativo",
      desistente: "Desistente",
      concluido: "Concluído",
      suspenso: "Suspenso",
    };
    return labels[status] || status;
  };

  if (loading) return <div>Carregando...</div>;

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>Gerenciamento de Alunos</CardTitle>
            <CardDescription>
              Gerencie os alunos cadastrados no sistema
            </CardDescription>
          </div>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button
                onClick={handleOpenDialog}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                Novo Aluno
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>
                  {editingAluno ? "Editar Aluno" : "Cadastrar Novo Aluno"}
                </DialogTitle>
                <DialogDescription>
                  {editingAluno
                    ? "Atualize os dados do aluno"
                    : "Preencha os dados para cadastrar um novo aluno"}
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Campos Obrigatórios - Destacados */}
                <div className="border-2 border-blue-200 rounded-lg p-4 bg-blue-50">
                  <h3 className="text-lg font-semibold text-blue-800 mb-3">
                    📋 Informações Obrigatórias
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label
                        htmlFor="nome"
                        className="text-blue-700 font-medium"
                      >
                        Nome Completo *
                      </Label>
                      <Input
                        id="nome"
                        value={formData.nome}
                        onChange={(e) =>
                          setFormData({ ...formData, nome: e.target.value })
                        }
                        placeholder="Ex: João Silva Santos"
                        className="border-blue-300 focus:border-blue-500"
                        required
                      />
                    </div>

                    <div className="space-y-2">
                      <Label
                        htmlFor="idade"
                        className="text-blue-700 font-medium"
                      >
                        Idade *
                      </Label>
                      <Input
                        id="idade"
                        type="number"
                        value={formData.idade}
                        onChange={(e) =>
                          setFormData({ ...formData, idade: e.target.value })
                        }
                        placeholder="Ex: 25"
                        min="1"
                        max="120"
                        className="border-blue-300 focus:border-blue-500"
                        required
                      />
                    </div>

                    <div className="space-y-2">
                      <Label
                        htmlFor="cpf"
                        className="text-blue-700 font-medium"
                      >
                        CPF *
                      </Label>
                      <Input
                        id="cpf"
                        value={formData.cpf}
                        onChange={(e) =>
                          setFormData({ ...formData, cpf: e.target.value })
                        }
                        placeholder="000.000.000-00"
                        className="border-blue-300 focus:border-blue-500"
                        required
                      />
                    </div>
                  </div>
                </div>

                {/* Campos Complementares */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-700">
                    📄 Informações Complementares
                  </h3>

                  <div className="grid grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="rg">RG</Label>
                      <Input
                        id="rg"
                        value={formData.rg}
                        onChange={(e) =>
                          setFormData({ ...formData, rg: e.target.value })
                        }
                        placeholder="00.000.000-0"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="data_nascimento">
                        Data de Nascimento
                      </Label>
                      <Input
                        id="data_nascimento"
                        type="date"
                        value={formData.data_nascimento}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            data_nascimento: e.target.value,
                          })
                        }
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Gênero</Label>
                      <Select
                        value={formData.genero}
                        onValueChange={(value) =>
                          setFormData({ ...formData, genero: value })
                        }
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Selecione" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="masculino">Masculino</SelectItem>
                          <SelectItem value="feminino">Feminino</SelectItem>
                          <SelectItem value="outro">Outro</SelectItem>
                          <SelectItem value="nao_informado">
                            Não informado
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="telefone">Telefone</Label>
                      <Input
                        id="telefone"
                        value={formData.telefone}
                        onChange={(e) =>
                          setFormData({ ...formData, telefone: e.target.value })
                        }
                        placeholder="(11) 99999-9999"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        type="email"
                        value={formData.email}
                        onChange={(e) =>
                          setFormData({ ...formData, email: e.target.value })
                        }
                        placeholder="aluno@email.com"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="endereco">Endereço Completo</Label>
                    <Input
                      id="endereco"
                      value={formData.endereco}
                      onChange={(e) =>
                        setFormData({ ...formData, endereco: e.target.value })
                      }
                      placeholder="Rua, número, bairro, cidade, CEP"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="nome_responsavel">
                        Nome do Responsável
                      </Label>
                      <Input
                        id="nome_responsavel"
                        value={formData.nome_responsavel}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            nome_responsavel: e.target.value,
                          })
                        }
                        placeholder="Para menores de idade"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="telefone_responsavel">
                        Telefone do Responsável
                      </Label>
                      <Input
                        id="telefone_responsavel"
                        value={formData.telefone_responsavel}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            telefone_responsavel: e.target.value,
                          })
                        }
                        placeholder="(11) 99999-9999"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="observacoes">Observações</Label>
                    <Textarea
                      id="observacoes"
                      value={formData.observacoes}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          observacoes: e.target.value,
                        })
                      }
                      placeholder="Observações sobre o aluno..."
                    />
                  </div>
                </div>

                <Button
                  type="submit"
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  <Save className="h-4 w-4 mr-2" />
                  {editingAluno ? "Atualizar Aluno" : "Cadastrar Aluno"}
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </CardHeader>
      <CardContent>
        <div className="table-container">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>CPF</TableHead>
                <TableHead>Idade</TableHead>
                <TableHead>Contato</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {alunos.map((aluno) => (
                <TableRow key={aluno.id}>
                  <TableCell className="font-medium">{aluno.nome}</TableCell>
                  <TableCell>{aluno.cpf}</TableCell>
                  <TableCell className="text-center font-medium">
                    {aluno.idade ? `${aluno.idade} anos` : "N/A"}
                  </TableCell>
                  <TableCell>
                    <div className="space-y-1">
                      {aluno.telefone && (
                        <div className="flex items-center text-sm">
                          <Phone className="h-3 w-3 mr-1 text-gray-400" />
                          {aluno.telefone}
                        </div>
                      )}
                      {aluno.email && (
                        <div className="flex items-center text-sm">
                          <Mail className="h-3 w-3 mr-1 text-gray-400" />
                          {aluno.email}
                        </div>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant={getStatusColor(aluno.status)}>
                      {getStatusLabel(aluno.status)}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleViewAluno(aluno)}
                        title="Visualizar detalhes"
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleEdit(aluno)}
                        title="Editar aluno"
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
};

// Unidades Manager Component COMPLETO
const UnidadesManager = () => {
  const [unidades, setUnidades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingUnidade, setEditingUnidade] = useState(null);
  const [formData, setFormData] = useState({
    nome: "",
    endereco: "",
    telefone: "",
    responsavel: "",
    email: "",
  });
  const { toast } = useToast();

  useEffect(() => {
    fetchUnidades();
  }, []);

  const fetchUnidades = async () => {
    try {
      const response = await axios.get(`${API}/units`);
      setUnidades(response.data);
    } catch (error) {
      console.error("Error fetching unidades:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingUnidade) {
        await axios.put(`${API}/units/${editingUnidade.id}`, formData);
        toast({
          title: "Unidade atualizada com sucesso!",
          description: "As informações da unidade foram atualizadas.",
        });
      } else {
        await axios.post(`${API}/units`, formData);
        toast({
          title: "Unidade criada com sucesso!",
          description: "A nova unidade foi adicionada ao sistema.",
        });
      }

      setIsDialogOpen(false);
      setEditingUnidade(null);
      resetForm();
      fetchUnidades();
    } catch (error) {
      toast({
        title: editingUnidade
          ? "Erro ao atualizar unidade"
          : "Erro ao criar unidade",
        description: error.response?.data?.detail || "Tente novamente",
        variant: "destructive",
      });
    }
  };

  const resetForm = () => {
    setFormData({
      nome: "",
      endereco: "",
      telefone: "",
      responsavel: "",
      email: "",
    });
  };

  const handleEdit = (unidade) => {
    setEditingUnidade(unidade);
    setFormData({
      nome: unidade.nome,
      endereco: unidade.endereco,
      telefone: unidade.telefone || "",
      responsavel: unidade.responsavel || "",
      email: unidade.email || "",
    });
    setIsDialogOpen(true);
  };

  const handleDelete = async (unidadeId) => {
    if (window.confirm("Tem certeza que deseja desativar esta unidade?")) {
      try {
        await axios.delete(`${API}/units/${unidadeId}`);
        toast({
          title: "Unidade desativada com sucesso!",
          description: "A unidade foi desativada do sistema.",
        });
        fetchUnidades();
      } catch (error) {
        toast({
          title: "Erro ao desativar unidade",
          description: error.response?.data?.detail || "Tente novamente",
          variant: "destructive",
        });
      }
    }
  };

  const handleOpenDialog = () => {
    setEditingUnidade(null);
    resetForm();
    setIsDialogOpen(true);
  };

  if (loading) return <div>Carregando...</div>;

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>Gerenciamento de Unidades</CardTitle>
            <CardDescription>
              Gerencie as unidades do Instituto da Oportunidade Social
            </CardDescription>
          </div>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button
                onClick={handleOpenDialog}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                Nova Unidade
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>
                  {editingUnidade ? "Editar Unidade" : "Criar Nova Unidade"}
                </DialogTitle>
                <DialogDescription>
                  {editingUnidade
                    ? "Atualize os dados da unidade"
                    : "Preencha os dados para criar uma nova unidade"}
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="nome">Nome da Unidade</Label>
                  <Input
                    id="nome"
                    value={formData.nome}
                    onChange={(e) =>
                      setFormData({ ...formData, nome: e.target.value })
                    }
                    placeholder="Ex: Unidade Centro"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="endereco">Endereço</Label>
                  <Input
                    id="endereco"
                    value={formData.endereco}
                    onChange={(e) =>
                      setFormData({ ...formData, endereco: e.target.value })
                    }
                    placeholder="Rua, número, bairro, cidade"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="telefone">Telefone</Label>
                  <Input
                    id="telefone"
                    value={formData.telefone}
                    onChange={(e) =>
                      setFormData({ ...formData, telefone: e.target.value })
                    }
                    placeholder="(11) 1234-5678"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="responsavel">Responsável</Label>
                  <Input
                    id="responsavel"
                    value={formData.responsavel}
                    onChange={(e) =>
                      setFormData({ ...formData, responsavel: e.target.value })
                    }
                    placeholder="Nome do responsável"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) =>
                      setFormData({ ...formData, email: e.target.value })
                    }
                    placeholder="unidade@ios.com.br"
                  />
                </div>

                <Button
                  type="submit"
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  <Save className="h-4 w-4 mr-2" />
                  {editingUnidade ? "Atualizar Unidade" : "Criar Unidade"}
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </CardHeader>
      <CardContent>
        <div className="table-container">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Endereço</TableHead>
                <TableHead>Contato</TableHead>
                <TableHead>Responsável</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {unidades.map((unidade) => (
                <TableRow key={unidade.id}>
                  <TableCell className="font-medium">{unidade.nome}</TableCell>
                  <TableCell>
                    <div className="flex items-center">
                      <MapPin className="h-4 w-4 mr-1 text-gray-400" />
                      {unidade.endereco}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="space-y-1">
                      {unidade.telefone && (
                        <div className="flex items-center text-sm">
                          <Phone className="h-3 w-3 mr-1 text-gray-400" />
                          {unidade.telefone}
                        </div>
                      )}
                      {unidade.email && (
                        <div className="flex items-center text-sm">
                          <Mail className="h-3 w-3 mr-1 text-gray-400" />
                          {unidade.email}
                        </div>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>{unidade.responsavel || "-"}</TableCell>
                  <TableCell>
                    <Badge variant={unidade.ativo ? "default" : "secondary"}>
                      {unidade.ativo ? "Ativa" : "Inativa"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleEdit(unidade)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDelete(unidade.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
};

// Cursos Manager Component COMPLETO
const CursosManager = () => {
  const [cursos, setCursos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingCurso, setEditingCurso] = useState(null);
  const [formData, setFormData] = useState({
    nome: "",
    descricao: "",
    carga_horaria: "",
    categoria: "",
    pre_requisitos: "",
  });
  const { toast } = useToast();

  useEffect(() => {
    fetchCursos();
  }, []);

  const fetchCursos = async () => {
    try {
      const response = await axios.get(`${API}/courses`);
      setCursos(response.data);
    } catch (error) {
      console.error("Error fetching cursos:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const submitData = {
        ...formData,
        carga_horaria: parseInt(formData.carga_horaria),
      };

      if (editingCurso) {
        await axios.put(`${API}/courses/${editingCurso.id}`, submitData);
        toast({
          title: "Curso atualizado com sucesso!",
          description: "As informações do curso foram atualizadas.",
        });
      } else {
        await axios.post(`${API}/courses`, submitData);
        toast({
          title: "Curso criado com sucesso!",
          description: "O novo curso foi adicionado ao sistema.",
        });
      }

      setIsDialogOpen(false);
      setEditingCurso(null);
      resetForm();
      fetchCursos();
    } catch (error) {
      toast({
        title: editingCurso ? "Erro ao atualizar curso" : "Erro ao criar curso",
        description: error.response?.data?.detail || "Tente novamente",
        variant: "destructive",
      });
    }
  };

  const resetForm = () => {
    setFormData({
      nome: "",
      descricao: "",
      carga_horaria: "",
      categoria: "",
      pre_requisitos: "",
    });
  };

  const handleEdit = (curso) => {
    setEditingCurso(curso);
    setFormData({
      nome: curso.nome,
      descricao: curso.descricao || "",
      carga_horaria: curso.carga_horaria.toString(),
      categoria: curso.categoria || "",
      pre_requisitos: curso.pre_requisitos || "",
    });
    setIsDialogOpen(true);
  };

  const handleDelete = async (cursoId) => {
    if (window.confirm("Tem certeza que deseja desativar este curso?")) {
      try {
        await axios.delete(`${API}/courses/${cursoId}`);
        toast({
          title: "Curso desativado com sucesso!",
          description: "O curso foi desativado do sistema.",
        });
        fetchCursos();
      } catch (error) {
        toast({
          title: "Erro ao desativar curso",
          description: error.response?.data?.detail || "Tente novamente",
          variant: "destructive",
        });
      }
    }
  };

  const handleOpenDialog = () => {
    setEditingCurso(null);
    resetForm();
    setIsDialogOpen(true);
  };

  if (loading) return <div>Carregando...</div>;

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>Gerenciamento de Cursos</CardTitle>
            <CardDescription>
              Gerencie os cursos oferecidos pelo Instituto
            </CardDescription>
          </div>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button
                onClick={handleOpenDialog}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                Novo Curso
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>
                  {editingCurso ? "Editar Curso" : "Criar Novo Curso"}
                </DialogTitle>
                <DialogDescription>
                  {editingCurso
                    ? "Atualize os dados do curso"
                    : "Preencha os dados para criar um novo curso"}
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="nome">Nome do Curso</Label>
                  <Input
                    id="nome"
                    value={formData.nome}
                    onChange={(e) =>
                      setFormData({ ...formData, nome: e.target.value })
                    }
                    placeholder="Ex: Informática Básica"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="descricao">Descrição</Label>
                  <Textarea
                    id="descricao"
                    value={formData.descricao}
                    onChange={(e) =>
                      setFormData({ ...formData, descricao: e.target.value })
                    }
                    placeholder="Descreva o curso..."
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="carga_horaria">Carga Horária (horas)</Label>
                  <Input
                    id="carga_horaria"
                    type="number"
                    value={formData.carga_horaria}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        carga_horaria: e.target.value,
                      })
                    }
                    placeholder="Ex: 80"
                    min="1"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="categoria">Categoria</Label>
                  <Input
                    id="categoria"
                    value={formData.categoria}
                    onChange={(e) =>
                      setFormData({ ...formData, categoria: e.target.value })
                    }
                    placeholder="Ex: Tecnologia, Gestão"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="pre_requisitos">Pré-requisitos</Label>
                  <Textarea
                    id="pre_requisitos"
                    value={formData.pre_requisitos}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        pre_requisitos: e.target.value,
                      })
                    }
                    placeholder="Liste os pré-requisitos..."
                  />
                </div>

                <Button
                  type="submit"
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  <Save className="h-4 w-4 mr-2" />
                  {editingCurso ? "Atualizar Curso" : "Criar Curso"}
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </CardHeader>
      <CardContent>
        <div className="table-container">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Categoria</TableHead>
                <TableHead>Carga Horária</TableHead>
                <TableHead>Descrição</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {cursos.map((curso) => (
                <TableRow key={curso.id}>
                  <TableCell className="font-medium">{curso.nome}</TableCell>
                  <TableCell>
                    {curso.categoria && (
                      <Badge variant="outline">{curso.categoria}</Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center">
                      <Clock className="h-4 w-4 mr-1 text-gray-400" />
                      {curso.carga_horaria}h
                    </div>
                  </TableCell>
                  <TableCell className="max-w-xs truncate">
                    {curso.descricao || "-"}
                  </TableCell>
                  <TableCell>
                    <Badge variant={curso.ativo ? "default" : "secondary"}>
                      {curso.ativo ? "Ativo" : "Inativo"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleEdit(curso)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDelete(curso.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <div className="App">
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginRoute />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
          </Routes>
        </BrowserRouter>
        <Toaster />
      </div>
    </AuthProvider>
  );
}

// Route Components
const LoginRoute = () => {
  const { user, loading } = useAuth();

  if (loading) return <div>Carregando...</div>;
  if (user) return <Navigate to="/" replace />;

  return <Login />;
};

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) return <div>Carregando...</div>;
  if (!user) return <Navigate to="/login" replace />;

  return children;
};

export default App;
