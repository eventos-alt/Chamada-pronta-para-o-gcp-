#!/usr/bin/env python3
"""
📊 Script de Exportação CSV - Sistema IOS
Exporta dados de presença do MongoDB para CSV detalhado

Uso:
    python export_attendance_csv.py
    
Requisitos:
    pip install pandas pymongo python-dotenv

Formato do CSV gerado:
    Aluno, CPF, Matricula, Turma, Curso, Data, Hora_Inicio, 
    Hora_Fim, Status, Hora_Registro, Professor, Unidade, Observacoes
"""

import pandas as pd
from pymongo import MongoClient
from datetime import datetime, date
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def connect_to_mongodb():
    """Conecta ao MongoDB usando variáveis de ambiente"""
    try:
        mongo_url = os.getenv("MONGO_URL")
        db_name = os.getenv("DB_NAME", "ios_sistema")
        
        if not mongo_url:
            raise ValueError("MONGO_URL não encontrada no arquivo .env")
        
        client = MongoClient(mongo_url)
        db = client[db_name]
        
        # Testar conexão
        db.admin.command('ping')
        print(f"✅ Conectado ao MongoDB: {db_name}")
        
        return db
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao MongoDB: {e}")
        return None

def export_attendance_to_csv(db, output_file="relatorio_presenca_completo.csv"):
    """
    Exporta dados de presença para CSV com formato detalhado
    
    Args:
        db: Conexão com MongoDB
        output_file: Nome do arquivo CSV de saída
    """
    try:
        print("📊 Coletando dados de presença...")
        
        # Buscar todas as chamadas
        chamadas = list(db.chamadas.find({}))
        
        if not chamadas:
            print("⚠️  Nenhuma chamada encontrada no banco de dados")
            return
        
        print(f"📋 Encontradas {len(chamadas)} chamadas registradas")
        
        # Lista para armazenar dados do CSV
        csv_data = []
        
        # Processar cada chamada
        for chamada in chamadas:
            try:
                # Buscar dados da turma
                turma = db.turmas.find_one({"id": chamada.get("turma_id")})
                if not turma:
                    print(f"⚠️  Turma não encontrada: {chamada.get('turma_id')}")
                    continue
                
                # Buscar dados do curso
                curso = db.cursos.find_one({"id": turma.get("curso_id")}) if turma.get("curso_id") else None
                
                # Buscar dados da unidade
                unidade = db.unidades.find_one({"id": turma.get("unidade_id")}) if turma.get("unidade_id") else None
                
                # Buscar dados do instrutor
                instrutor = db.usuarios.find_one({"id": turma.get("instrutor_id")}) if turma.get("instrutor_id") else None
                
                # Dados da chamada
                data_chamada = chamada.get("data", "")
                presencas = chamada.get("presencas", {})
                observacoes_gerais = chamada.get("observacoes", "")
                
                # Horários da turma
                hora_inicio = turma.get("horario_inicio", "08:00")
                hora_fim = turma.get("horario_fim", "12:00")
                
                # Processar cada aluno na chamada
                for aluno_id, dados_presenca in presencas.items():
                    try:
                        # Buscar dados completos do aluno
                        aluno = db.alunos.find_one({"id": aluno_id})
                        if not aluno:
                            print(f"⚠️  Aluno não encontrado: {aluno_id}")
                            continue
                        
                        # Determinar status detalhado
                        presente = dados_presenca.get("presente", False)
                        justificativa = dados_presenca.get("justificativa", "")
                        hora_registro = dados_presenca.get("hora_registro", "")
                        
                        # Status mais detalhado
                        if presente:
                            if hora_registro and hora_registro > hora_inicio:
                                status = "Atrasado"
                            else:
                                status = "Presente"
                        else:
                            if justificativa and ("atestado" in justificativa.lower() or "justificada" in justificativa.lower()):
                                status = "Justificado"
                            else:
                                status = "Ausente"
                        
                        # Observações combinadas
                        obs_final = []
                        if justificativa:
                            obs_final.append(justificativa)
                        if observacoes_gerais:
                            obs_final.append(f"Obs. turma: {observacoes_gerais}")
                        observacoes_texto = "; ".join(obs_final)
                        
                        # Adicionar linha aos dados
                        csv_data.append({
                            "Aluno": aluno.get("nome", ""),
                            "CPF": aluno.get("cpf", ""),
                            "Matricula": aluno.get("matricula", aluno.get("id", "")),
                            "Turma": turma.get("nome", ""),
                            "Curso": curso.get("nome", "") if curso else "",
                            "Data": data_chamada,
                            "Hora_Inicio": hora_inicio,
                            "Hora_Fim": hora_fim,
                            "Status": status,
                            "Hora_Registro": hora_registro,
                            "Professor": instrutor.get("nome", "") if instrutor else "",
                            "Unidade": unidade.get("nome", "") if unidade else "",
                            "Observacoes": observacoes_texto
                        })
                        
                    except Exception as e:
                        print(f"❌ Erro ao processar aluno {aluno_id}: {e}")
                        continue
                        
            except Exception as e:
                print(f"❌ Erro ao processar chamada {chamada.get('id', 'unknown')}: {e}")
                continue
        
        if not csv_data:
            print("⚠️  Nenhum dado válido encontrado para exportação")
            return
        
        # Criar DataFrame e exportar
        df = pd.DataFrame(csv_data)
        
        # Ordenar por data e turma
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        df = df.sort_values(['Data', 'Turma', 'Aluno'])
        df['Data'] = df['Data'].dt.strftime('%Y-%m-%d')
        
        # Exportar para CSV
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        
        print(f"✅ CSV gerado com sucesso: {output_file}")
        print(f"📊 Total de registros: {len(csv_data)}")
        print(f"📅 Período: {df['Data'].min()} a {df['Data'].max()}")
        print(f"🏫 Turmas: {df['Turma'].nunique()}")
        print(f"👥 Alunos únicos: {df['Aluno'].nunique()}")
        
        # Estatísticas de presença
        status_counts = df['Status'].value_counts()
        print("\n📈 Estatísticas de Presença:")
        for status, count in status_counts.items():
            print(f"   {status}: {count}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Erro durante exportação: {e}")
        return None

def main():
    """Função principal"""
    print("🚀 Sistema de Exportação CSV - IOS")
    print("=" * 50)
    
    # Conectar ao MongoDB
    db = connect_to_mongodb()
    if not db:
        return
    
    # Gerar nome do arquivo com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"relatorio_presenca_{timestamp}.csv"
    
    # Exportar dados
    result = export_attendance_to_csv(db, output_file)
    
    if result:
        print(f"\n🎉 Exportação concluída com sucesso!")
        print(f"📁 Arquivo: {result}")
    else:
        print(f"\n❌ Falha na exportação")

if __name__ == "__main__":
    main()