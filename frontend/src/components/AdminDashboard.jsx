import React, { useState, useEffect } from 'react';
import { Users, TrendingUp, AlertCircle, Award, RefreshCw, Download, UserX } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import FilterBar from './FilterBar';
import EvasaoModal from './EvasaoModal';
import InsightsPanel from './InsightsPanel';
import SkeletonLoader from './SkeletonLoader';
import { listarUnidades, listarTurmas, listarAlunos, obterDashboardAdmin } from '@/lib/api';
import { toast } from 'sonner';

const AdminDashboard = () => {
  const [filtros, setFiltros] = useState({});
  const [unidades, setUnidades] = useState([]);
  const [turmas, setTurmas] = useState([]);
  const [cursos, setCursos] = useState([]);
  const [alunos, setAlunos] = useState([]);
  const [dashboardData, setDashboardData] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [carregandoTabela, setCarregandoTabela] = useState(false);
  const [alunoSelecionado, setAlunoSelecionado] = useState(null);
  const [modalEvasaoAberto, setModalEvasaoAberto] = useState(false);

  useEffect(() => {
    carregarDadosIniciais();
  }, []);

  useEffect(() => {
    carregarDados();
  }, [filtros]);

  const carregarDadosIniciais = async () => {
    try {
      const [unidadesData, turmasData] = await Promise.all([
        listarUnidades(),
        listarTurmas()
      ]);
      
      setUnidades(unidadesData);
      setTurmas(turmasData);
      
      // Extrair cursos únicos
      const cursosUnicos = [...new Set(turmasData.map(t => t.curso))];
      setCursos(cursosUnicos);
    } catch (error) {
      console.error('Erro ao carregar dados iniciais:', error);
      toast.error('Erro ao carregar dados iniciais');
    }
  };

  const carregarDados = async () => {
    try {
      setCarregandoTabela(true);
      
      const [alunosData, dashData] = await Promise.all([
        listarAlunos(filtros),
        obterDashboardAdmin(filtros)
      ]);
      
      setAlunos(alunosData);
      setDashboardData(dashData);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      toast.error('Erro ao carregar dados');
    } finally {
      setCarregando(false);
      setCarregandoTabela(false);
    }
  };

  const abrirModalEvasao = (aluno) => {
    setAlunoSelecionado(aluno);
    setModalEvasaoAberto(true);
  };

  const handleEvasaoRegistrada = () => {
    carregarDados();
    toast.success('Evasão registrada com sucesso!');
  };

  const getStatusBadgeVariant = (status) => {
    switch (status) {
      case 'ativo': return 'default';
      case 'em_risco': return 'warning';
      case 'desistente': return 'destructive';
      default: return 'secondary';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'ativo': return 'Ativo';
      case 'em_risco': return 'Em Risco';
      case 'desistente': return 'Desistente';
      default: return status;
    }
  };

  const getPresencaColor = (presenca) => {
    if (presenca >= 80) return 'text-green-600 font-semibold';
    if (presenca >= 70) return 'text-yellow-600 font-semibold';
    return 'text-red-600 font-semibold';
  };

  return (
    <div className="p-6" data-testid="admin-dashboard">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Cabeçalho */}
        <div className="flex justify-between items-center animate-fade-in-up">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Painel Administrativo</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">Sistema IOS - Gestão de Presença e Evasão</p>
          </div>
          <div className="flex gap-3">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={carregarDados} 
              data-testid="refresh-btn"
              className="hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Atualizar
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              data-testid="export-btn"
              className="hover:bg-green-50 dark:hover:bg-green-900/20 transition-all"
            >
              <Download className="w-4 h-4 mr-2" />
              Exportar
            </Button>
          </div>
        </div>

        {/* Filtros */}
        <div className="animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
          <FilterBar 
            filtros={filtros}
            onFiltrosChange={setFiltros}
            unidades={unidades}
            cursos={cursos}
            turmas={turmas}
          />
        </div>

        {/* Cards de Métricas */}
        {carregando ? (
          <SkeletonLoader type="cards" count={4} />
        ) : dashboardData && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 stagger-children">
            <Card data-testid="metric-total-alunos" className="card-interactive hover:shadow-xl transition-all duration-300 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-700">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-blue-900 dark:text-blue-100">Total de Alunos</CardTitle>
                <Users className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-700 dark:text-blue-300 counter-value">{dashboardData.metricas_gerais.total_alunos}</div>
                <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                  {dashboardData.metricas_gerais.total_turmas} turmas ativas
                </p>
              </CardContent>
            </Card>

            <Card data-testid="metric-presenca-media" className="card-interactive hover:shadow-xl transition-all duration-300 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200 dark:border-green-700">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-green-900 dark:text-green-100">Presença Média</CardTitle>
                <Award className="h-5 w-5 text-green-600 dark:text-green-400" />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-700 dark:text-green-300 counter-value">
                  {dashboardData.metricas_gerais.presenca_media}%
                </div>
                <p className="text-xs text-green-600 dark:text-green-400 mt-1">
                  {dashboardData.metricas_gerais.alunos_ativos} alunos ativos
                </p>
              </CardContent>
            </Card>

            <Card data-testid="metric-alunos-risco" className="card-interactive hover:shadow-xl transition-all duration-300 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 border-orange-200 dark:border-orange-700">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-orange-900 dark:text-orange-100">Alunos em Risco</CardTitle>
                <AlertCircle className="h-5 w-5 text-orange-600 dark:text-orange-400" />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-orange-700 dark:text-orange-300 counter-value">
                  {dashboardData.metricas_gerais.alunos_em_risco}
                </div>
                <p className="text-xs text-orange-600 dark:text-orange-400 mt-1">
                  Presença &lt; 70%
                </p>
              </CardContent>
            </Card>

            <Card data-testid="metric-taxa-evasao" className="card-interactive hover:shadow-xl transition-all duration-300 bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 border-red-200 dark:border-red-700">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-red-900 dark:text-red-100">Taxa de Evasão</CardTitle>
                <UserX className="h-5 w-5 text-red-600 dark:text-red-400" />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-red-700 dark:text-red-300 counter-value">
                  {dashboardData.metricas_gerais.taxa_evasao}%
                </div>
                <p className="text-xs text-red-600 dark:text-red-400 mt-1">
                  {dashboardData.metricas_gerais.alunos_desistentes} desistências
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Insights */}
        <div className="animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
          <InsightsPanel filtros={filtros} />
        </div>

        {/* Tabela de Alunos */}
        <Card data-testid="alunos-table-card" className="animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
          <CardHeader>
            <CardTitle>Alunos ({alunos.length})</CardTitle>
          </CardHeader>
          <CardContent>
            {carregandoTabela ? (
              <div className="flex justify-center items-center py-12">
                <RefreshCw className="w-8 h-8 animate-spin text-gray-400" />
              </div>
            ) : alunos.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                Nenhum aluno encontrado com os filtros aplicados
              </div>
            ) : (
              <div className="rounded-md border overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-gray-50 dark:bg-gray-800">
                      <TableHead className="font-semibold">Nome</TableHead>
                      <TableHead className="font-semibold">Turma</TableHead>
                      <TableHead className="font-semibold">Status</TableHead>
                      <TableHead className="text-right font-semibold">Presença</TableHead>
                      <TableHead className="text-right font-semibold">Faltas</TableHead>
                      <TableHead className="font-semibold">Ações</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {alunos.map((aluno, index) => {
                      const turma = turmas.find(t => t.id === aluno.id_turma);
                      return (
                        <TableRow 
                          key={aluno.id} 
                          data-testid={`aluno-row-${aluno.id}`}
                          className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                          style={{ animationDelay: `${index * 0.05}s` }}
                        >
                          <TableCell className="font-medium">{aluno.nome}</TableCell>
                          <TableCell>
                            <span className="text-sm text-gray-600 dark:text-gray-400">
                              {turma ? turma.nome : aluno.id_turma}
                            </span>
                          </TableCell>
                          <TableCell>
                            <Badge variant={getStatusBadgeVariant(aluno.status)}>
                              {getStatusLabel(aluno.status)}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-right">
                            <span className={getPresencaColor(aluno.presenca_total)}>
                              {aluno.presenca_total}%
                            </span>
                          </TableCell>
                          <TableCell className="text-right">{aluno.faltas}</TableCell>
                          <TableCell>
                            {aluno.status !== 'desistente' && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => abrirModalEvasao(aluno)}
                                data-testid={`registrar-evasao-btn-${aluno.id}`}
                                className="hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20 transition-all"
                              >
                                Registrar Evasão
                              </Button>
                            )}
                            {aluno.status === 'desistente' && aluno.motivo_evasao && (
                              <span className="text-xs text-gray-500 dark:text-gray-400 italic">
                                {aluno.motivo_evasao.substring(0, 30)}...
                              </span>
                            )}
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Modal de Evasão */}
      {alunoSelecionado && (
        <EvasaoModal
          aluno={alunoSelecionado}
          aberto={modalEvasaoAberto}
          onFechar={() => {
            setModalEvasaoAberto(false);
            setAlunoSelecionado(null);
          }}
          onSucesso={handleEvasaoRegistrada}
        />
      )}
    </div>
  );
};

export default AdminDashboard;