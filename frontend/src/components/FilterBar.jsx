import React, { useState, useEffect } from 'react';
import { X, Filter, ChevronDown } from 'lucide-react';
import { Button } from './ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Slider } from './ui/slider';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';

const FilterBar = ({ 
  filtros, 
  onFiltrosChange, 
  unidades = [], 
  cursos = [], 
  turmas = [],
  mostrarTodosOsFiltros = true 
}) => {
  const [filtrosAtivos, setFiltrosAtivos] = useState(filtros || {});
  const [mostrarAvancados, setMostrarAvancados] = useState(false);

  useEffect(() => {
    // Salvar filtros no localStorage
    localStorage.setItem('filtros_ios', JSON.stringify(filtrosAtivos));
    onFiltrosChange(filtrosAtivos);
  }, [filtrosAtivos]);

  useEffect(() => {
    // Carregar filtros salvos
    const filtrosSalvos = localStorage.getItem('filtros_ios');
    if (filtrosSalvos) {
      try {
        setFiltrosAtivos(JSON.parse(filtrosSalvos));
      } catch (e) {
        console.error('Erro ao carregar filtros', e);
      }
    }
  }, []);

  const aplicarFiltro = (key, value) => {
    setFiltrosAtivos(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const removerFiltro = (key) => {
    setFiltrosAtivos(prev => {
      const novo = { ...prev };
      delete novo[key];
      return novo;
    });
  };

  const limparFiltros = () => {
    setFiltrosAtivos({});
    localStorage.removeItem('filtros_ios');
  };

  const getChipLabel = (key, value) => {
    const labels = {
      unidade: 'Unidade',
      curso: 'Curso',
      turma: 'Turma',
      status: 'Status',
      presenca_min: 'Presença mín',
      presenca_max: 'Presença máx',
      categoria: 'Categoria',
      motivo: 'Motivo',
      periodo_dias: 'Período'
    };
    return `${labels[key] || key}: ${value}`;
  };

  const statusOpcoes = [
    { value: 'ativo', label: 'Ativo' },
    { value: 'em_risco', label: 'Em Risco' },
    { value: 'desistente', label: 'Desistente' }
  ];

  const categoriaOpcoes = [
    { value: 'externo', label: 'Externo' },
    { value: 'interno', label: 'Interno' },
    { value: 'pessoal', label: 'Pessoal' },
    { value: 'financeiro', label: 'Financeiro' },
    { value: 'desconhecido', label: 'Desconhecido' }
  ];

  const periodoOpcoes = [
    { value: '7', label: 'Última semana' },
    { value: '30', label: 'Último mês' },
    { value: '90', label: 'Último trimestre' }
  ];

  const contarFiltrosAtivos = () => {
    return Object.keys(filtrosAtivos).length;
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-4 space-y-3" data-testid="filter-bar">
      {/* Linha de filtros principais */}
      <div className="flex flex-wrap gap-3 items-center">
        <div className="flex items-center gap-2 text-gray-700 font-medium">
          <Filter className="w-5 h-5" />
          <span>Filtros</span>
          {contarFiltrosAtivos() > 0 && (
            <Badge variant="secondary" className="ml-1">
              {contarFiltrosAtivos()}
            </Badge>
          )}
        </div>

        {/* Unidade */}
        {mostrarTodosOsFiltros && unidades.length > 0 && (
          <Select 
            value={filtrosAtivos.unidade || ''} 
            onValueChange={(value) => aplicarFiltro('unidade', value)}
          >
            <SelectTrigger className="w-[180px]" data-testid="filter-unidade">
              <SelectValue placeholder="Unidade" />
            </SelectTrigger>
            <SelectContent>
              {unidades.map(u => (
                <SelectItem key={u.id} value={u.nome}>{u.nome}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}

        {/* Curso */}
        {mostrarTodosOsFiltros && cursos.length > 0 && (
          <Select 
            value={filtrosAtivos.curso || ''} 
            onValueChange={(value) => aplicarFiltro('curso', value)}
          >
            <SelectTrigger className="w-[180px]" data-testid="filter-curso">
              <SelectValue placeholder="Curso" />
            </SelectTrigger>
            <SelectContent>
              {cursos.map(c => (
                <SelectItem key={c} value={c}>{c}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}

        {/* Turma */}
        {turmas.length > 0 && (
          <Select 
            value={filtrosAtivos.turma || ''} 
            onValueChange={(value) => aplicarFiltro('turma', value)}
          >
            <SelectTrigger className="w-[200px]" data-testid="filter-turma">
              <SelectValue placeholder="Turma" />
            </SelectTrigger>
            <SelectContent>
              {turmas.map(t => (
                <SelectItem key={t.id} value={t.id}>{t.nome}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}

        {/* Status */}
        <Select 
          value={filtrosAtivos.status || ''} 
          onValueChange={(value) => aplicarFiltro('status', value)}
        >
          <SelectTrigger className="w-[150px]" data-testid="filter-status">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            {statusOpcoes.map(s => (
              <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* Período */}
        {mostrarTodosOsFiltros && (
          <Select 
            value={filtrosAtivos.periodo_dias || ''} 
            onValueChange={(value) => aplicarFiltro('periodo_dias', value)}
          >
            <SelectTrigger className="w-[180px]" data-testid="filter-periodo">
              <SelectValue placeholder="Período" />
            </SelectTrigger>
            <SelectContent>
              {periodoOpcoes.map(p => (
                <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}

        {/* Botão Filtros Avançados */}
        {mostrarTodosOsFiltros && (
          <Popover open={mostrarAvancados} onOpenChange={setMostrarAvancados}>
            <PopoverTrigger asChild>
              <Button variant="outline" size="sm" data-testid="advanced-filters-btn">
                + Filtros Avançados
                <ChevronDown className="w-4 h-4 ml-1" />
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-80" align="start">
              <div className="space-y-4">
                <h4 className="font-medium text-sm">Filtros Avançados</h4>
                
                {/* Categoria de Evasão */}
                <div>
                  <label className="text-sm text-gray-600 mb-1 block">Categoria</label>
                  <Select 
                    value={filtrosAtivos.categoria || ''} 
                    onValueChange={(value) => aplicarFiltro('categoria', value)}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Selecione" />
                    </SelectTrigger>
                    <SelectContent>
                      {categoriaOpcoes.map(c => (
                        <SelectItem key={c.value} value={c.value}>{c.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Taxa de Presença */}
                <div>
                  <label className="text-sm text-gray-600 mb-2 block">
                    Taxa de Presença: {filtrosAtivos.presenca_min || 0}% - {filtrosAtivos.presenca_max || 100}%
                  </label>
                  <div className="space-y-2">
                    <Slider
                      value={[filtrosAtivos.presenca_min || 0]}
                      onValueChange={([value]) => aplicarFiltro('presenca_min', value)}
                      max={100}
                      step={5}
                      className="w-full"
                    />
                    <Slider
                      value={[filtrosAtivos.presenca_max || 100]}
                      onValueChange={([value]) => aplicarFiltro('presenca_max', value)}
                      max={100}
                      step={5}
                      className="w-full"
                    />
                  </div>
                </div>
              </div>
            </PopoverContent>
          </Popover>
        )}

        {/* Botão Limpar */}
        {contarFiltrosAtivos() > 0 && (
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={limparFiltros}
            data-testid="clear-filters-btn"
          >
            Limpar Filtros
          </Button>
        )}
      </div>

      {/* Chips de filtros ativos */}
      {contarFiltrosAtivos() > 0 && (
        <div className="flex flex-wrap gap-2">
          {Object.entries(filtrosAtivos).map(([key, value]) => (
            <Badge 
              key={key} 
              variant="secondary" 
              className="flex items-center gap-1 px-3 py-1"
              data-testid={`filter-chip-${key}`}
            >
              {getChipLabel(key, value)}
              <button 
                onClick={() => removerFiltro(key)}
                className="ml-1 hover:text-red-600 transition-colors"
              >
                <X className="w-3 h-3" />
              </button>
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
};

export default FilterBar;
