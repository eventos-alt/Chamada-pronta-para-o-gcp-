import requests
import json

# Fazer login para obter token
login_data = {
    "email": "jesiel.junior@ios.org.br",
    "senha": "b99018cd"
}

try:
    # Login
    login_response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        print(f"✅ Login realizado com sucesso")
        
        # Testar o novo endpoint
        headers = {"Authorization": f"Bearer {token}"}
        csv_response = requests.get("http://localhost:8000/api/reports/student-frequency?export_csv=true", headers=headers)
        
        if csv_response.status_code == 200:
            csv_data = csv_response.json()["csv_data"]
            print(f"✅ CSV gerado com {len(csv_data.splitlines())} linhas")
            
            # Salvar o CSV para verificar
            with open("test_frequency_report.csv", "w", encoding="utf-8") as f:
                f.write(csv_data)
            
            # Mostrar algumas linhas para validar
            lines = csv_data.splitlines()
            print(f"\n📋 CABEÇALHO:")
            print(lines[0])
            print(f"\n📋 PRIMEIRA LINHA DE DADOS:")
            if len(lines) > 1:
                print(lines[1])
            else:
                print("Nenhum dado encontrado")
                
        else:
            print(f"❌ Erro no CSV: {csv_response.status_code}")
            print(csv_response.text)
            
    else:
        print(f"❌ Erro no login: {login_response.status_code}")
        print(login_response.text)
        
except Exception as e:
    print(f"❌ Erro: {e}")