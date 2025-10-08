#!/usr/bin/env python3
"""
🧹 SCRIPT DE LIMPEZA COMPLETA - SISTEMA IOS
Remove todos os dados de teste, exemplo e demonstração do MongoDB
Execute apenas UMA vez antes de entregar para produção!
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

async def cleanup_database():
    """Remove todos os dados de teste do MongoDB"""
    
    # Conexão MongoDB
    username = quote_plus("jesielamarojunior_db_user")
    password = quote_plus("admin123")
    MONGO_URL = f"mongodb+srv://{username}:{password}@cluster0.vuho6l7.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority"
    
    print("🔗 Conectando ao MongoDB Atlas...")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client["IOS-SISTEMA-CHAMADA"]
    
    try:
        # 🏫 LIMPAR TURMAS DE TESTE
        print("\n🗑️ Removendo turmas de teste...")
        turmas_removidas = await db.turmas.delete_many({
            "$or": [
                {"nome": {"$regex": "(Teste|Test|Exemplo|Demo|Zendesk|EXTENSÃO)", "$options": "i"}},
                {"nome": {"$regex": "^(Turma [0-9]+|Turma A|Turma B)", "$options": "i"}},
                {"instrutor_nome": {"$regex": "(Teste|Test|Demo)", "$options": "i"}}
            ]
        })
        print(f"   ✅ {turmas_removidas.deleted_count} turmas de teste removidas")
        
        # 👥 LIMPAR ALUNOS DE TESTE
        print("\n🗑️ Removendo alunos de teste...")
        alunos_removidos = await db.alunos.delete_many({
            "$or": [
                {"nome": {"$regex": "^Aluno [0-9]+$", "$options": "i"}},
                {"nome": {"$regex": "(Teste|Test|Exemplo|Demo|Fake)", "$options": "i"}},
                {"email": {"$regex": "(teste|test|fake|exemplo|demo)", "$options": "i"}},
                {"cpf": {"$regex": "^00100000", "$options": "i"}},  # CPFs sequenciais de teste
                {"telefone": {"$regex": "^\\(11\\) 9[0-9]{4}-[0-9]{4}$", "$options": "i"}}  # Telefones sequenciais
            ]
        })
        print(f"   ✅ {alunos_removidos.deleted_count} alunos de teste removidos")
        
        # 📞 LIMPAR CHAMADAS/ATTENDANCE DE TESTE
        print("\n🗑️ Removendo chamadas de teste...")
        chamadas_removidas = await db.chamadas.delete_many({
            "$or": [
                {"turma_nome": {"$regex": "(Teste|Test|Exemplo|Demo)", "$options": "i"}},
                {"instrutor_nome": {"$regex": "(Teste|Test|Demo)", "$options": "i"}}
            ]
        })
        print(f"   ✅ {chamadas_removidas.deleted_count} registros de chamada removidos")
        
        # 👤 LIMPAR USUÁRIOS DE TESTE (MANTER APENAS ADMINS E USUÁRIOS REAIS)
        print("\n🗑️ Removendo usuários de teste...")
        usuarios_removidos = await db.usuarios.delete_many({
            "$and": [
                {"tipo": {"$ne": "admin"}},  # Não remover admins
                {
                    "$or": [
                        {"email": {"$regex": "(teste|test|fake|exemplo|demo)", "$options": "i"}},
                        {"nome": {"$regex": "(Teste|Test|Exemplo|Demo|Fake)", "$options": "i"}},
                        {"status": "pendente"}  # Remover usuários pendentes de teste
                    ]
                }
            ]
        })
        print(f"   ✅ {usuarios_removidos.deleted_count} usuários de teste removidos")
        
        # 📊 LIMPAR RELATÓRIOS E LOGS DE TESTE
        print("\n🗑️ Removendo dados auxiliares de teste...")
        await db.relatorios.delete_many({"tipo": "teste"})
        await db.logs.delete_many({"nivel": "debug"})
        
        # 📈 ESTATÍSTICAS FINAIS
        print("\n📊 ESTATÍSTICAS APÓS LIMPEZA:")
        turmas_restantes = await db.turmas.count_documents({})
        alunos_restantes = await db.alunos.count_documents({})
        usuarios_restantes = await db.usuarios.count_documents({})
        chamadas_restantes = await db.chamadas.count_documents({})
        
        print(f"   📚 Turmas restantes: {turmas_restantes}")
        print(f"   👥 Alunos restantes: {alunos_restantes}")
        print(f"   👤 Usuários restantes: {usuarios_restantes}")
        print(f"   📞 Chamadas restantes: {chamadas_restantes}")
        
        # 🎯 VERIFICAR SE LIMPEZA FOI COMPLETA
        if turmas_restantes == 0 and alunos_restantes == 0:
            print("\n🎉 LIMPEZA COMPLETA! Sistema pronto para produção.")
        else:
            print(f"\n⚠️ Ainda existem {turmas_restantes + alunos_restantes} registros. Verifique se são dados legítimos.")
        
    except Exception as e:
        print(f"❌ Erro durante limpeza: {e}")
    finally:
        client.close()
        print("\n🔒 Conexão MongoDB fechada.")

if __name__ == "__main__":
    print("=" * 60)
    print("🧹 INICIANDO LIMPEZA COMPLETA DO SISTEMA IOS")
    print("=" * 60)
    print("⚠️  ATENÇÃO: Este script remove TODOS os dados de teste!")
    print("⚠️  Execute apenas UMA vez antes de entregar para produção!")
    print("=" * 60)
    
    asyncio.run(cleanup_database())