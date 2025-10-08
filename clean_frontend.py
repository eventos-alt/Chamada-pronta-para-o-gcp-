#!/usr/bin/env python3
"""
🧹 LIMPEZA FRONTEND - SISTEMA IOS
Remove funções de debug, teste e botões de demonstração
"""

import os
import re

def clean_frontend():
    """Remove funções de debug e teste do frontend"""
    
    frontend_path = "c:/Users/Participante IOS.DESKTOP-DHQGCTG/Documents/Chamada-190925-main/frontend/src/App.js"
    
    print("🔍 Lendo arquivo frontend...")
    with open(frontend_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("📏 Arquivo original:", len(content), "caracteres")
    
    # Remover funções de debug específicas
    patterns_to_remove = [
        # Função handleFixCreatedBy completa
        r'const handleFixCreatedBy = async \(\) => \{.*?\n  \};',
        
        # Função handleCleanupOrphans completa  
        r'const handleCleanupOrphans = async \(\) => \{.*?\n  \};',
        
        # Função handleDebugStudents completa
        r'const handleDebugStudents = async \(userId\) => \{.*?\n  \};',
        
        # Função handleResetDatabase completa
        r'const handleResetDatabase = async \(\) => \{.*?\n  \};',
    ]
    
    # Aplicar remoções com regex multiline
    cleaned_content = content
    total_removed = 0
    
    for pattern in patterns_to_remove:
        matches = re.findall(pattern, cleaned_content, re.DOTALL)
        if matches:
            print(f"🗑️ Removendo: {len(matches)} blocos ({len(matches[0])} chars cada)")
            total_removed += len(matches[0])
            cleaned_content = re.sub(pattern, '  // 🎯 PRODUÇÃO: Função de debug removida', cleaned_content, flags=re.DOTALL)
    
    # Backup do arquivo original
    backup_path = frontend_path + ".backup"
    print(f"💾 Criando backup: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Salvar versão limpa
    print(f"💾 Salvando versão limpa...")
    with open(frontend_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    print("📏 Arquivo limpo:", len(cleaned_content), "caracteres")
    print(f"🗑️ Total removido: {total_removed} caracteres")
    
    # Verificar se limpeza foi bem-sucedida
    debug_terms = ['handleFixCreatedBy', 'handleCleanupOrphans', 'handleDebugStudents', 'handleResetDatabase']
    remaining_debug = []
    
    for term in debug_terms:
        if term in cleaned_content:
            remaining_debug.append(term)
    
    if remaining_debug:
        print(f"⚠️ Ainda restam termos de debug: {remaining_debug}")
    else:
        print("✅ Limpeza completa! Nenhum termo de debug restante.")

if __name__ == "__main__":
    print("🧹 LIMPEZA FRONTEND - SISTEMA IOS")
    print("=" * 40)
    clean_frontend()
    print("=" * 40)
    print("✅ Limpeza frontend concluída!")