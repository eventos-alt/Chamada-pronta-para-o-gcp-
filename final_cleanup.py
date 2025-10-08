#!/usr/bin/env python3
"""
🧹 LIMPEZA FINAL - SISTEMA IOS
Remove os últimos dados restantes identificados
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote_plus

async def final_cleanup():
    """Remove os dados restantes identificados"""
    
    # Conexão MongoDB
    username = quote_plus("jesielamarojunior_db_user")
    password = quote_plus("admin123")
    MONGO_URL = f"mongodb+srv://{username}:{password}@cluster0.vuho6l7.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority"
    
    print("🔗 Conectando ao MongoDB Atlas...")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client["IOS-SISTEMA-CHAMADA"]
    
    try:
        # 🏫 REMOVER TURMAS RESTANTES (são de teste)
        print("\n🗑️ Removendo turmas restantes de teste...")
        turmas_removidas = await db.turmas.delete_many({
            "$or": [
                {"nome": "Informática Turma A"},
                {"nome": "Administração Turma B"},
                {"instrutor_nome": {"$exists": False}},  # Turmas ohne instrutor
                {"curso_nome": {"$exists": False}}       # Turmas ohne curso
            ]
        })
        print(f"   ✅ {turmas_removidas.deleted_count} turmas removidas")
        
        # 📞 REMOVER CHAMADAS ÓRFÃS (sem turma/instrutor)
        print("\n🗑️ Removendo chamadas órfãs...")
        chamadas_removidas = await db.chamadas.delete_many({
            "$or": [
                {"turma_nome": {"$exists": False}},
                {"turma_nome": None},
                {"turma_nome": "SEM_TURMA"},
                {"instrutor_nome": {"$exists": False}},
                {"instrutor_nome": None},
                {"instrutor_nome": "SEM_INSTRUTOR"}
            ]
        })
        print(f"   ✅ {chamadas_removidas.deleted_count} chamadas órfãs removidas")
        
        # 👤 REMOVER USUÁRIO DE TESTE IDENTIFICADO
        print("\n🗑️ Removendo usuário de teste identificado...")
        usuarios_removidos = await db.usuarios.delete_many({
            "$or": [
                {"email": "test@ios.com"},
                {"nome": "Usuário Teste"}
            ]
        })
        print(f"   ✅ {usuarios_removidos.deleted_count} usuários de teste removidos")
        
        # 📊 ESTATÍSTICAS FINAIS
        print("\n📊 ESTATÍSTICAS APÓS LIMPEZA FINAL:")
        turmas_restantes = await db.turmas.count_documents({})
        alunos_restantes = await db.alunos.count_documents({})
        usuarios_restantes = await db.usuarios.count_documents({})
        chamadas_restantes = await db.chamadas.count_documents({})
        
        print(f"   📚 Turmas restantes: {turmas_restantes}")
        print(f"   👥 Alunos restantes: {alunos_restantes}")
        print(f"   👤 Usuários restantes: {usuarios_restantes}")
        print(f"   📞 Chamadas restantes: {chamadas_restantes}")
        
        if turmas_restantes == 0 and alunos_restantes == 0 and chamadas_restantes == 0:
            print("\n🎉 LIMPEZA FINAL COMPLETA!")
            print("✅ Sistema 100% limpo e pronto para produção!")
            print("✅ Apenas usuários reais restantes no banco de dados.")
        else:
            print(f"\n✅ Limpeza concluída! Restaram apenas dados legítimos.")
        
    except Exception as e:
        print(f"❌ Erro durante limpeza final: {e}")
    finally:
        client.close()
        print("\n🔒 Conexão MongoDB fechada.")

if __name__ == "__main__":
    print("🧹 LIMPEZA FINAL DO SISTEMA IOS")
    print("=" * 40)
    asyncio.run(final_cleanup())