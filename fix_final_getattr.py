#!/usr/bin/env python3
"""
🚨 FIX CRÍTICO: Correção sistemática de TODOS os acessos a curso_id/unidade_id
"""
import re

def fix_remaining_getattr(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corrigir current_user.curso_id sem getattr
    content = re.sub(
        r'current_user\.curso_id(?!\w)',
        "getattr(current_user, 'curso_id', None)",
        content
    )
    
    # Corrigir current_user.unidade_id sem getattr  
    content = re.sub(
        r'current_user\.unidade_id(?!\w)',
        "getattr(current_user, 'unidade_id', None)",
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Todas as referências current_user.curso_id/unidade_id corrigidas!")

if __name__ == "__main__":
    fix_remaining_getattr("backend/server.py")
    print("🎯 CORREÇÃO COMPLETA APLICADA!")