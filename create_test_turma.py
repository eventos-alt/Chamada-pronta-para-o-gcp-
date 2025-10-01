#!/usr/bin/env python3
"""
🏗️ CRIAR TURMA PARA TESTE DA LÓGICA DO INSTRUTOR
Cria uma turma e associa alunos para testar a nova lógica
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import uuid

# Carregar variáveis de ambiente
load_dotenv('backend/.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb+srv://jesielamarojunior_db_user:admin123@cluster0.vuho6l7.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority')
DB_NAME = os.environ.get('DB_NAME', 'IOS-SISTEMA-CHAMADA')

async def create_test_turma():
    """Criar turma de teste para instrutor"""
    try:
        print("🔌 Conectando ao MongoDB...")
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        # Testar conexão
        await client.admin.command('ping')
        print("✅ Conectado ao MongoDB!")
        
        # Buscar instrutor Fabiana
        instrutor = await db.usuarios.find_one({"email": "fabiana.coelho@ios.org.br"})
        if not instrutor:
            print("❌ Instrutor Fabiana não encontrado")
            return
            
        print(f"\n👨‍🏫 INSTRUTOR SELECIONADO:")
        print(f"   Nome: {instrutor.get('nome')}")
        print(f"   Email: {instrutor.get('email')}")
        print(f"   Curso ID: {instrutor.get('curso_id')}")
        print(f"   Unidade ID: {instrutor.get('unidade_id')}")
        
        # Buscar alguns alunos para adicionar na turma (criamos 60 alunos após o reset)
        alunos = await db.alunos.find({"ativo": True}).limit(5).to_list(5)
        aluno_ids = [aluno["id"] for aluno in alunos]
        
        print(f"\n👥 ALUNOS PARA ADICIONAR NA TURMA:")
        for aluno in alunos:
            print(f"   • {aluno.get('nome', 'N/A')} - {aluno.get('cpf', 'N/A')}")
        
        # Criar turma de teste
        turma_data = {
            "id": str(uuid.uuid4()),
            "nome": f"Turma Teste - {instrutor.get('nome')}",
            "curso_id": instrutor.get('curso_id'),
            "unidade_id": instrutor.get('unidade_id'),
            "instrutor_id": instrutor.get('id'),
            "alunos_ids": aluno_ids,
            "ativo": True,
            "data_inicio": "2025-10-01",
            "data_fim": "2025-12-31",
            "dias_semana": ["segunda", "quarta", "sexta"],
            "horario_inicio": "08:00",
            "horario_fim": "12:00"
        }
        
        # Verificar se já existe uma turma de teste
        turma_existente = await db.turmas.find_one({"nome": turma_data["nome"]})
        if turma_existente:
            print(f"\n⚠️ Turma já existe, removendo primeiro...")
            await db.turmas.delete_one({"id": turma_existente["id"]})
        
        # Inserir turma
        result = await db.turmas.insert_one(turma_data)
        
        if result.inserted_id:
            print(f"\n✅ TURMA CRIADA COM SUCESSO!")
            print(f"   ID: {turma_data['id']}")
            print(f"   Nome: {turma_data['nome']}")
            print(f"   Instrutor: {instrutor.get('nome')}")
            print(f"   Alunos: {len(aluno_ids)}")
            
            # Testar a nova lógica agora
            print(f"\n🧪 TESTANDO NOVA LÓGICA COM A TURMA CRIADA:")
            
            # Buscar turmas do instrutor (deve encontrar 1 agora)
            turmas_instrutor = await db.turmas.find({
                "curso_id": instrutor.get('curso_id'),
                "unidade_id": instrutor.get('unidade_id'),
                "instrutor_id": instrutor.get('id'),
                "ativo": True
            }).to_list(1000)
            
            print(f"   Turmas encontradas: {len(turmas_instrutor)}")
            
            # Coletar IDs dos alunos
            aluno_ids_encontrados = set()
            for turma in turmas_instrutor:
                turma_alunos = turma.get("alunos_ids", [])
                aluno_ids_encontrados.update(turma_alunos)
                print(f"   • Turma '{turma['nome']}': {len(turma_alunos)} alunos")
            
            print(f"\n✅ RESULTADO: Instrutor deve ver {len(aluno_ids_encontrados)} alunos!")
            print(f"   Isso é muito mais específico que ver todos os 60 alunos do sistema.")
            
        else:
            print(f"\n❌ Falha ao criar turma")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(create_test_turma())