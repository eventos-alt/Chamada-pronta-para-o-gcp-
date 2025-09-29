# 📊 Sistema IOS - Exportação CSV e Notificações

## 🚀 Novas Funcionalidades Implementadas

### 1. 📋 CSV Detalhado de Presença

O sistema agora gera relatórios CSV completos com todos os campos necessários para gestão acadêmica:

**Campos incluídos:**

- **Aluno**: Nome completo do estudante
- **CPF**: Documento do aluno
- **Matricula**: Número de matrícula (ou ID se não houver)
- **Turma**: Nome da turma (ex: "1ºB Informática")
- **Curso**: Nome do curso/disciplina
- **Data**: Data da chamada (AAAA-MM-DD)
- **Hora_Inicio**: Horário de início da aula
- **Hora_Fim**: Horário de término da aula
- **Status**: Presente, Ausente, Atrasado, Justificado
- **Hora_Registro**: Horário exato que o aluno foi marcado presente
- **Professor**: Nome do instrutor responsável
- **Unidade**: Nome da unidade/escola
- **Observacoes**: Justificativas e observações

### 2. 🔔 Sistema de Notificações

Sistema proativo que monitora chamadas pendentes:

**Funcionalidades:**

- ✅ Notificação no header do sistema (ícone de sino)
- ✅ Contador de chamadas pendentes em tempo real
- ✅ Verificação automática a cada 5 minutos
- ✅ Diferentes níveis de prioridade (Alta, Média, Baixa)
- ✅ Filtros por tipo de usuário (Admin vê tudo, Instrutor só suas turmas)

**Critérios de notificação:**

- **Alta prioridade**: Chamadas não feitas há 2+ dias
- **Média prioridade**: Chamadas não feitas ontem
- **Baixa prioridade**: Chamadas não feitas hoje

## 📈 Como Usar

### Exportação CSV via Interface Web

1. Acesse a aba "Relatórios"
2. Configure os filtros desejados (opcional)
3. Clique no botão "Exportar CSV"
4. O arquivo será baixado automaticamente

### Exportação CSV via Script Python

Para exportações massivas ou automação:

```bash
# 1. Instalar dependências
pip install -r requirements_export.txt

# 2. Configurar .env no backend (já deve estar configurado)
# MONGO_URL=sua_connection_string
# DB_NAME=ios_sistema

# 3. Executar script
python export_attendance_csv.py
```

**Saída do script:**

```
🚀 Sistema de Exportação CSV - IOS
==================================================
✅ Conectado ao MongoDB: ios_sistema
📊 Coletando dados de presença...
📋 Encontradas 45 chamadas registradas
✅ CSV gerado com sucesso: relatorio_presenca_20250929_143022.csv
📊 Total de registros: 1,250
📅 Período: 2025-09-01 a 2025-09-29
🏫 Turmas: 8
👥 Alunos únicos: 156

📈 Estatísticas de Presença:
   Presente: 1,100
   Ausente: 120
   Atrasado: 25
   Justificado: 5
```

### Sistema de Notificações

1. **Visualização**: Ícone de sino no header

   - 🔔 Sino normal: Sem pendências
   - 🔔 Sino com badge vermelho: Tem pendências

2. **Detalhes**: Clique no sino para ver:

   - Lista de turmas com chamadas pendentes
   - Nível de prioridade de cada pendência
   - Informações completas (instrutor, unidade, curso)
   - Data da última chamada realizada

3. **Atualização**: Botão "Atualizar" para verificar novamente

## 🔧 Estrutura Técnica

### Backend (server.py)

**Endpoint CSV Aprimorado:**

```python
GET /api/reports/attendance?export_csv=true
```

**Novo Endpoint de Notificações:**

```python
GET /api/notifications/pending-calls
```

**Melhorias na Chamada:**

- Registro automático de hora para alunos presentes
- Status inteligente (Presente, Atrasado, Ausente, Justificado)
- Validação de permissões por curso/unidade

### Frontend (App.js)

**Componente NotificationButton:**

- Polling automático a cada 5 minutos
- Dialog modal com lista detalhada
- Badges de prioridade coloridos
- Atualização em tempo real

## 📊 Exemplo de CSV Gerado

```csv
Aluno,CPF,Matricula,Turma,Curso,Data,Hora_Inicio,Hora_Fim,Status,Hora_Registro,Professor,Unidade,Observacoes
Maria Silva,123.456.789-01,2023001,1ºB Informática,Desenvolvimento Web,2025-09-29,08:00,12:00,Presente,08:03,Prof. João,Unidade Centro,
Pedro Souza,987.654.321-02,2023002,1ºB Informática,Desenvolvimento Web,2025-09-29,08:00,12:00,Atrasado,08:15,Prof. João,Unidade Centro,Chegou 15min atrasado
Ana Costa,111.222.333-03,2023003,1ºB Informática,Desenvolvimento Web,2025-09-29,08:00,12:00,Ausente,,Prof. João,Unidade Centro,Faltou sem justificativa
Carlos Lima,444.555.666-04,2023004,1ºB Informática,Desenvolvimento Web,2025-09-29,08:00,12:00,Justificado,,Prof. João,Unidade Centro,Falta justificada com atestado médico
```

## 🔄 Fluxo de Trabalho Completo

### Para Administradores:

1. **Monitoramento**: Recebe notificações de todas as turmas pendentes
2. **Relatórios**: Pode exportar CSV completo de qualquer período
3. **Gestão**: Acompanha performance de instrutores via notificações

### Para Instrutores:

1. **Chamada**: Sistema registra automaticamente hora de presença
2. **Alertas**: Recebe notificações apenas das suas turmas pendentes
3. **Relatórios**: Pode exportar CSV das suas turmas

### Para Pedagogos/Monitores:

1. **Acompanhamento**: Vê notificações do seu curso/unidade
2. **Relatórios**: Acesso a dados do seu escopo de trabalho
3. **Suporte**: Pode auxiliar instrutores com base nas notificações

## 🎯 Benefícios Implementados

✅ **Gestão Acadêmica**: CSV com todos os dados necessários para secretaria
✅ **Controle de Frequência**: Status detalhado e horários precisos  
✅ **Auditoria**: Rastreamento completo de quem, quando e onde
✅ **Proatividade**: Notificações automáticas para chamadas pendentes
✅ **Automação**: Script independente para exportações em lote
✅ **Permissões**: Respeit aos níveis de acesso por usuário
✅ **Tempo Real**: Updates automáticos sem refresh manual

## 🚀 Deploy e Produção

As alterações são compatíveis com o deploy atual:

- **Backend**: Endpoints adicionais, sem breaking changes
- **Frontend**: Novos componentes, interface existente intacta
- **Banco**: Utiliza dados existentes, campos opcionais para compatibilidade

Basta fazer push das alterações que tudo continuará funcionando! 🎉
