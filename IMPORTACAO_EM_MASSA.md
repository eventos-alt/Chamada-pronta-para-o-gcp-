# 📋 Importação em Massa de Alunos - Manual de Uso

## 🎯 Funcionalidade

O sistema permite importar múltiplos alunos de uma vez usando arquivos CSV, agilizando o processo de cadastramento e reduzindo erros manuais.

## 👥 Permissões de Acesso

### 🔧 **Admin (Administrador)**

- ✅ Pode importar alunos para **qualquer curso e unidade**
- ✅ Acesso completo a todas as funcionalidades
- ✅ Pode corrigir dados após importação

### 👨‍🏫 **Instrutor**

- ✅ Pode importar alunos **apenas para seu curso específico**
- ✅ Turmas inexistentes no CSV são criadas automaticamente
- ✅ Alunos sem turma ficam como "não alocado"

### 📊 **Pedagogo**

- ✅ Pode importar alunos **para qualquer curso da sua unidade**
- ⚠️ Restrito à sua unidade

### 👩‍💻 **Monitor**

- ❌ **Não pode importar** (apenas visualizar alunos)

## 📋 Formato do Arquivo CSV

### Campos Obrigatórios

```csv
nome_completo,cpf,data_nascimento
```

### Campos Opcionais

```csv
email,telefone,rg,genero,endereco,turma
```

### 📄 Exemplo Completo

```csv
nome_completo,cpf,data_nascimento,email,telefone,rg,genero,endereco,turma
João da Silva Santos,123.456.789-09,15/03/1990,joao@email.com,11999999999,12.345.678-9,masculino,Rua das Flores 123,Turma A
Maria Souza Oliveira,987.654.321-00,22/08/1995,maria@email.com,11888888888,98.765.432-1,feminino,Av Paulista 456,Turma B
Carlos Pereira Lima,111.222.333-44,01/01/1988,carlos@email.com,11777777777,11.122.233-3,masculino,Rua Augusta 789,Turma A
```

## 🎯 Formatos Aceitos

### 📅 Data de Nascimento

- **Formato:** `DD/MM/AAAA`
- **Exemplos válidos:** `15/03/1990`, `01/12/2000`, `30/06/1985`

### 🆔 CPF

- **Com pontuação:** `123.456.789-09`
- **Sem pontuação:** `12345678909`
- **Validação:** Sistema verifica se o CPF é válido

### 📧 Email (Opcional)

- **Formato:** `usuario@dominio.com`
- **Validação:** Sistema verifica formato válido

### 👤 Gênero (Opcional)

- **Opções:** `masculino`, `feminino`, `outro`, `nao_informado`

## 🚀 Como Usar

### 1️⃣ **Acessar a Função**

1. Faça login no sistema
2. Vá para a aba **"Alunos"**
3. Clique no botão **"Importar em Massa"** (verde)

### 2️⃣ **Preparar o Arquivo**

1. Clique em **"Baixar Modelo CSV"** para ter um exemplo
2. Abra o arquivo no Excel ou editor de texto
3. Preencha os dados dos alunos seguindo o formato
4. Salve como arquivo `.csv`

### 3️⃣ **Configurar Importação**

1. **Selecione o arquivo CSV** no seu computador
2. **Opções disponíveis:**
   - ☑️ **Atualizar existentes:** Atualiza alunos com mesmo CPF
   - 🎯 **Turma padrão:** Turma para alunos sem turma especificada

### 4️⃣ **Executar Importação**

1. Clique em **"Importar Alunos"**
2. Aguarde o processamento (pode demorar alguns segundos)
3. Visualize o **relatório detalhado** dos resultados

## 📊 Relatório de Resultados

### 📈 Métricas Exibidas

- ✅ **Sucessos:** Alunos importados com sucesso
- ❌ **Erros:** Linhas com problemas de validação
- 🔄 **Duplicados:** CPFs já existentes no sistema
- 📋 **Total:** Linhas processadas

### 📝 Detalhes do Processamento

- **Linha por linha:** Status individual de cada aluno
- **Mensagens específicas:** Detalhes sobre sucessos e erros
- **Download de erros:** Arquivo CSV com os erros encontrados

## ⚠️ Problemas Comuns

### ❌ **CPF Inválido**

- **Problema:** CPF não passa na validação
- **Solução:** Verificar se o CPF está correto

### ❌ **Data Inválida**

- **Problema:** Data não está no formato DD/MM/AAAA
- **Solução:** Corrigir formato da data

### ❌ **Curso Não Permitido**

- **Problema:** Instrutor tentando importar para outro curso
- **Solução:** Verificar se o curso no CSV é o mesmo do usuário

### ❌ **Arquivo Muito Grande**

- **Problema:** Muitos alunos no arquivo CSV
- **Solução:** Dividir em arquivos menores (máx. 500 alunos por vez)

## 💡 Dicas e Boas Práticas

### 📋 **Preparação do Arquivo**

1. **Use o modelo:** Sempre baixe e use o modelo fornecido
2. **Teste pequeno:** Comece com poucos alunos para testar
3. **Backup:** Mantenha uma cópia do arquivo original

### 🎯 **Gestão de Turmas**

1. **Turmas existentes:** Use nomes exatos das turmas já criadas
2. **Novas turmas:** Instrutores podem criar turmas automaticamente
3. **Sem turma:** Deixe campo vazio para "não alocado"

### 🔄 **Atualizações**

1. **CPF único:** Sistema usa CPF para identificar alunos existentes
2. **Dados novos:** Marque "Atualizar existentes" para sobrescrever
3. **Validação:** Sempre revise o relatório de resultados

## 📞 Suporte

### 🆘 Em caso de dúvidas:

1. Consulte este manual primeiro
2. Teste com poucos registros
3. Verifique o relatório de erros
4. Entre em contato com a equipe técnica

---

## 🎉 Resultado Final

Após a importação bem-sucedida:

- ✅ Alunos aparecem na lista principal
- ✅ Podem ser gerenciados normalmente
- ✅ Estão prontos para chamadas e relatórios
- ✅ Histórico de importação fica salvo no sistema

**💪 Importação em massa concluída com sucesso!**
