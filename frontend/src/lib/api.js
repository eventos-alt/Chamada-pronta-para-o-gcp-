import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API = `${BACKEND_URL}/api`;

// ============================================================================
// UNIDADES
// ============================================================================

export const listarUnidades = async () => {
  const response = await axios.get(`${API}/unidades`);
  return response.data;
};

// ============================================================================
// PROFESSORES
// ============================================================================

export const listarProfessores = async () => {
  const response = await axios.get(`${API}/professores`);
  return response.data;
};

// ============================================================================
// TURMAS
// ============================================================================

export const listarTurmas = async (filtros = {}) => {
  const params = new URLSearchParams();
  if (filtros.unidade) params.append('unidade', filtros.unidade);
  if (filtros.curso) params.append('curso', filtros.curso);
  if (filtros.professor) params.append('professor', filtros.professor);
  
  const response = await axios.get(`${API}/turmas?${params.toString()}`);
  return response.data;
};

export const obterTurma = async (id) => {
  const response = await axios.get(`${API}/turmas/${id}`);
  return response.data;
};

// ============================================================================
// ALUNOS
// ============================================================================

export const listarAlunos = async (filtros = {}) => {
  const params = new URLSearchParams();
  if (filtros.unidade) params.append('unidade', filtros.unidade);
  if (filtros.curso) params.append('curso', filtros.curso);
  if (filtros.turma) params.append('turma', filtros.turma);
  if (filtros.status) params.append('status', filtros.status);
  if (filtros.presenca_min !== undefined) params.append('presenca_min', filtros.presenca_min);
  if (filtros.presenca_max !== undefined) params.append('presenca_max', filtros.presenca_max);
  
  const response = await axios.get(`${API}/alunos?${params.toString()}`);
  return response.data;
};

export const obterAluno = async (id) => {
  const response = await axios.get(`${API}/alunos/${id}`);
  return response.data;
};

export const atualizarStatusAluno = async (id, status) => {
  const response = await axios.patch(`${API}/alunos/${id}/status?status=${status}`);
  return response.data;
};

// ============================================================================
// EVASÕES
// ============================================================================

export const listarEvasoes = async (filtros = {}) => {
  const params = new URLSearchParams();
  if (filtros.unidade) params.append('unidade', filtros.unidade);
  if (filtros.curso) params.append('curso', filtros.curso);
  if (filtros.turma) params.append('turma', filtros.turma);
  if (filtros.motivo) params.append('motivo', filtros.motivo);
  if (filtros.categoria) params.append('categoria', filtros.categoria);
  if (filtros.data_inicio) params.append('data_inicio', filtros.data_inicio);
  if (filtros.data_fim) params.append('data_fim', filtros.data_fim);
  
  const response = await axios.get(`${API}/evasoes?${params.toString()}`);
  return response.data;
};

export const registrarEvasao = async (dados) => {
  const response = await axios.post(`${API}/evasoes`, dados);
  return response.data;
};

export const listarMotivosEvasao = async () => {
  const response = await axios.get(`${API}/motivos-evasao`);
  return response.data;
};

// ============================================================================
// INSIGHTS
// ============================================================================

export const obterInsights = async (filtros = {}) => {
  const params = new URLSearchParams();
  if (filtros.unidade) params.append('unidade', filtros.unidade);
  if (filtros.curso) params.append('curso', filtros.curso);
  if (filtros.periodo_dias) params.append('periodo_dias', filtros.periodo_dias);
  
  const response = await axios.get(`${API}/insights?${params.toString()}`);
  return response.data;
};

// ============================================================================
// DASHBOARD
// ============================================================================

export const obterDashboardAdmin = async (filtros = {}) => {
  const params = new URLSearchParams();
  if (filtros.unidade) params.append('unidade', filtros.unidade);
  if (filtros.curso) params.append('curso', filtros.curso);
  
  const response = await axios.get(`${API}/dashboard/admin?${params.toString()}`);
  return response.data;
};

export const obterDashboardProfessor = async (idProfessor) => {
  const response = await axios.get(`${API}/dashboard/professor/${idProfessor}`);
  return response.data;
};
