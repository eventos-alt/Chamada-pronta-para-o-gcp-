#!/usr/bin/env python3
"""
🚨 SCRIPT DE RESET TOTAL DO BANCO
Este script apaga TODOS os alunos e turmas do sistema
"""

import requests
import json

# Configurações
API_BASE = "http://localhost:8000/api"

def login_admin():
    """Tenta fazer login com usuários admin comuns"""
    # Lista de possíveis credenciais admin
    admin_credentials = [
        {"email": "admin@ios.com", "password": "admin123"},
        {"email": "admin@sistema.com", "password": "admin123"},
        {"email": "administrador@ios.com", "password": "admin123"},
        {"email": "admin", "password": "admin"},
        {"email": "root@ios.com", "password": "root123"},
    ]
    
    for cred in admin_credentials:
        try:
            print(f"🔑 Tentando login: {cred['email']}")
            response = requests.post(f"{API_BASE}/auth/login", json=cred)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                user = data.get("user", {})
                
                if user.get("tipo") == "admin":
                    print(f"✅ Login admin bem-sucedido: {user.get('nome', user.get('email'))}")
                    return token
                else:
                    print(f"❌ Usuário não é admin: {user.get('tipo')}")
            else:
                print(f"❌ Falha no login: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro na tentativa: {e}")
    
    return None

def reset_database(token):
    """Executa o reset total do banco"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print("\n🚨 EXECUTANDO RESET TOTAL DO BANCO...")
        print("   ⚠️  Esta operação apagará TODOS os alunos e turmas!")
        
        response = requests.post(f"{API_BASE}/database/reset-all", headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ RESET EXECUTADO COM SUCESSO!")
            print(f"   📊 Alunos removidos: {result['removidos']['alunos']}")
            print(f"   📊 Turmas removidas: {result['removidos']['turmas']}")
            print(f"   📊 Chamadas removidas: {result['removidos']['chamadas']}")
            print(f"   📋 Status: {result['status']}")
            return True
        else:
            print(f"❌ Erro no reset: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na execução: {e}")
        return False

def main():
    print("🚨 SISTEMA DE RESET TOTAL DO BANCO IOS")
    print("=" * 50)
    
    # Fazer login
    token = login_admin()
    if not token:
        print("\n❌ FALHA: Não foi possível fazer login como admin")
        print("   Você precisa ter pelo menos um usuário admin no sistema")
        return
    
    # Executar reset
    success = reset_database(token)
    
    if success:
        print("\n🎉 OPERAÇÃO CONCLUÍDA!")
        print("   O banco foi limpo completamente.")
        print("   Você pode agora recadastrar alunos do zero.")
    else:
        print("\n❌ OPERAÇÃO FALHOU!")
        print("   Verifique os logs do backend para mais detalhes.")

if __name__ == "__main__":
    main()