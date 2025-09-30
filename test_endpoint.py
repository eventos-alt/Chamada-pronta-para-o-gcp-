import asyncio
import sys
import os
from dotenv import load_dotenv

# Configurar ambiente
sys.path.append('backend')
load_dotenv('backend/.env')

async def test_students_endpoint():
    """Testar diretamente o processamento de alunos"""
    from server import db, parse_from_mongo, Aluno
    
    print("🔍 Testando processamento de alunos...")
    
    # Simular a query do endpoint (admin vê todos)
    query = {"ativo": True}
    
    try:
        # Buscar alunos (limitando para teste)
        alunos = await db.alunos.find(query).limit(5).to_list(5)
        print(f"📊 Encontrados {len(alunos)} alunos para processar")
        
        # Testar o mesmo processamento do endpoint
        result_alunos = []
        for i, aluno in enumerate(alunos, 1):
            try:
                print(f"\n👤 Processando aluno {i}:")
                print(f"   ID: {aluno.get('id', 'SEM_ID')[:8]}...")
                print(f"   Nome: {aluno.get('nome', 'SEM_NOME')}")
                print(f"   Data Nascimento: {aluno.get('data_nascimento')} (tipo: {type(aluno.get('data_nascimento'))})")
                
                parsed_aluno = parse_from_mongo(aluno)
                print(f"   ✅ Parse OK")
                
                # Garantir campos obrigatórios para compatibilidade
                if 'data_nascimento' not in parsed_aluno or parsed_aluno['data_nascimento'] is None:
                    parsed_aluno['data_nascimento'] = None
                    print(f"   📝 data_nascimento definida como None")
                
                aluno_obj = Aluno(**parsed_aluno)
                print(f"   ✅ Modelo Pydantic OK: {aluno_obj.nome}")
                result_alunos.append(aluno_obj)
                
            except Exception as e:
                print(f"   ❌ Erro ao processar: {e}")
                print(f"   Tipo do erro: {type(e)}")
                continue
        
        print(f"\n🎯 Resultado final: {len(result_alunos)} alunos processados com sucesso!")
        return len(result_alunos) > 0
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_students_endpoint())
    print(f"\n{'✅ TESTE PASSOU' if result else '❌ TESTE FALHOU'}")