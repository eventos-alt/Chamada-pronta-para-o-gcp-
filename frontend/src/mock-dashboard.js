// Dados mockados para dashboard IOS

export const mockAdminStats = {
  totalAlunos: 126,
  turmasAtivas: 6,
  presencaMedia: 71.3,
  alunosAtivos: 80,
  alunosEmRisco: 23,
  taxaEvasao: 18.3,
  totalEvasoes: 23,
  evasoesRecentes: 6
};

export const mockPerguntasNegocio = [
  {
    id: 'Q1',
    pergunta: 'Qual é o principal motivo de evasão nos últimos 30 dias?',
    resposta: 'OPTOU POR UM CURSO FORA DO IOS (1 caso, 16.7% do total)'
  },
  {
    id: 'Q2',
    pergunta: 'Qual categoria de motivo tem maior impacto?',
    resposta: 'Externo (3 casos, 50% do total)'
  },
  {
    id: 'Q3',
    pergunta: 'Qual curso apresenta maior taxa de evasão?',
    resposta: 'Zendesk (20.6% de evasão)'
  },
  {
    id: 'Q4',
    pergunta: 'Quantos alunos estão em risco de evasão (presença < 70%)?',
    resposta: '23 alunos (18.3% do total)'
  },
  {
    id: 'Q5',
    pergunta: 'A evasão está aumentando ou diminuindo?',
    resposta: 'Diminuiu em 2 casos comparado ao período anterior'
  },
  {
    id: 'Q6',
    pergunta: 'Qual o perfil médio de presença dos alunos em risco?',
    resposta: 'Taxa média de presença: 58.2%'
  },
  {
    id: 'Q7',
    pergunta: 'Conflitos com trabalho ou com estudos são mais frequentes?',
    resposta: 'Trabalho: 3 casos | Estudos: 2 casos | Trabalho é o maior conflito'
  }
];

export const mockEvasaoPorCategoria = [
  { categoria: 'Interno', total: 2, percentual: 33.3 },
  { categoria: 'Externo', total: 3, percentual: 50.0 },
  { categoria: 'Pessoal', total: 1, percentual: 16.7 }
];

export const mockEvasaoPorCurso = [
  { curso: 'Zendesk', taxa: 20.6, total: 13 },
  { curso: 'C6 Bank', taxa: 10.5, total: 3 },
  { curso: 'Power BI', taxa: 15.8, total: 5 },
  { curso: 'Analista de Dados', taxa: 8.2, total: 2 }
];

export const mockTopMotivosEvasao = [
  { motivo: 'Optou por curso fora do IOS', total: 1, percentual: 16.7 },
  { motivo: 'Conflito de horário com escola', total: 3, percentual: 50.0 },
  { motivo: 'Conflito entre curso e trabalho', total: 2, percentual: 33.3 },
  { motivo: 'Problemas de saúde', total: 1, percentual: 16.7 },
  { motivo: 'Sem retorno de contato', total: 1, percentual: 16.7 }
];

export const mockInsights = [
  {
    tipo: 'alerta',
    mensagem: 'A Turma Zendesk 001540 tem 14 alunos em risco (58% da turma). Recomenda-se intervenção imediata.'
  },
  {
    tipo: 'elogio',
    mensagem: 'A Turma 01 - C6 Bank mantém 91,1% de presença média. Excelente desempenho!'
  },
  {
    tipo: 'tendencia',
    mensagem: 'Taxa de evasão reduziu 8% comparado ao mês anterior. Tendência positiva!'
  }
];
