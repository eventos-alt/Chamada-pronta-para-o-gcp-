#!/usr/bin/env python3
"""
🧪 TESTE DA NOVA LÓGICA DE INSTRUTOR
Testa se a lógica de visualização de alunos está funcionando corretamente
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('backend/.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb+srv://jesielamarojunior_db_user:admin123@cluster0.vuho6l7.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority')
DB_NAME = os.environ.get('DB_NAME', 'IOS-SISTEMA-CHAMADA')

async def test_instructor_logic():
    """Testar nova lógica do instrutor"""
    try:
        print("🔌 Conectando ao MongoDB...")
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        # Testar conexão
        await client.admin.command('ping')
        print("✅ Conectado ao MongoDB!")
        
        # Buscar um instrutor para teste
        instrutor = await db.usuarios.find_one({"tipo": "instrutor"})
        if not instrutor:
            print("❌ Nenhum instrutor encontrado para teste")
            return
            
        print(f"\n🧪 TESTANDO LÓGICA PARA INSTRUTOR:")
        print(f"   Nome: {instrutor.get('nome')}")
        print(f"   Email: {instrutor.get('email')}")
        print(f"   Curso ID: {instrutor.get('curso_id', 'N/A')}")
        print(f"   Unidade ID: {instrutor.get('unidade_id', 'N/A')}")
        
        # Simular a nova lógica
        if not instrutor.get('curso_id') or not instrutor.get('unidade_id'):
            print("❌ Instrutor sem curso ou unidade definida")
            return
            
        # Buscar turmas do instrutor
        turmas_instrutor = await db.turmas.find({
            "curso_id": instrutor.get('curso_id'),
            "unidade_id": instrutor.get('unidade_id'),
            "instrutor_id": instrutor.get('id'),
            "ativo": True
        }).to_list(1000)
        
        print(f"\n📚 TURMAS DO INSTRUTOR: {len(turmas_instrutor)}")
        
        # Coletar alunos
        aluno_ids = set()
        for turma in turmas_instrutor:
            turma_alunos = turma.get("alunos_ids", [])
            aluno_ids.update(turma_alunos)
            print(f"   • {turma.get('nome', 'N/A')}: {len(turma_alunos)} alunos")
        
        print(f"\n👥 TOTAL DE ALUNOS QUE O INSTRUTOR DEVE VER: {len(aluno_ids)}")
        
        if aluno_ids:
            # Buscar os alunos reais
            alunos = await db.alunos.find({"id": {"$in": list(aluno_ids)}}).to_list(1000)
            print(f"✅ Alunos encontrados no banco: {len(alunos)}")
            
            for aluno in alunos[:5]:  # Mostrar só os primeiros 5
                print(f"   • {aluno.get('nome', 'N/A')} - {aluno.get('cpf', 'N/A')}")
            
            if len(alunos) > 5:
                print(f"   ... e mais {len(alunos) - 5} alunos")
        else:
            print("❌ Nenhum aluno encontrado nas turmas do instrutor")
        
        # Comparar com a lógica antiga (todos os alunos ativos)
        todos_alunos = await db.alunos.count_documents({"ativo": True})
        print(f"\n📊 COMPARAÇÃO:")
        print(f"   Lógica ANTIGA (todos os alunos): {todos_alunos} alunos")
        print(f"   Lógica NOVA (só das turmas): {len(aluno_ids)} alunos")
        print(f"   Diferença: {todos_alunos - len(aluno_ids)} alunos a menos (mais específico)")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(test_instructor_logic())