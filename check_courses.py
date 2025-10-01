#!/usr/bin/env python3
"""
📋 VERIFICAR CURSOS DISPONÍVEIS NO SISTEMA
Lista todos os cursos para entender as opções disponíveis
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('backend/.env')

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb+srv://jesielamarojunior_db_user:admin123@cluster0.vuho6l7.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority')
DB_NAME = os.environ.get('DB_NAME', 'IOS-SISTEMA-CHAMADA')

async def check_courses_and_units():
    """Verificar cursos e unidades disponíveis"""
    try:
        print("🔌 Conectando ao MongoDB...")
        client = AsyncIOMotorClient(MONGO_URL)
        db = client[DB_NAME]
        
        # Testar conexão
        await client.admin.command('ping')
        print("✅ Conectado ao MongoDB!")
        
        # Listar unidades
        print(f"\n🏢 UNIDADES DISPONÍVEIS:")
        unidades = await db.unidades.find({}).to_list(100)
        for i, unidade in enumerate(unidades, 1):
            print(f"   {i}. {unidade.get('nome', 'N/A')} (ID: {unidade.get('id', 'N/A')})")
        
        # Listar cursos
        print(f"\n📚 CURSOS DISPONÍVEIS:")
        cursos = await db.cursos.find({}).to_list(100)
        for i, curso in enumerate(cursos, 1):
            print(f"   {i}. {curso.get('nome', 'N/A')} (ID: {curso.get('id', 'N/A')})")
        
        # Verificar se "Microsoft Office Essencial + Zendesk" existe
        curso_procurado = "Microsoft Office Essencial + Zendesk"
        curso_encontrado = await db.cursos.find_one({"nome": curso_procurado})
        
        if curso_encontrado:
            print(f"\n✅ CURSO ENCONTRADO: {curso_procurado}")
            print(f"   ID: {curso_encontrado.get('id')}")
            print(f"   Categoria: {curso_encontrado.get('categoria', 'N/A')}")
        else:
            print(f"\n❌ CURSO NÃO ENCONTRADO: {curso_procurado}")
            print(f"   Você precisa criar este curso primeiro!")
        
        # Verificar unidade "Santana - SP"
        unidade_procurada = "Santana - SP"
        unidade_encontrada = await db.unidades.find_one({"nome": unidade_procurada})
        
        if unidade_encontrada:
            print(f"\n✅ UNIDADE ENCONTRADA: {unidade_procurada}")
            print(f"   ID: {unidade_encontrada.get('id')}")
        else:
            print(f"\n❌ UNIDADE NÃO ENCONTRADA: {unidade_procurada}")
            print(f"   Você precisa criar esta unidade primeiro!")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    asyncio.run(check_courses_and_units())