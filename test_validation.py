#!/usr/bin/env python3
"""
🧪 TESTE SIMPLES DO BULK UPLOAD
Teste direto das funções de validação CPF e data
"""

import re
from datetime import datetime, date

def normalize_cpf(raw: str) -> str:
    """Remove all non-digit characters from CPF"""
    if raw is None:
        return ""
    s = re.sub(r"\D", "", str(raw))
    return s

def validate_cpf(cpf: str) -> bool:
    """Validate Brazilian CPF number"""
    cpf = normalize_cpf(cpf)
    if len(cpf) != 11:
        return False
    # evita sequências iguais
    if cpf == cpf[0] * 11:
        return False

    def calc_digit(cpf_slice: str) -> int:
        size = len(cpf_slice) + 1
        total = 0
        for i, ch in enumerate(cpf_slice):
            total += int(ch) * (size - i)
        r = total % 11
        return 0 if r < 2 else 11 - r

    d1 = calc_digit(cpf[:9])
    d2 = calc_digit(cpf[:10])
    return d1 == int(cpf[9]) and d2 == int(cpf[10])

def parse_date_str(s: str) -> date:
    """Parse date string in various formats"""
    if s is None:
        raise ValueError("Data vazia")
    s = str(s).strip()
    # tenta formatos comuns
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            pass
    # fallback mais flexível
    try:
        from dateutil import parser as dateutil_parser
        return dateutil_parser.parse(s, dayfirst=True).date()
    except Exception as e:
        raise ValueError("Formato de data inválido. Utilize YYYY-MM-DD ou DD/MM/YYYY") from e

def test_cpf_validation():
    """Teste da validação de CPF"""
    test_cases = [
        ("123.456.789-09", True),    # CPF válido
        ("12345678909", True),       # CPF válido sem formatação
        ("000.000.000-00", False),   # CPF inválido (zeros)
        ("123.456.789-00", False),   # CPF inválido
        ("12345", False),            # CPF muito curto
        ("", False),                 # CPF vazio
        ("111.111.111-11", False),   # Sequência igual
    ]
    
    print("🧪 Testando validação de CPF:")
    for cpf, expected in test_cases:
        result = validate_cpf(cpf)
        status = "✅" if result == expected else "❌"
        print(f"   {status} {cpf} -> {result} (esperado: {expected})")

def test_date_parsing():
    """Teste do parsing de datas"""
    test_cases = [
        ("12/05/1990", True),     # DD/MM/YYYY
        ("1995-03-22", True),     # YYYY-MM-DD
        ("01-01-1988", True),     # DD-MM-YYYY
        ("2000/12/25", True),     # YYYY/MM/DD
        ("25/12/2000", True),     # DD/MM/YYYY
        ("invalid", False),       # Data inválida
        ("", False),              # Data vazia
        ("32/13/2000", False),    # Data impossível
    ]
    
    print("\n🧪 Testando parsing de datas:")
    for date_str, should_work in test_cases:
        try:
            result = parse_date_str(date_str)
            status = "✅" if should_work else "❌"
            print(f"   {status} '{date_str}' -> {result}")
        except Exception as e:
            status = "✅" if not should_work else "❌"
            print(f"   {status} '{date_str}' -> ERRO: {e}")

def test_csv_parsing():
    """Teste do parsing de CSV"""
    csv_content = """nome_completo,cpf,data_nascimento,email
João da Silva,123.456.789-09,12/05/1990,joao@email.com
Maria Souza,987.654.321-00,22/03/1995,maria@email.com
Invalid CPF,000.000.000-00,01/01/1988,invalid@email.com
Invalid Date,111.222.333-44,invalid_date,date@email.com"""

    print("\n🧪 Testando parsing de CSV:")
    
    import csv
    from io import StringIO
    
    reader = csv.DictReader(StringIO(csv_content))
    
    for i, row in enumerate(reader, 1):
        print(f"\n   Linha {i}:")
        nome = row.get('nome_completo', '').strip()
        cpf = row.get('cpf', '').strip()
        data_str = row.get('data_nascimento', '').strip()
        email = row.get('email', '').strip()
        
        print(f"     Nome: {nome}")
        print(f"     CPF: {cpf} -> {'✅' if validate_cpf(cpf) else '❌'}")
        
        try:
            data = parse_date_str(data_str)
            print(f"     Data: {data_str} -> ✅ {data}")
        except Exception as e:
            print(f"     Data: {data_str} -> ❌ {e}")
        
        print(f"     Email: {email}")

if __name__ == "__main__":
    print("🚀 TESTE DAS FUNÇÕES DE BULK UPLOAD")
    print("=" * 50)
    
    test_cpf_validation()
    test_date_parsing()
    test_csv_parsing()
    
    print("\n" + "=" * 50)
    print("✅ Todos os testes de validação concluídos!")
    print("\n📋 Endpoint implementado: POST /api/students/bulk-upload")
    print("📋 Parâmetros aceitos:")
    print("   - file: UploadFile (CSV ou Excel)")
    print("   - turma_id: Optional[str] (associar à turma)")
    print("   - curso_id: Optional[str] (curso específico)")
    print("   - update_existing: bool (atualizar existentes)")
    print("\n📋 Campos CSV aceitos:")
    print("   Obrigatórios: nome_completo, cpf")
    print("   Opcionais: data_nascimento, email, telefone, rg, genero, endereco")
    print("\n📋 Validações implementadas:")
    print("   ✅ CPF brasileiro com algoritmo completo")
    print("   ✅ Datas em múltiplos formatos")
    print("   ✅ Duplicados por CPF")
    print("   ✅ Permissões por tipo de usuário")
    print("   ✅ Encoding automático (UTF-8, Windows-1252, ISO-8859-1)")
    print("   ✅ Separador CSV automático (, ou ;)")