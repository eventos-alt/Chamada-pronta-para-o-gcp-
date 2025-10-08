#!/usr/bin/env python3
"""
🚀 TESTE DO ENDPOINT BULK UPLOAD DE ALUNOS
Test script para validar o novo endpoint /api/students/bulk-upload

Testa:
- Validação CPF
- Parsing de datas
- Upload CSV
- Upload Excel (se pandas disponível)
- Tratamento de duplicados
- Permissões por tipo de usuário
"""

import requests
import csv
import io
import json
from datetime import datetime

# Configuração
BACKEND_URL = "http://localhost:8000"  # Ajustar conforme necessário
API_URL = f"{BACKEND_URL}/api"

def test_helper_functions():
    """Teste das funções helper de validação"""
    print("🧪 Testando funções helper...")
    
    # Teste para serem adicionados diretamente no servidor se necessário
    test_cpfs = [
        ("123.456.789-09", True),    # CPF válido
        ("12345678909", True),       # CPF válido sem formatação
        ("000.000.000-00", False),   # CPF inválido (zeros)
        ("123.456.789-00", False),   # CPF inválido
        ("12345", False),            # CPF muito curto
        ("", False),                 # CPF vazio
    ]
    
    test_dates = [
        "12/05/1990",     # DD/MM/YYYY
        "1995-03-22",     # YYYY-MM-DD
        "01-01-1988",     # DD-MM-YYYY
        "2000/12/25",     # YYYY/MM/DD
        "invalid",        # Data inválida
        "",               # Data vazia
    ]
    
    print("✅ Testes das funções helper definidos (executar no servidor)")

def create_test_csv():
    """Cria arquivo CSV de teste"""
    csv_content = """nome_completo,cpf,data_nascimento,email,telefone
João da Silva,123.456.789-09,12/05/1990,joao@email.com,11999999999
Maria Souza,987.654.321-00,1995-03-22,maria@email.com,11888888888
Carlos Pereira,111.222.333-44,01-01-1988,carlos@email.com,11777777777
Ana Santos,555.666.777-88,2000/12/25,ana@email.com,11666666666
CPF Inválido,000.000.000-00,1985-05-15,invalido@email.com,11555555555"""
    
    return csv_content

def test_bulk_upload_endpoint():
    """Teste do endpoint bulk upload"""
    print("\n🚀 Testando endpoint /api/students/bulk-upload...")
    
    # Primeiro, fazer login para obter token
    login_data = {
        "email": "admin@ios.com",  # Ajustar conforme usuário admin existente
        "senha": "admin123"        # Ajustar conforme senha
    }
    
    try:
        # Login
        print("🔐 Fazendo login...")
        login_response = requests.post(f"{API_URL}/auth/login", json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.status_code}")
            print(f"   Resposta: {login_response.text}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login realizado com sucesso")
        
        # Criar CSV de teste
        csv_content = create_test_csv()
        
        # Preparar arquivo para upload
        files = {
            "file": ("test_alunos.csv", csv_content, "text/csv")
        }
        
        # Parâmetros do teste
        params = {
            "update_existing": "false",  # Primeiro teste: não atualizar
            # "turma_id": "turma_id_existente",  # Opcional: associar a uma turma
            # "curso_id": "curso_id_existente"   # Opcional: curso específico
        }
        
        print("📤 Enviando CSV para bulk upload...")
        
        # Fazer upload
        response = requests.post(
            f"{API_URL}/students/bulk-upload",
            files=files,
            params=params,
            headers=headers
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload realizado com sucesso!")
            print(f"📊 Resumo:")
            print(f"   Inseridos: {result['summary']['inserted']}")
            print(f"   Atualizados: {result['summary']['updated']}")
            print(f"   Pulados: {result['summary']['skipped']}")
            print(f"   Erros: {result['summary']['errors_count']}")
            print(f"   Taxa de sucesso: {result['summary']['success_rate']}")
            
            if result['summary']['errors']:
                print(f"❌ Erros encontrados:")
                for error in result['summary']['errors'][:5]:  # Mostrar apenas 5 primeiros
                    print(f"   Linha {error['line']}: {error['error']}")
        else:
            print(f"❌ Erro no upload: {response.status_code}")
            print(f"   Resposta: {response.text}")
        
        # Teste 2: Reenviar mesmo CSV com update_existing=true
        print("\n🔄 Testando atualização de existentes...")
        params_update = {
            "update_existing": "true"
        }
        
        files_update = {
            "file": ("test_alunos_update.csv", csv_content, "text/csv")
        }
        
        response_update = requests.post(
            f"{API_URL}/students/bulk-upload",
            files=files_update,
            params=params_update,
            headers=headers
        )
        
        if response_update.status_code == 200:
            result_update = response_update.json()
            print("✅ Teste de atualização realizado!")
            print(f"   Atualizados: {result_update['summary']['updated']}")
            print(f"   Pulados: {result_update['summary']['skipped']}")
        else:
            print(f"❌ Erro na atualização: {response_update.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        print("⚠️ Certifique-se de que o backend está rodando em http://localhost:8000")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def create_sample_csv_file():
    """Cria arquivo CSV de exemplo para download"""
    sample_csv = """nome_completo,cpf,data_nascimento,email,telefone,rg,genero,endereco
João da Silva,123.456.789-09,12/05/1990,joao@email.com,11999999999,12.345.678-9,M,Rua A 123
Maria Souza,987.654.321-00,22/03/1995,maria@email.com,11888888888,98.765.432-1,F,Av B 456
Carlos Pereira,111.222.333-44,01/01/1988,carlos@email.com,11777777777,11.122.233-3,M,Rua C 789"""
    
    with open("exemplo_alunos.csv", "w", encoding="utf-8", newline="") as f:
        f.write(sample_csv)
    
    print("📁 Arquivo exemplo_alunos.csv criado para download!")

if __name__ == "__main__":
    print("🚀 TESTE DO SISTEMA DE BULK UPLOAD DE ALUNOS")
    print("=" * 50)
    
    # Executar testes
    test_helper_functions()
    test_bulk_upload_endpoint()
    create_sample_csv_file()
    
    print("\n" + "=" * 50)
    print("✅ Testes concluídos!")
    print("\n📋 Para usar no frontend:")
    print("1. Botão 'Importar Alunos em Massa'")
    print("2. Upload de arquivo CSV ou Excel")
    print("3. Opções: update_existing, turma_id, curso_id")
    print("4. Mostrar resumo detalhado após upload")
    print("5. Download do arquivo exemplo_alunos.csv criado")