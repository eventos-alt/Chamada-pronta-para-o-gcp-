#!/usr/bin/env python3
"""
🚨 RESTAURAÇÃO CRÍTICA: Vínculos Unidade/Curso perdidos
Restaurando vínculos baseados nas informações fornecidas
"""
import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

# 📋 MAPEAMENTO CORRETO DOS USUÁRIOS
USUARIOS_CORRIGIR = {
    "fabiana.coelho@ios.org.br": {
        "unidade": "Jd.Angela", 
        "unidade_id": "4d752e46-e89d-44dc-a974-78adc8e46ae5",
        "curso": "Microsoft Office Essencial + Zendesk",
        "curso_id": "4977d16f-8ad2-4d92-90a1-ec1ba5ea7823"
    },
    "marcus.dourado@ios.org.br": {
        "unidade": "Jd.Angela",
        "unidade_id": "4d752e46-e89d-44dc-a974-78adc8e46ae5", 
        "curso": "Microsoft Office Essencial + Zendesk",
        "curso_id": "4977d16f-8ad2-4d92-90a1-ec1ba5ea7823"
    },
    "ione.almeida@ios.org.br": {
        "unidade": "Santana - SP",
        "unidade_id": "5cb126bf-bf09-41a7-90ee-2292a6bd4b51",
        "curso": "Microsoft Office Essencial + Zendesk", 
        "curso_id": "4977d16f-8ad2-4d92-90a1-ec1ba5ea7823"
    },
    "gabrielle.nobile@ios.org.br": {
        "unidade": "Santana - SP",
        "unidade_id": "5cb126bf-bf09-41a7-90ee-2292a6bd4b51",
        "curso": "Microsoft Office Essencial + Zendesk",
        "curso_id": "4977d16f-8ad2-4d92-90a1-ec1ba5ea7823"
    },
    "ermerson.barros@ios.org.br": {
        "unidade": "Porto Alegre - RS", 
        "unidade_id": "7fb8db70-fc1b-494e-a7b3-a3ef66374638",
        "curso": "Microsoft Office Essencial + Zendesk",
        "curso_id": "4977d16f-8ad2-4d92-90a1-ec1ba5ea7823"
    }
}

async def restaurar_vinculos():
    client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    db = client[os.getenv('DB_NAME')]
    
    print("🔄 INICIANDO RESTAURAÇÃO DE VÍNCULOS...")
    
    for email, dados in USUARIOS_CORRIGIR.items():
        try:
            # Buscar usuário
            usuario = await db.usuarios.find_one({"email": email})
            if not usuario:
                print(f"❌ Usuário {email} não encontrado")
                continue
                
            # Atualizar vínculos
            result = await db.usuarios.update_one(
                {"email": email},
                {"$set": {
                    "unidade_id": dados["unidade_id"],
                    "curso_id": dados["curso_id"]
                }}
            )
            
            if result.modified_count > 0:
                print(f"✅ {usuario['nome']} ({email})")
                print(f"   Unidade: {dados['unidade']}")
                print(f"   Curso: {dados['curso']}")
            else:
                print(f"⚠️ Nenhuma alteração para {email}")
                
        except Exception as e:
            print(f"❌ Erro ao atualizar {email}: {e}")
    
    print("\n🎯 RESTAURAÇÃO CONCLUÍDA!")
    client.close()

if __name__ == "__main__":
    asyncio.run(restaurar_vinculos())