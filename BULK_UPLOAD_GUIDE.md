# 🚀 Sistema de Bulk Upload de Alunos - Guia Completo

## 📋 Visão Geral

O Sistema de Bulk Upload permite importar centenas de alunos de uma vez via arquivos CSV ou Excel, com validações robustas, tratamento de duplicados e permissões granulares por tipo de usuário.

## 🔗 Endpoint

```
POST /api/students/bulk-upload
```

## 📊 Parâmetros

| Parâmetro         | Tipo       | Obrigatório | Descrição                                   |
| ----------------- | ---------- | ----------- | ------------------------------------------- |
| `file`            | UploadFile | ✅          | Arquivo CSV ou Excel                        |
| `turma_id`        | string     | ❌          | ID da turma para associar alunos            |
| `curso_id`        | string     | ❌          | ID do curso (opcional para instrutor)       |
| `update_existing` | boolean    | ❌          | Se true, atualiza alunos existentes por CPF |

## 📄 Formato do Arquivo CSV

### Cabeçalhos Aceitos (aliases flexíveis):

**Obrigatórios:**

- `nome_completo`, `nome`, `full_name`, `student_name`
- `cpf`, `CPF`, `Cpf`, `document`

**Opcionais:**

- `data_nascimento`, `data nascimento`, `birthdate`, `dob`, `data_nasc`
- `email`, `e-mail`, `Email`
- `telefone`, `phone`, `celular`, `tel`
- `rg`, `RG`, `identidade`
- `genero`, `sexo`, `gender`
- `endereco`, `endereço`, `address`

### Exemplo de CSV:

```csv
nome_completo,cpf,data_nascimento,email,telefone,rg,genero,endereco
João da Silva,123.456.789-09,12/05/1990,joao@email.com,11999999999,12.345.678-9,M,Rua das Flores 123
Maria Souza,987.654.321-00,22/03/1995,maria@email.com,11888888888,98.765.432-1,F,Av Paulista 456
Carlos Pereira,111.222.333-44,01/01/1988,carlos@email.com,11777777777,11.122.233-3,M,Rua Augusta 789
```

## 🔒 Sistema de Permissões

| Tipo de Usuário  | Permissões                                                 |
| ---------------- | ---------------------------------------------------------- |
| **👑 Admin**     | Sem restrições - pode importar para qualquer curso/unidade |
| **👨‍🏫 Instrutor** | Apenas seu curso específico                                |
| **📊 Pedagogo**  | Qualquer curso da sua unidade                              |
| **👩‍💻 Monitor**   | ❌ SEM permissão de upload                                 |

## ✅ Validações Implementadas

### 1. Validação de CPF

- Algoritmo oficial brasileiro completo
- Remove automaticamente pontos e traços
- Rejeita sequências iguais (111.111.111-11)
- Valida dígitos verificadores

### 2. Parsing de Datas

- **DD/MM/YYYY** (12/05/1990)
- **YYYY-MM-DD** (1990-05-12)
- **DD-MM-YYYY** (12-05-1990)
- **YYYY/MM/DD** (1990/05/12)
- Parsing flexível com dateutil

### 3. Encoding Automático

- UTF-8 (padrão)
- Windows-1252 (Excel brasileiro)
- ISO-8859-1 (fallback)

### 4. Separador Automático

- Vírgula (,) ou ponto e vírgula (;)
- Detecção automática baseada no conteúdo

## 📊 Resposta da API

```json
{
  "success": true,
  "message": "Upload concluído: 15 inseridos, 3 atualizados, 2 pulados, 1 erros",
  "summary": {
    "total_processed": 21,
    "inserted": 15,
    "updated": 3,
    "skipped": 2,
    "errors_count": 1,
    "success_rate": "95.2%",
    "errors": [
      {
        "line": 7,
        "error": "CPF inválido: 000.000.000-00",
        "data": {
          "cpf_original": "000.000.000-00",
          "cpf_normalized": "00000000000"
        }
      }
    ]
  }
}
```

## 🎯 Implementação Frontend (React)

### 1. Componente de Upload

```javascript
const BulkUploadDialog = ({ isOpen, onClose, onSuccess }) => {
  const [file, setFile] = useState(null);
  const [updateExisting, setUpdateExisting] = useState(false);
  const [turmaId, setTurmaId] = useState("");
  const [uploading, setUploading] = useState(false);

  const handleUpload = async () => {
    if (!file) {
      toast({ title: "Erro", description: "Selecione um arquivo" });
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    const params = new URLSearchParams();
    if (updateExisting) params.append("update_existing", "true");
    if (turmaId) params.append("turma_id", turmaId);

    try {
      const response = await axios.post(
        `${API}/students/bulk-upload?${params}`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
          timeout: 300000, // 5 minutos para uploads grandes
        }
      );

      const result = response.data;
      toast({
        title: "✅ Upload Concluído",
        description: result.message,
      });

      // Mostrar resumo detalhado
      showUploadSummary(result.summary);
      onSuccess();
    } catch (error) {
      toast({
        title: "❌ Erro no Upload",
        description: error.response?.data?.detail || error.message,
        variant: "destructive",
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>📤 Importar Alunos em Massa</DialogTitle>
          <DialogDescription>
            Importe centenas de alunos via CSV ou Excel com validações
            automáticas
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Upload Area */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
            <input
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={(e) => setFile(e.target.files[0])}
              className="mb-4"
            />

            <div className="text-sm text-gray-600">
              <p>📄 Formatos aceitos: CSV, Excel (.xlsx, .xls)</p>
              <p>📊 Campos obrigatórios: nome_completo, cpf</p>
              <p>📋 Campos opcionais: data_nascimento, email, telefone, etc.</p>
            </div>
          </div>

          {/* Opções */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="update"
                checked={updateExisting}
                onCheckedChange={setUpdateExisting}
              />
              <Label htmlFor="update">
                Atualizar alunos existentes (por CPF)
              </Label>
            </div>

            <div className="space-y-2">
              <Label>Turma para associar (opcional)</Label>
              <Select value={turmaId} onValueChange={setTurmaId}>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione uma turma..." />
                </SelectTrigger>
                <SelectContent>
                  {turmas.map((turma) => (
                    <SelectItem key={turma.id} value={turma.id}>
                      {turma.nome}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Links Úteis */}
          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-medium mb-2">📋 Recursos Úteis:</h4>
            <div className="space-y-1 text-sm">
              <a
                href="/template_bulk_upload.csv"
                download
                className="text-blue-600 hover:underline block"
              >
                📥 Baixar modelo CSV
              </a>
              <a
                href="#validation-help"
                className="text-blue-600 hover:underline block"
              >
                📖 Guia de validações
              </a>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancelar
          </Button>
          <Button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="bg-green-600 hover:bg-green-700"
          >
            {uploading ? <>⏳ Processando...</> : <>🚀 Importar Alunos</>}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
```

