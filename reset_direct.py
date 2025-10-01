#!/usr/bin/env python3
"""
🔍 SCRIPT PARA LISTAR USUÁRIOS E FAZER RESET DIRETO
Conecta diretamente no MongoDB para fazer o reset
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('backend/.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb+srv://jesielamarojunior_db_user:admin123@cluster0.vuho6l7.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority')
DB_NAME = os.environ.get('DB_NAME', 'IOS-SISTEMA-CHAMADA')

async def reset_database_direct():
    """Reset direto no MongoDB"""
    try:
        print("🔌 Conectando ao MongoDB...")
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        # Testar conexão
        await client.admin.command('ping')
        print("✅ Conectado ao MongoDB!")
        
        # Contar registros antes
        alunos_count = await db.alunos.count_documents({})
        turmas_count = await db.turmas.count_documents({})
        chamadas_count = await db.chamadas.count_documents({})
        usuarios_count = await db.usuarios.count_documents({})
        
        print(f"\n📊 ESTADO ATUAL DO BANCO:")
        print(f"   👥 Usuários: {usuarios_count}")
        print(f"   🎓 Alunos: {alunos_count}")
        print(f"   📚 Turmas: {turmas_count}")
        print(f"   📋 Chamadas: {chamadas_count}")
        
        # Listar alguns usuários para ver se tem admin
        print(f"\n👥 USUÁRIOS NO SISTEMA:")
        usuarios = await db.usuarios.find({}).limit(10).to_list(10)
        for user in usuarios:
            print(f"   • {user.get('nome', 'N/A')} ({user.get('email', 'N/A')}) - Tipo: {user.get('tipo', 'N/A')}")
        
        print(f"\n🚨 EXECUTANDO RESET TOTAL...")
        print(f"   ⚠️  APAGANDO {alunos_count} alunos...")
        print(f"   ⚠️  APAGANDO {turmas_count} turmas...")
        print(f"   ⚠️  APAGANDO {chamadas_count} chamadas...")
        
        # FAZER O RESET
        result_alunos = await db.alunos.delete_many({})
        result_turmas = await db.turmas.delete_many({})
        result_chamadas = await db.chamadas.delete_many({})
        
        print(f"\n✅ RESET CONCLUÍDO!")
        print(f"   🗑️  Alunos removidos: {result_alunos.deleted_count}")
        print(f"   🗑️  Turmas removidas: {result_turmas.deleted_count}")
        print(f"   🗑️  Chamadas removidas: {result_chamadas.deleted_count}")
        
        # Verificar se está limpo
        alunos_restantes = await db.alunos.count_documents({})
        turmas_restantes = await db.turmas.count_documents({})
        chamadas_restantes = await db.chamadas.count_documents({})
        
        print(f"\n📊 ESTADO FINAL:")
        print(f"   👥 Usuários: {usuarios_count} (mantidos)")
        print(f"   🎓 Alunos: {alunos_restantes}")
        print(f"   📚 Turmas: {turmas_restantes}")
        print(f"   📋 Chamadas: {chamadas_restantes}")
        
        if alunos_restantes == 0 and turmas_restantes == 0 and chamadas_restantes == 0:
            print(f"\n🎉 SUCESSO TOTAL! Banco limpo e pronto para recomeçar!")
        else:
            print(f"\n⚠️  Ainda restaram alguns registros...")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(reset_database_direct())