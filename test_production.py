import requests
import json

def test_students_endpoint_production():
    """Testar endpoint /api/students em produção com autenticação"""
    
    backend_url = "https://sistema-ios-backend.onrender.com/api"
    
    print("🔍 Testando endpoint /api/students em PRODUÇÃO...")
    
    try:
        # 1. Fazer login como admin
        print("\n1️⃣ Fazendo login como admin...")
        login_data = {
            "email": "admin@ios.com", 
            "senha": "admin123"
        }
        
        login_response = requests.post(f"{backend_url}/auth/login", json=login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Login falhou: {login_response.text}")
            return False
            
        # 2. Extrair token
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Token obtido com sucesso")
        
        # 3. Testar endpoint /api/students
        print("\n2️⃣ Testando endpoint /api/students...")
        students_response = requests.get(f"{backend_url}/students", headers=headers)
        
        print(f"Students Status: {students_response.status_code}")
        print(f"Content-Type: {students_response.headers.get('content-type', 'N/A')}")
        
        if students_response.status_code == 200:
            students = students_response.json()
            print(f"✅ SUCCESS! Total de alunos: {len(students)}")
            
            if students:
                primeiro_aluno = students[0]
                print(f"👤 Primeiro aluno:")
                print(f"   Nome: {primeiro_aluno.get('nome', 'N/A')}")
                print(f"   CPF: {primeiro_aluno.get('cpf', 'N/A')}")
                print(f"   Data Nascimento: {primeiro_aluno.get('data_nascimento', 'N/A')}")
                print(f"   Status: {primeiro_aluno.get('status', 'N/A')}")
            
            return True
            
        elif students_response.status_code == 422:
            print(f"❌ ERRO 422 ainda persiste!")
            print(f"Response: {students_response.text[:500]}...")
            return False
        else:
            print(f"❌ Erro inesperado: {students_response.status_code}")
            print(f"Response: {students_response.text[:500]}...")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

if __name__ == "__main__":
    success = test_students_endpoint_production()
    print(f"\n🎯 Resultado: {'✅ ENDPOINT FUNCIONANDO' if success else '❌ ENDPOINT COM PROBLEMA'}")