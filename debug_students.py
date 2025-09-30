# Debug script para testar o endpoint de alunos
import os
import sys
import asyncio
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Carregar variáveis de ambiente
load_dotenv('backend/.env')

# Configuração MongoDB
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

async def debug_students():
    """Debug dos dados de alunos no MongoDB"""
    print("🔍 Debugging dados de alunos...")
    
    # Contar total de alunos
    total_alunos = await db.alunos.count_documents({})
    print(f"📊 Total de alunos no banco: {total_alunos}")
    
    # Buscar alguns alunos para análise
    alunos = await db.alunos.find({}).limit(3).to_list(3)
    
    for i, aluno in enumerate(alunos, 1):
        print(f"\n👤 Aluno {i}:")
        print(f"   ID: {aluno.get('id', 'SEM ID')}")
        print(f"   Nome: {aluno.get('nome', 'SEM NOME')}")
        print(f"   CPF: {aluno.get('cpf', 'SEM CPF')}")
        print(f"   Data Nascimento: {aluno.get('data_nascimento', 'SEM DATA')} (tipo: {type(aluno.get('data_nascimento'))})")
        print(f"   Status: {aluno.get('status', 'SEM STATUS')}")
        print(f"   Ativo: {aluno.get('ativo', 'SEM ATIVO')}")
        print(f"   Created At: {aluno.get('created_at', 'SEM CREATED_AT')} (tipo: {type(aluno.get('created_at'))})")

async def test_parse_function():
    """Testar função parse_from_mongo com path correto"""
    import sys
    sys.path.append('backend')
    
    from server import parse_from_mongo, Aluno
    
    # Buscar um aluno real do banco
    aluno_raw = await db.alunos.find_one({})
    if not aluno_raw:
        print("❌ Nenhum aluno encontrado no banco")
        return
    
    print(f"\n🔄 Testando parse_from_mongo...")
    print(f"Dados brutos (parciais): id={aluno_raw.get('id')}, nome={aluno_raw.get('nome')}")
    
    try:
        aluno_parsed = parse_from_mongo(aluno_raw.copy())
        print(f"✅ Parse OK para aluno: {aluno_parsed.get('nome')}")
        
        # Testar criação do modelo Pydantic
        aluno_obj = Aluno(**aluno_parsed)
        print(f"✅ Modelo Pydantic OK: {aluno_obj.nome}")
        return True
        
    except Exception as e:
        print(f"❌ Erro no parse/modelo: {e}")
        print(f"Tipo do erro: {type(e)}")
        # Debug específico para data_nascimento
        if 'data_nascimento' in str(e):
            print(f"🔍 data_nascimento problemática: {aluno_raw.get('data_nascimento')} (tipo: {type(aluno_raw.get('data_nascimento'))})")
        return False

if __name__ == "__main__":
    asyncio.run(debug_students())
    asyncio.run(test_parse_function())