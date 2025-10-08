#!/usr/bin/env python3
"""
🧹 LIMPEZA RADICAL - SISTEMA IOS
Remove TUDO: alunos, turmas, chamadas e dados de seed/inicialização
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote_plus

async def radical_cleanup():
    """Remove TODOS os dados de demonstração e teste"""
    
    # Conexão MongoDB
    username = quote_plus("jesielamarojunior_db_user")
    password = quote_plus("admin123")
    MONGO_URL = f"mongodb+srv://{username}:{password}@cluster0.vuho6l7.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority"
    
    print("🔗 Conectando ao MongoDB Atlas...")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client["IOS-SISTEMA-CHAMADA"]
    
    try:
        print("\n🚨 LIMPEZA RADICAL - REMOVENDO TUDO!")
        
        # 🗑️ DELETAR TODAS AS TURMAS (sem exceção)
        print("\n🏫 Removendo TODAS as turmas...")
        result_turmas = await db.turmas.delete_many({})
        print(f"   ✅ {result_turmas.deleted_count} turmas removidas")
        
        # 🗑️ DELETAR TODOS OS ALUNOS (sem exceção)
        print("\n👥 Removendo TODOS os alunos...")
        result_alunos = await db.alunos.delete_many({})
        print(f"   ✅ {result_alunos.deleted_count} alunos removidos")
        
        # 🗑️ DELETAR TODAS AS CHAMADAS
        print("\n📞 Removendo TODAS as chamadas...")
        result_chamadas = await db.chamadas.delete_many({})
        print(f"   ✅ {result_chamadas.deleted_count} chamadas removidas")
        
        # 🗑️ DELETAR DESISTENTES
        print("\n📋 Removendo desistentes...")
        result_desistentes = await db.desistentes.delete_many({})
        print(f"   ✅ {result_desistentes.deleted_count} desistentes removidos")
        
        # 🗑️ DELETAR RELATÓRIOS E LOGS
        print("\n📊 Removendo relatórios e logs...")
        await db.relatorios.delete_many({})
        await db.logs.delete_many({})
        await db.uploads.delete_many({})
        await db.atestados.delete_many({})
        
        # 📊 VERIFICAÇÃO FINAL
        print("\n📊 VERIFICAÇÃO FINAL:")
        turmas_restantes = await db.turmas.count_documents({})
        alunos_restantes = await db.alunos.count_documents({})
        chamadas_restantes = await db.chamadas.count_documents({})
        usuarios_restantes = await db.usuarios.count_documents({})
        
        print(f"   📚 Turmas: {turmas_restantes}")
        print(f"   👥 Alunos: {alunos_restantes}")
        print(f"   📞 Chamadas: {chamadas_restantes}")
        print(f"   👤 Usuários: {usuarios_restantes}")
        
        if turmas_restantes == 0 and alunos_restantes == 0 and chamadas_restantes == 0:
            print("\n🎉 LIMPEZA RADICAL COMPLETA!")
            print("✅ Sistema 100% limpo - ZERO dados de exemplo")
            print("✅ Apenas usuários reais mantidos")
        else:
            print(f"\n⚠️ Ainda existem dados: T:{turmas_restantes} A:{alunos_restantes} C:{chamadas_restantes}")
        
    except Exception as e:
        print(f"❌ Erro durante limpeza radical: {e}")
    finally:
        client.close()
        print("\n🔒 Conexão MongoDB fechada.")

if __name__ == "__main__":
    print("=" * 60)
    print("🚨 LIMPEZA RADICAL - REMOÇÃO COMPLETA")
    print("=" * 60)
    print("⚠️  ATENÇÃO: Remove TUDO - turmas, alunos, chamadas!")
    print("⚠️  Mantém apenas usuários reais do sistema!")
    print("=" * 60)
    
    asyncio.run(radical_cleanup())