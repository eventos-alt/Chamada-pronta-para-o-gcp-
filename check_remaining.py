#!/usr/bin/env python3
"""
🔍 VERIFICAR TURMAS RESTANTES - SISTEMA IOS
Lista as turmas que não foram removidas para análise manual
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from urllib.parse import quote_plus
import json

async def check_remaining_data():
    """Verifica os dados restantes após limpeza"""
    
    # Conexão MongoDB
    username = quote_plus("jesielamarojunior_db_user")
    password = quote_plus("admin123")
    MONGO_URL = f"mongodb+srv://{username}:{password}@cluster0.vuho6l7.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority"
    
    print("🔗 Conectando ao MongoDB Atlas...")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client["IOS-SISTEMA-CHAMADA"]
    
    try:
        # 🏫 LISTAR TURMAS RESTANTES
        print("\n📚 TURMAS RESTANTES:")
        turmas = await db.turmas.find({}).to_list(length=None)
        for i, turma in enumerate(turmas, 1):
            print(f"   {i}. Nome: '{turma.get('nome', 'SEM_NOME')}'")
            print(f"      ID: {turma.get('id', 'SEM_ID')}")
            print(f"      Instrutor: {turma.get('instrutor_nome', 'SEM_INSTRUTOR')}")
            print(f"      Curso: {turma.get('curso_nome', 'SEM_CURSO')}")
            print(f"      Tipo: {turma.get('tipo_turma', 'INDEFINIDO')}")
            print(f"      Alunos: {len(turma.get('alunos_ids', []))}")
            print()
        
        # 👥 LISTAR ALUNOS RESTANTES
        print("\n👥 ALUNOS RESTANTES:")
        alunos = await db.alunos.find({}).to_list(length=None)
        for i, aluno in enumerate(alunos, 1):
            print(f"   {i}. Nome: '{aluno.get('nome', 'SEM_NOME')}'")
            print(f"      CPF: {aluno.get('cpf', 'SEM_CPF')}")
            print(f"      Email: {aluno.get('email', 'SEM_EMAIL')}")
            print()
        
        # 👤 LISTAR USUÁRIOS RESTANTES
        print("\n👤 USUÁRIOS RESTANTES:")
        usuarios = await db.usuarios.find({}).to_list(length=None)
        for i, usuario in enumerate(usuarios, 1):
            print(f"   {i}. Nome: '{usuario.get('nome', 'SEM_NOME')}'")
            print(f"      Email: {usuario.get('email', 'SEM_EMAIL')}")
            print(f"      Tipo: {usuario.get('tipo', 'SEM_TIPO')}")
            print(f"      Status: {usuario.get('status', 'SEM_STATUS')}")
            print()
            
        # 📞 LISTAR CHAMADAS RESTANTES
        print("\n📞 CHAMADAS RESTANTES:")
        chamadas = await db.chamadas.find({}).to_list(length=None)
        for i, chamada in enumerate(chamadas, 1):
            print(f"   {i}. Data: {chamada.get('data', 'SEM_DATA')}")
            print(f"      Turma: {chamada.get('turma_nome', 'SEM_TURMA')}")
            print(f"      Instrutor: {chamada.get('instrutor_nome', 'SEM_INSTRUTOR')}")
            print()
            
    except Exception as e:
        print(f"❌ Erro durante verificação: {e}")
    finally:
        client.close()
        print("🔒 Conexão MongoDB fechada.")

if __name__ == "__main__":
    print("🔍 VERIFICANDO DADOS RESTANTES APÓS LIMPEZA")
    print("=" * 50)
    asyncio.run(check_remaining_data())