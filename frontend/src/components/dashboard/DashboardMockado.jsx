import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Button } from '../ui/button';
import { Users, Percent, AlertTriangle, TrendingDown, RefreshCw, Download, Lightbulb, TrendingUp, Award, X } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { mockAdminStats, mockPerguntasNegocio, mockEvasaoPorCategoria, mockEvasaoPorCurso, mockTopMotivosEvasao, mockInsights } from '../../mock-dashboard';

const COLORS = {
  interno: '#f59e0b',
  externo: '#ef4444',
  pessoal: '#8b5cf6'
};

const MetricCard = ({ title, value, icon: Icon, variant, trendValue }) => {
  const variants = {
    info: 'from-blue-50 to-cyan-50 border-blue-200',
    success: 'from-green-50 to-emerald-50 border-green-200',
    warning: 'from-yellow-50 to-orange-50 border-orange-200',
    danger: 'from-red-50 to-pink-50 border-red-200'
  };

  const iconColors = {
    info: 'text-blue-600',
    success: 'text-green-600',
    warning: 'text-orange-600',
    danger: 'text-red-600'
  };

  return (
    <Card className={`bg-gradient-to-br ${variants[variant]} border-2 card-interactive`}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <div className={`p-2 rounded-lg bg-white/50`}>
            <Icon className={`h-5 w-5 ${iconColors[variant]}`} />
          </div>
        </div>
        <p className="text-3xl font-bold text-gray-900 counter-value">{value}</p>
        {trendValue && (
          <p className="text-sm text-gray-500 mt-2">{trendValue}</p>
        )}
      </CardContent>
    </Card>
  );
};

const DashboardMockado = () => {
  const [filtrosAtivos, setFiltrosAtivos] = useState([]);

  return (
    <div className="space-y-6 animate-fade-in-up">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Painel Administrativo</h2>
          <p className="text-gray-600 mt-1">Sistema IOS - Gestão de Presença e Evasão</p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" size="sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Atualizar
          </Button>
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Exportar
          </Button>
        </div>
      </div>

      {/* 4 Cards Principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 stagger-children">
        <MetricCard
          title="Total de Alunos"
          value={mockAdminStats.totalAlunos}
          icon={Users}
          variant="info"
          trendValue={`${mockAdminStats.turmasAtivas} turmas ativas`}
        />
        <MetricCard
          title="Presença Média"
          value={`${mockAdminStats.presencaMedia}%`}
          icon={Percent}
          variant="success"
          trendValue={`${mockAdminStats.alunosAtivos} alunos ativos`}
        />
        <MetricCard
          title="Alunos em Risco"
          value={mockAdminStats.alunosEmRisco}
          icon={AlertTriangle}
          variant="warning"
          trendValue="Presença < 70%"
        />
        <MetricCard
          title="Taxa de Evasão"
          value={`${mockAdminStats.taxaEvasao}%`}
          icon={TrendingDown}
          variant="danger"
          trendValue={`${mockAdminStats.totalEvasoes} desistências`}
        />
      </div>

      {/* Insights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {mockInsights.map((insight, idx) => {
          const tipos = {
            alerta: { bg: 'bg-red-50 border-red-200', icon: AlertTriangle, color: 'text-red-600' },
            elogio: { bg: 'bg-green-50 border-green-200', icon: Award, color: 'text-green-600' },
            tendencia: { bg: 'bg-blue-50 border-blue-200', icon: TrendingUp, color: 'text-blue-600' }
          };
          const config = tipos[insight.tipo];
          const Icon = config.icon;

          return (
            <Card key={idx} className={`${config.bg} border-2`}>
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <Icon className={`w-5 h-5 ${config.color} mt-0.5`} />
                  <p className="text-sm text-gray-700">{insight.mensagem}</p>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Cards Grandes Coloridos */}
      <Card>
        <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50">
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-yellow-500" />
              Insights e Análises Inteligentes
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-normal text-gray-600">6 evasões analisadas</span>
              <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                Tendência: Em baixa
              </span>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-6 text-white shadow-lg">
              <div className="flex items-center justify-between mb-2">
                <Users className="w-8 h-8 opacity-80" />
                <span className="text-4xl font-bold">{mockAdminStats.totalAlunos}</span>
              </div>
              <p className="text-sm opacity-90">Total de Alunos</p>
            </div>

            <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg p-6 text-white shadow-lg">
              <div className="flex items-center justify-between mb-2">
                <AlertTriangle className="w-8 h-8 opacity-80" />
                <span className="text-4xl font-bold">{mockAdminStats.alunosEmRisco}</span>
              </div>
              <p className="text-sm opacity-90">Alunos em Risco</p>
            </div>

            <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-lg p-6 text-white shadow-lg">
              <div className="flex items-center justify-between mb-2">
                <TrendingDown className="w-8 h-8 opacity-80" />
                <span className="text-4xl font-bold">{mockAdminStats.evasoesRecentes}</span>
              </div>
              <p className="text-sm opacity-90">Total de Evasões</p>
            </div>

            <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-6 text-white shadow-lg">
              <div className="flex items-center justify-between mb-2">
                <Percent className="w-8 h-8 opacity-80" />
                <span className="text-4xl font-bold">{mockAdminStats.taxaEvasao.toFixed(1)}%</span>
              </div>
              <p className="text-sm opacity-90">Taxa de Evasão</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Perguntas de Negócio */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-yellow-500" />
            Perguntas de Negócio Automatizadas
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {mockPerguntasNegocio.map((item) => (
            <div key={item.id} className="border-l-4 border-blue-500 bg-gradient-to-r from-blue-50 to-indigo-50 p-4 rounded-r-lg">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0">
                  {item.id}
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-gray-900 mb-2">{item.pergunta}</p>
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 flex items-start gap-2">
                    <Lightbulb className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-gray-700">{item.resposta}</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Gráficos */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Evasão por Categoria */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Evasão por Categoria</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={mockEvasaoPorCategoria}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ categoria, percentual }) => `${categoria}: ${percentual.toFixed(1)}%`}
                  outerRadius={80}
                  dataKey="total"
                  animationDuration={1000}
                >
                  {mockEvasaoPorCategoria.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[entry.categoria.toLowerCase()]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Taxa por Curso */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Taxa de Evasão por Curso</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={mockEvasaoPorCurso}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis dataKey="curso" tick={{ fontSize: 11 }} angle={-15} textAnchor="end" height={60} />
                <YAxis domain={[0, 'auto']} />
                <Tooltip formatter={(value) => `${value}%`} />
                <Bar dataKey="taxa" fill="#ef4444" radius={[8, 8, 0, 0]} animationDuration={1200} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Top Motivos */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Top 5 Motivos de Evasão</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={mockTopMotivosEvasao} layout="vertical" margin={{ left: 100 }}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis type="number" />
                <YAxis type="category" dataKey="motivo" tick={{ fontSize: 10 }} width={90} />
                <Tooltip />
                <Bar dataKey="total" fill="#8b5cf6" radius={[0, 8, 8, 0]} animationDuration={1200} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DashboardMockado;
