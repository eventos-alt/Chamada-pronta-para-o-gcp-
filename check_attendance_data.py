import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, date, timedelta

# Conectar ao MongoDB
MONGO_URL = "mongodb+srv://jesielamarojunior_db_user:admin123@cluster0.vuho6l7.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority"
client = AsyncIOMotorClient(MONGO_URL)
db = client["IOS-SISTEMA-CHAMADA"]

async def check_attendance_data():
    """Verificar dados de attendance no banco"""
    print("🔍 VERIFICANDO DADOS DE ATTENDANCES...")
    
    # 1. Contar total de attendances
    total_attendances = await db.attendances.count_documents({})
    print(f"📊 Total de attendances: {total_attendances}")
    
    # 2. Buscar algumas attendances de exemplo
    attendances_sample = await db.attendances.find({}).limit(3).to_list(3)
    
    print(f"\n📋 ESTRUTURA DAS ATTENDANCES:")
    for i, att in enumerate(attendances_sample, 1):
        print(f"\n--- Attendance {i} ---")
        print(f"ID: {att.get('id')}")
        print(f"Turma ID: {att.get('turma_id')}")
        print(f"Data: {att.get('data')}")
        print(f"Records: {len(att.get('records', []))} alunos")
        if att.get('records'):
            print(f"Exemplo record: {att['records'][0]}")
    
    # 3. Verificar se existem alunos
    total_alunos = await db.alunos.count_documents({})
    print(f"\n👨‍🎓 Total de alunos: {total_alunos}")
    
    # 4. Verificar turmas
    total_turmas = await db.turmas.count_documents({})
    print(f"🏫 Total de turmas: {total_turmas}")
    
    # 5. Buscar uma turma de exemplo para ver a estrutura
    turma_sample = await db.turmas.find_one({})
    if turma_sample:
        print(f"\n📚 ESTRUTURA DE TURMA:")
        print(f"ID: {turma_sample.get('id')}")
        print(f"Nome: {turma_sample.get('nome')}")
        print(f"Instrutor ID: {turma_sample.get('instrutor_id')}")
        print(f"Curso ID: {turma_sample.get('curso_id')}")
        print(f"Alunos IDs: {turma_sample.get('alunos_ids', [])}")
    
    # 6. Testar query que é usada no CSV
    print(f"\n🔍 TESTANDO QUERY DO CSV...")
    query = {}  # Query vazia como admin
    chamadas = await db.attendances.find(query).limit(5).to_list(5)
    
    print(f"📊 Attendances encontradas com query vazia: {len(chamadas)}")
    
    for chamada in chamadas:
        records = chamada.get("records", [])
        presentes = len([r for r in records if r.get("presente", False)])
        ausentes = len(records) - presentes
        print(f"Data: {chamada.get('data')} | Presentes: {presentes} | Ausentes: {ausentes} | Total: {len(records)}")
    
    # 7. Verificar se há dados recentes (últimos 30 dias)
    data_limite = (date.today() - timedelta(days=30)).isoformat()
    recentes = await db.attendances.count_documents({"data": {"$gte": data_limite}})
    print(f"\n📅 Attendances dos últimos 30 dias: {recentes}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_attendance_data())