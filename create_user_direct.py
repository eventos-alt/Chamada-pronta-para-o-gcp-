#!/usr/bin/env python3
"""
👤 CRIAR USUÁRIO DIRETAMENTE NO BANCO
Cria o usuário Ione Lima de Almeida com os dados corretos
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import uuid
import bcrypt

# Carregar variáveis de ambiente
load_dotenv('backend/.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb+srv://jesielamarojunior_db_user:admin123@cluster0.vuho6l7.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority')
DB_NAME = os.environ.get('DB_NAME', 'IOS-SISTEMA-CHAMADA')

async def create_user_direct():
    """Criar usuário diretamente no banco"""
    try:
        print("🔌 Conectando ao MongoDB...")
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        # Testar conexão
        await client.admin.command('ping')
        print("✅ Conectado ao MongoDB!")
        
        # Dados do usuário
        user_data = {
            "id": str(uuid.uuid4()),
            "nome": "Ione Lima de Almeida",
            "email": "ione.almeida@ios.org.br",
            "tipo": "pedagogo",
            "unidade_id": "5cb126bf-bf09-41a7-90ee-2292a6bd4b51",  # Santana - SP
            "curso_id": "4977d16f-8ad2-4d92-90a1-ec1ba5ea7823",    # Microsoft Office Essencial + Zendesk
            "telefone": "11 94459-6398",
            "senha": bcrypt.hashpw("temp123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "status": "pendente",
            "primeiro_acesso": True,
            "ativo": True,
            "token_confirmacao": str(uuid.uuid4())
        }
        
        print(f"\n👤 CRIANDO USUÁRIO:")
        print(f"   Nome: {user_data['nome']}")
        print(f"   Email: {user_data['email']}")
        print(f"   Tipo: {user_data['tipo']}")
        print(f"   Unidade: Santana - SP")
        print(f"   Curso: Microsoft Office Essencial + Zendesk")
        print(f"   Telefone: {user_data['telefone']}")
        print(f"   Senha temporária: temp123")
        
        # Verificar se já existe
        existing = await db.usuarios.find_one({"email": user_data["email"]})
        if existing:
            print(f"\n❌ Usuário já existe! Removendo primeiro...")
            await db.usuarios.delete_one({"email": user_data["email"]})
        
        # Inserir usuário
        result = await db.usuarios.insert_one(user_data)
        
        if result.inserted_id:
            print(f"\n✅ USUÁRIO CRIADO COM SUCESSO!")
            print(f"   ID: {user_data['id']}")
            print(f"   Senha temporária: temp123")
            print(f"   Status: {user_data['status']}")
            print(f"   O usuário pode fazer login e alterar a senha no primeiro acesso")
        else:
            print(f"\n❌ Falha ao criar usuário")
        
        # Verificar se foi criado
        created_user = await db.usuarios.find_one({"email": user_data["email"]})
        if created_user:
            print(f"\n🔍 VERIFICAÇÃO: Usuário encontrado no banco!")
            print(f"   Nome: {created_user.get('nome')}")
            print(f"   Email: {created_user.get('email')}")
            print(f"   Tipo: {created_user.get('tipo')}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(create_user_direct())