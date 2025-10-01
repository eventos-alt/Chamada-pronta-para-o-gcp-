#!/usr/bin/env python3
"""
🗑️ REMOVER USUÁRIO ESPECÍFICO PARA PERMITIR RECADASTRO
Remove o usuário Ione Lima de Almeida para permitir novo cadastro
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('backend/.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb+srv://jesielamarojunior_db_user:admin123@cluster0.vuho6l7.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority')
DB_NAME = os.environ.get('DB_NAME', 'IOS-SISTEMA-CHAMADA')

async def remove_duplicate_user():
    """Remove o usuário duplicado para permitir novo cadastro"""
    try:
        print("🔌 Conectando ao MongoDB...")
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        # Testar conexão
        await client.admin.command('ping')
        print("✅ Conectado ao MongoDB!")
        
        # Buscar o usuário existente
        email_para_remover = "ione.almeida@ios.org.br"
        usuario_existente = await db.usuarios.find_one({"email": email_para_remover})
        
        if usuario_existente:
            print(f"\n🎯 USUÁRIO ENCONTRADO:")
            print(f"   Nome: {usuario_existente.get('nome')}")
            print(f"   Email: {usuario_existente.get('email')}")
            print(f"   Tipo: {usuario_existente.get('tipo')}")
            print(f"   ID: {usuario_existente.get('id')}")
            
            print(f"\n🗑️ REMOVENDO USUÁRIO...")
            result = await db.usuarios.delete_one({"email": email_para_remover})
            
            if result.deleted_count > 0:
                print(f"✅ USUÁRIO REMOVIDO COM SUCESSO!")
                print(f"   Agora você pode cadastrar um novo usuário com este email.")
            else:
                print(f"❌ Falha ao remover usuário.")
        else:
            print(f"✅ Email {email_para_remover} já está livre!")
        
        # Verificar usuários restantes
        total_usuarios = await db.usuarios.count_documents({})
        print(f"\n📊 USUÁRIOS RESTANTES NO SISTEMA: {total_usuarios}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(remove_duplicate_user())