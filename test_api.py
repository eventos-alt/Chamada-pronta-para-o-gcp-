import requests
import json

# Testar endpoint público primeiro
print("🔍 Testando endpoints...")

# 1. Testar ping (público)
try:
    response = requests.get("http://localhost:8001/api/ping")
    print(f"✅ Ping: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"❌ Erro no ping: {e}")

# 2. Testar students sem auth (deve dar 401)
try:
    response = requests.get("http://localhost:8001/api/students")
    print(f"🔒 Students sem auth: {response.status_code} - {response.text[:100]}...")
except Exception as e:
    print(f"❌ Erro no students: {e}")

# 3. Testar com login de admin
try:
    # Login do admin
    login_data = {
        "email": "admin@ios.com",
        "password": "admin123"
    }
    login_response = requests.post("http://localhost:8001/api/auth/login", json=login_data)
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Testar students com auth
        students_response = requests.get("http://localhost:8001/api/students", headers=headers)
        print(f"👤 Students com auth: {students_response.status_code}")
        
        if students_response.status_code == 200:
            students = students_response.json()
            print(f"✅ Total de alunos retornados: {len(students)}")
            if students:
                print(f"🎯 Primeiro aluno: {students[0].get('nome', 'SEM_NOME')} - Data Nascimento: {students[0].get('data_nascimento', 'NENHUMA')}")
        else:
            print(f"❌ Erro students: {students_response.text}")
    else:
        print(f"❌ Login falhou: {login_response.status_code} - {login_response.text}")
        
except Exception as e:
    print(f"❌ Erro no teste completo: {e}")

print("\n🏁 Teste finalizado!")