### 2. Componente de Resumo

```javascript
const UploadSummaryDialog = ({ summary, isOpen, onClose }) => {
  const successRate = parseFloat(summary.success_rate);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>📊 Resumo do Upload</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Métricas */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-green-50 p-3 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {summary.inserted}
              </div>
              <div className="text-sm text-green-700">Inseridos</div>
            </div>

            <div className="bg-blue-50 p-3 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {summary.updated}
              </div>
              <div className="text-sm text-blue-700">Atualizados</div>
            </div>

            <div className="bg-yellow-50 p-3 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">
                {summary.skipped}
              </div>
              <div className="text-sm text-yellow-700">Pulados</div>
            </div>

            <div className="bg-red-50 p-3 rounded-lg">
              <div className="text-2xl font-bold text-red-600">
                {summary.errors_count}
              </div>
              <div className="text-sm text-red-700">Erros</div>
            </div>
          </div>

          {/* Taxa de Sucesso */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex justify-between items-center">
              <span className="font-medium">Taxa de Sucesso:</span>
              <span
                className={`text-lg font-bold ${
                  successRate >= 95
                    ? "text-green-600"
                    : successRate >= 80
                    ? "text-yellow-600"
                    : "text-red-600"
                }`}
              >
                {summary.success_rate}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div
                className={`h-2 rounded-full ${
                  successRate >= 95
                    ? "bg-green-600"
                    : successRate >= 80
                    ? "bg-yellow-600"
                    : "bg-red-600"
                }`}
                style={{ width: `${successRate}%` }}
              ></div>
            </div>
          </div>

          {/* Erros */}
          {summary.errors_count > 0 && (
            <div className="space-y-2">
              <h4 className="font-medium text-red-600">
                ❌ Erros Encontrados:
              </h4>
              <div className="max-h-40 overflow-y-auto space-y-2">
                {summary.errors.map((error, index) => (
                  <div
                    key={index}
                    className="bg-red-50 p-3 rounded border-l-4 border-red-400"
                  >
                    <div className="font-medium">Linha {error.line}:</div>
                    <div className="text-sm text-red-700">{error.error}</div>
                    {error.data && (
                      <div className="text-xs text-gray-600 mt-1">
                        {JSON.stringify(error.data)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button onClick={onClose}>Fechar</Button>
          {summary.errors_count > 0 && (
            <Button
              variant="outline"
              onClick={() => downloadErrorReport(summary.errors)}
            >
              📥 Baixar Relatório de Erros
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
```

## 🎯 UX Recomendada

1. **Botão Principal**: "📤 Importar Alunos em Massa"
2. **Preview**: Mostrar primeiras 5 linhas após seleção do arquivo
3. **Validação Prévia**: Validar formato antes do upload
4. **Progress Bar**: Para uploads grandes
5. **Resumo Detalhado**: Com métricas visuais
6. **Download de Erros**: CSV com linhas problemáticas
7. **Links Úteis**: Modelo CSV, guia de validação

## 🧪 Testando o Sistema

```bash
# Testar validações
python test_validation.py

# Testar endpoint (servidor rodando)
python test_bulk_upload.py

# Executar servidor
cd backend
python server.py
```

## 📋 Dependências Necessárias

```bash
# Backend
pip install python-dateutil

# Opcional para Excel
pip install pandas openpyxl
```

## 🚨 Considerações Importantes

1. **Performance**: Para +1000 linhas, considere job em background
2. **Timeout**: Configure timeout adequado no frontend (5+ minutos)
3. **Memória**: Arquivos muito grandes podem causar problemas
4. **Validação**: Sempre mostre resumo detalhado para o usuário
5. **Backup**: Considere backup antes de operações grandes
6. **Logs**: Sistema registra quem criou cada aluno (auditoria)

## 📖 Exemplos de Erro Comuns

- **CPF inválido**: "000.000.000-00" (sequência de zeros)
- **Data inválida**: "32/13/2000" (dia/mês impossível)
- **Campo vazio**: Nome ou CPF obrigatórios em branco
- **Duplicado**: CPF já existe no sistema
- **Permissão**: Instrutor tentando importar outro curso

O sistema está pronto para produção! 🚀
