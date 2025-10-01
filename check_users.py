#!/usr/bin/env python3
"""
🔍 SCRIPT PARA VERIFICAR E LIMPAR USUÁRIOS DUPLICADOS
Conecta diretamente no MongoDB para resolver conflitos de email
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('backend/.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb+srv://jesielamarojunior_db_user:admin123@cluster0.vuho6l7.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority')
DB_NAME = os.environ.get('DB_NAME', 'IOS-SISTEMA-CHAMADA')

async def check_and_fix_users():
    """Verificar e corrigir problemas com usuários"""
    try:
        print("🔌 Conectando ao MongoDB...")
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        # Testar conexão
        await client.admin.command('ping')
        print("✅ Conectado ao MongoDB!")
        
        # Listar todos os usuários
        print(f"\n👥 USUÁRIOS EXISTENTES:")
        usuarios = await db.usuarios.find({}).to_list(100)
        
        emails_vistos = set()
        duplicados = []
        
        for i, user in enumerate(usuarios, 1):
            email = user.get('email', 'N/A')
            nome = user.get('nome', 'N/A')
            tipo = user.get('tipo', 'N/A')
            id_user = user.get('id', user.get('_id', 'N/A'))
            
            print(f"   {i}. {nome} ({email}) - {tipo} - ID: {id_user}")
            
            if email in emails_vistos:
                duplicados.append(user)
                print(f"      ⚠️  DUPLICADO ENCONTRADO!")
            else:
                emails_vistos.add(email)
        
        if duplicados:
            print(f"\n🚨 ENCONTRADOS {len(duplicados)} USUÁRIOS DUPLICADOS:")
            for dup in duplicados:
                print(f"   • {dup.get('nome')} ({dup.get('email')})")
                
            print(f"\n🗑️  REMOVENDO DUPLICADOS...")
            for dup in duplicados:
                await db.usuarios.delete_one({"_id": dup["_id"]})
                print(f"   ✅ Removido: {dup.get('nome')} ({dup.get('email')})")
        
        # Verificar se o email 'ione.almeida@ios.org.br' existe
        email_procurado = "ione.almeida@ios.org.br"
        usuario_existente = await db.usuarios.find_one({"email": email_procurado})
        
        if usuario_existente:
            print(f"\n⚠️  USUÁRIO COM EMAIL {email_procurado} JÁ EXISTS:")
            print(f"   Nome: {usuario_existente.get('nome')}")
            print(f"   Tipo: {usuario_existente.get('tipo')}")
            print(f"   ID: {usuario_existente.get('id')}")
            
            resposta = input(f"\n❓ Deseja remover este usuário para permitir o novo cadastro? (s/n): ")
            if resposta.lower() in ['s', 'sim', 'y', 'yes']:
                await db.usuarios.delete_one({"email": email_procurado})
                print(f"✅ Usuário {email_procurado} removido!")
            else:
                print(f"❌ Usuário mantido. Use um email diferente.")
        else:
            print(f"\n✅ Email {email_procurado} está livre para uso!")
        
        # Contar usuários finais
        total_usuarios = await db.usuarios.count_documents({})
        print(f"\n📊 TOTAL DE USUÁRIOS NO SISTEMA: {total_usuarios}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(check_and_fix_users())