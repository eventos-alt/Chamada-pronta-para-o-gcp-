import React, { useState, useEffect } from 'react';
import { Lightbulb, TrendingUp, TrendingDown, Minus, RefreshCw, ChevronDown, ChevronUp, Users, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { obterInsights } from '@/lib/api';
import { toast } from 'sonner';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';

const COLORS = {
  externo: '#ef4444',
  interno: '#f59e0b', 
  pessoal: '#8b5cf6',
  financeiro: '#10b981',
  desconhecido: '#6b7280'
};

const InsightsPanel = ({ filtros }) => {
  const [insights, setInsights] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [expandido, setExpandido] = useState(true);
  const [secaoExpandida, setSecaoExpandida] = useState({
    perguntas: true,
    categorias: true,
    cursos: true,
    motivos: true
  });

  useEffect(() => {
    carregarInsights();
  }, [filtros]);

  const carregarInsights = async () => {
    try {
      setCarregando(true);
      const data = await obterInsights(filtros);
      setInsights(data);
    } catch (error) {
      console.error('Erro ao carregar insights:', error);
      toast.error('Erro ao carregar insights');
    } finally {
      setCarregando(false);
    }
  };

  const getTendenciaIcon = (tendencia) => {
    switch (tendencia) {
      case 'alta': return <TrendingUp className="w-5 h-5 text-red-500" />;
      case 'baixa': return <TrendingDown className="w-5 h-5 text-green-500" />;
      default: return <Minus className="w-5 h-5 text-gray-500" />;
    }
  };

  const getTendenciaLabel = (tendencia) => {
    switch (tendencia) {
      case 'alta': return 'Em alta';
      case 'baixa': return 'Em baixa';
      default: return 'Estável';
    }
  };

  const getTendenciaColor = (tendencia) => {
    switch (tendencia) {
      case 'alta': return 'bg-red-100 text-red-800';
      case 'baixa': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const toggleSecao = (secao) => {
    setSecaoExpandida(prev => ({
      ...prev,
      [secao]: !prev[secao]
    }));
  };

  if (carregando) {
    return (
      <Card data-testid="insights-panel-loading">
        <CardContent className="flex justify-center items-center py-12">
          <RefreshCw className="w-8 h-8 animate-spin text-gray-400" />
        </CardContent>
      </Card>
    );
  }

  if (!insights) {
    return null;
  }

  // Preparar dados para gráficos
  const categoriasData = insights.evasao_por_categoria.map(cat => ({
    name: cat.categoria.charAt(0).toUpperCase() + cat.categoria.slice(1),
    value: cat.total,
    percentual: cat.percentual
  }));

  const cursosData = insights.evasao_por_curso.map(curso => ({
    name: curso.curso,
    taxa: parseFloat(curso.taxa.toFixed(1)),
    total: curso.total
  }));

  const motivosData = insights.principais_motivos.slice(0, 5).map(motivo => ({
    name: motivo.motivo.length > 30 ? motivo.motivo.substring(0, 30) + '...' : motivo.motivo,
    total: motivo.total,
    percentual: motivo.percentual
  }));

  return (
    <Card data-testid="insights-panel" className="overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-yellow-500" />
            <CardTitle>Insights e Análises Inteligentes</CardTitle>
            <Badge variant="outline" className="ml-2">
              {insights.resumo.total_evasoes} evasões analisadas
            </Badge>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">Tendência:</span>
              <Badge className={getTendenciaColor(insights.resumo.tendencia)}>
                {getTendenciaIcon(insights.resumo.tendencia)}
                <span className="ml-1">{getTendenciaLabel(insights.resumo.tendencia)}</span>
              </Badge>
            </div>
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setExpandido(!expandido)}
              data-testid="toggle-insights-btn"
            >
              {expandido ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </Button>
          </div>
        </div>
      </CardHeader>

      {expandido && (
        <CardContent className="space-y-6 p-6">
          {/* Resumo em Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 animate-fade-in-up">
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg p-4 text-white shadow-lg">
              <div className="flex items-center justify-between">
                <Users className="w-8 h-8 opacity-80" />
                <span className="text-3xl font-bold">{insights.resumo.total_alunos}</span>
              </div>
              <p className="text-sm mt-2 opacity-90">Total de Alunos</p>
            </div>

            <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg p-4 text-white shadow-lg">
              <div className="flex items-center justify-between">
                <AlertTriangle className="w-8 h-8 opacity-80" />
                <span className="text-3xl font-bold">{insights.resumo.alunos_em_risco}</span>
              </div>
              <p className="text-sm mt-2 opacity-90">Alunos em Risco</p>
            </div>

            <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-lg p-4 text-white shadow-lg">
              <div className="flex items-center justify-between">
                <TrendingDown className="w-8 h-8 opacity-80" />
                <span className="text-3xl font-bold">{insights.resumo.total_evasoes}</span>
              </div>
              <p className="text-sm mt-2 opacity-90">Total de Evasões</p>
            </div>

            <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg p-4 text-white shadow-lg">
              <div className="flex items-center justify-between">
                <TrendingUp className="w-8 h-8 opacity-80" />
                <span className="text-3xl font-bold">{insights.resumo.taxa_evasao.toFixed(1)}%</span>
              </div>
              <p className="text-sm mt-2 opacity-90">Taxa de Evasão</p>
            </div>
          </div>

          <Separator />

          {/* Perguntas de Negócio */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-yellow-500" />
                Perguntas de Negócio Automatizadas
              </h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => toggleSecao('perguntas')}
              >
                {secaoExpandida.perguntas ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </Button>
            </div>
            
            {secaoExpandida.perguntas && (
              <div className="space-y-3 animate-fade-in-up">
                {insights.perguntas_negocio.map((pn, index) => (
                  <div 
                    key={index} 
                    className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg p-4 border border-blue-100 dark:border-blue-800 hover:shadow-md transition-all duration-200"
                    data-testid={`pergunta-negocio-${index}`}
                  >
                    <p className="font-medium text-gray-900 dark:text-white mb-2 flex items-start gap-2">
                      <span className="text-blue-500 font-bold">Q{index + 1}:</span>
                      {pn.pergunta}
                    </p>
                    <p className="text-gray-700 dark:text-gray-300 text-sm bg-white dark:bg-gray-800 rounded px-3 py-2 border border-gray-200 dark:border-gray-700">
                      💡 {pn.resposta}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          <Separator />

          {/* Gráficos */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Gráfico de Pizza - Categorias */}
            {categoriasData.length > 0 && (
              <Card className="overflow-hidden">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base">Evasão por Categoria</CardTitle>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleSecao('categorias')}
                    >
                      {secaoExpandida.categorias ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </Button>
                  </div>
                </CardHeader>
                {secaoExpandida.categorias && (
                  <CardContent>
                    <ResponsiveContainer width="100%" height={250}>
                      <PieChart>
                        <Pie
                          data={categoriasData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percentual }) => `${name}: ${percentual.toFixed(1)}%`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                          animationDuration={1000}
                        >
                          {categoriasData.map((entry, index) => (
                            <Cell 
                              key={`cell-${index}`} 
                              fill={COLORS[entry.name.toLowerCase()] || '#6b7280'} 
                            />
                          ))}
                        </Pie>
                        <Tooltip 
                          contentStyle={{ 
                            backgroundColor: 'rgba(255, 255, 255, 0.95)',
                            border: '1px solid #e5e7eb',
                            borderRadius: '8px',
                            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
                          }}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                )}
              </Card>
            )}

            {/* Gráfico de Barras - Cursos */}
            {cursosData.length > 0 && (
              <Card className="overflow-hidden">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base">Taxa de Evasão por Curso</CardTitle>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleSecao('cursos')}
                    >
                      {secaoExpandida.cursos ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </Button>
                  </div>
                </CardHeader>
                {secaoExpandida.cursos && (
                  <CardContent>
                    <ResponsiveContainer width="100%" height={250}>
                      <BarChart data={cursosData}>
                        <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                        <XAxis 
                          dataKey="name" 
                          tick={{ fontSize: 12 }}
                          angle={-15}
                          textAnchor="end"
                          height={60}
                        />
                        <YAxis 
                          domain={[0, 'auto']}
                          label={{ value: 'Taxa (%)', angle: -90, position: 'insideLeft' }}
                        />
                        <Tooltip 
                          contentStyle={{ 
                            backgroundColor: 'rgba(255, 255, 255, 0.95)',
                            border: '1px solid #e5e7eb',
                            borderRadius: '8px',
                            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
                          }}
                          formatter={(value, name) => {
                            if (name === 'taxa') return [`${value}%`, 'Taxa de Evasão'];
                            return [value, name];
                          }}
                        />
                        <Bar 
                          dataKey="taxa" 
                          fill="#ef4444" 
                          radius={[8, 8, 0, 0]}
                          animationDuration={1200}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                )}
              </Card>
            )}
          </div>

          {/* Principais Motivos */}
          {insights.principais_motivos.length > 0 && (
            <Card className="overflow-hidden">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">Top 5 Motivos de Evasão</CardTitle>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => toggleSecao('motivos')}
                  >
                    {secaoExpandida.motivos ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </Button>
                </div>
              </CardHeader>
              {secaoExpandida.motivos && (
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart 
                      data={motivosData} 
                      layout="vertical"
                      margin={{ left: 150 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                      <XAxis type="number" />
                      <YAxis 
                        type="category" 
                        dataKey="name" 
                        tick={{ fontSize: 11 }}
                        width={140}
                      />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'rgba(255, 255, 255, 0.95)',
                          border: '1px solid #e5e7eb',
                          borderRadius: '8px',
                          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
                        }}
                        formatter={(value, name) => {
                          if (name === 'total') return [value, 'Casos'];
                          if (name === 'percentual') return [`${value.toFixed(1)}%`, 'Percentual'];
                          return [value, name];
                        }}
                      />
                      <Bar 
                        dataKey="total" 
                        fill="#3b82f6" 
                        radius={[0, 8, 8, 0]}
                        animationDuration={1200}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              )}
            </Card>
          )}

          {/* Botão Atualizar */}
          <div className="flex justify-center pt-4">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={carregarInsights}
              data-testid="refresh-insights-btn"
              className="hover:bg-blue-50 dark:hover:bg-blue-900/20"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Atualizar Insights
            </Button>
          </div>
        </CardContent>
      )}
    </Card>
  );
};

export default InsightsPanel;