import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, date, timedelta
import csv
from io import StringIO

# Conectar ao MongoDB
MONGO_URL = "mongodb+srv://jesielamarojunior_db_user:admin123@cluster0.vuho6l7.mongodb.net/IOS-SISTEMA-CHAMADA?retryWrites=true&w=majority"
client = AsyncIOMotorClient(MONGO_URL)
db = client["IOS-SISTEMA-CHAMADA"]

async def generate_frequency_csv():
    """GErar CSV de frequência por aluno diretamente do MongoDB"""
    
    print("🔍 GERANDO CSV DE FREQUÊNCIA POR ALUNO...")
    
    # Buscar todas as attendances
    attendances = await db.attendances.find({}).to_list(1000)
    print(f"📊 Total de attendances encontradas: {len(attendances)}")
    
    # Calcular estatísticas por aluno
    aluno_stats = {}
    
    for attendance in attendances:
        turma_id = attendance.get("turma_id")
        records = attendance.get("records", [])
        
        print(f"Processando attendance {attendance.get('data')} com {len(records)} records")
        
        for record in records:
            aluno_id = record.get("aluno_id")
            presente = record.get("presente", False)
            
            if aluno_id not in aluno_stats:
                aluno_stats[aluno_id] = {
                    "total_chamadas": 0,
                    "total_presencas": 0,
                    "total_faltas": 0,
                    "turma_id": turma_id
                }
            
            aluno_stats[aluno_id]["total_chamadas"] += 1
            if presente:
                aluno_stats[aluno_id]["total_presencas"] += 1
            else:
                aluno_stats[aluno_id]["total_faltas"] += 1
    
    print(f"📊 Estatísticas calculadas para {len(aluno_stats)} alunos")
    
    # Gerar CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Cabeçalhos
    writer.writerow([
        "Nome do Aluno", "CPF", "Total de Chamadas", "Presencas", "Faltas", 
        "% Presença (Preciso)", "Classificação de Risco", "Status do Aluno", 
        "Data de Nascimento", "Email"
    ])
    
    # Processar cada aluno
    for aluno_id, stats in aluno_stats.items():
        try:
            # Buscar dados do aluno
            aluno = await db.alunos.find_one({"id": aluno_id})
            if not aluno:
                print(f"⚠️ Aluno {aluno_id} não encontrado")
                continue
            
            # Calcular percentual
            total_chamadas = stats["total_chamadas"]
            total_presencas = stats["total_presencas"]
            percentual = round((total_presencas / total_chamadas * 100), 2) if total_chamadas > 0 else 0.0
            
            # Classificação de risco
            if percentual >= 75:
                risco = "Situação Normal"
            elif percentual >= 50:
                risco = "Atenção"
            else:
                risco = "Situação Crítica"
            
            # Formatar data de nascimento
            data_nasc = aluno.get("data_nascimento")
            if data_nasc:
                if isinstance(data_nasc, str):
                    data_nasc_str = data_nasc
                else:
                    data_nasc_str = str(data_nasc)
            else:
                data_nasc_str = "N/A"
            
            # Escrever linha
            writer.writerow([
                aluno.get("nome", ""),
                aluno.get("cpf", ""),
                stats["total_chamadas"],
                stats["total_presencas"],
                stats["total_faltas"],
                f"{percentual:.2f}%",
                risco,
                aluno.get("status", "ativo").title(),
                data_nasc_str,
                aluno.get("email", "N/A")
            ])
            
            print(f"✅ Processado: {aluno.get('nome', 'Nome?')} - {total_chamadas} chamadas, {total_presencas} presenças ({percentual:.1f}%)")
            
        except Exception as e:
            print(f"❌ Erro ao processar aluno {aluno_id}: {e}")
            continue
    
    # Salvar CSV
    csv_content = output.getvalue()
    with open("relatorio_frequencia_corrigido.csv", "w", encoding="utf-8-sig") as f:
        f.write(csv_content)
    
    print(f"✅ CSV gerado com sucesso: relatorio_frequencia_corrigido.csv")
    print(f"📋 Total de linhas: {len(csv_content.splitlines())}")
    
    # Mostrar preview
    lines = csv_content.splitlines()
    if len(lines) > 1:
        print(f"\n📋 PREVIEW:")
        print("CABEÇALHO:", lines[0])
        print("LINHA 1:", lines[1] if len(lines) > 1 else "Vazio")
        print("LINHA 2:", lines[2] if len(lines) > 2 else "Vazio")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(generate_frequency_csv())