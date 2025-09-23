#!/usr/bin/env python3
"""
Script de configuración final para GitHub Codespaces
Sistema de Soporte a la Decisión para Mantenimiento Predictivo
Grinding Perú - Arequipa, 2025
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_status(message, status="info"):
    """Imprimir mensaje con formato"""
    colors = {
        "info": "\033[94mℹ️",
        "success": "\033[92m✅",
        "warning": "\033[93m⚠️",
        "error": "\033[91m❌"
    }
    print(f"{colors.get(status, colors['info'])} {message}\033[0m")

def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print_status(f"Ejecutando: {description}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print_status(f"Completado: {description}", "success")
            return True
        else:
            print_status(f"Error en: {description} - {result.stderr}", "error")
            return False
    except Exception as e:
        print_status(f"Excepción en: {description} - {str(e)}", "error")
        return False

def main():
    """Función principal de configuración"""
    print("🚀 CONFIGURACIÓN FINAL DEL SISTEMA")
    print("=" * 50)
    print("Sistema: Grinding Perú - Arequipa, 2025")
    print("Versión: 1.0.0")
    print("")
    
    # 1. Verificar Python
    print_status("Verificando Python...")
    if sys.version_info < (3, 9):
        print_status("Python 3.9+ requerido", "error")
        return False
    
    # 2. Crear estructura de directorios
    print_status("Creando estructura de directorios...")
    directories = [
        "app/core",
        "app/services", 
        "app/api",
        "app/auth",
        "scripts",
        "logs",
        "data",
        "chroma_db"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # 3. Crear archivos __init__.py
    print_status("Creando archivos __init__.py...")
    init_files = [
        "app/__init__.py",
        "app/core/__init__.py",
        "app/services/__init__.py",
        "app/api/__init__.py",
        "app/auth/__init__.py"
    ]
    
    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write('"""Paquete de módulos"""\n')
    
    # 4. Crear archivo .env
    print_status("Configurando variables de entorno...")
    env_content = """SUPABASE_URL=https://bcdfjbnxetnhmfxlofvc.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJjZGZqYm54ZXRuaG1meGxvZnZjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc2Mzk1MTIsImV4cCI6MjA3MzIxNTUxMn0.CivW2USFw5VjRI0Ocyms11h076VBeZwPMQBAvnRh7p8
OPENAI_API_KEY=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
PORT=3000
HOST=0.0.0.0
JWT_SECRET_KEY=grinding-peru-secret-key-2025
ACCESS_TOKEN_EXPIRE_MINUTES=30
LOG_LEVEL=INFO
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    # 5. Instalar dependencias
    print_status("Instalando dependencias...")
    if not run_command("pip install -r requirements.txt", "Instalación de dependencias"):
        return False
    
    # 6. Verificar imports
    print_status("Verificando imports básicos...")
    test_imports = """
try:
    import fastapi
    import uvicorn
    import supabase
    import openai
    from dotenv import load_dotenv
    print('✅ Todos los imports básicos funcionan')
except ImportError as e:
    print(f'❌ Error en import: {e}')
    exit(1)
"""
    
    if not run_command(f"python3 -c \"{test_imports}\"", "Verificación de imports"):
        return False
    
    # 7. Crear script de inicio
    print_status("Creando script de inicio...")
    start_script = """#!/bin/bash
echo "🚀 INICIANDO SISTEMA DE MANTENIMIENTO PREDICTIVO"
echo "================================================"
echo "Sistema: Grinding Perú - Arequipa, 2025"
echo "Versión: 1.0.0"
echo ""
echo "🌐 Iniciando servidor en puerto 3000..."
echo "Accede a: http://localhost:3000"
echo "Documentación: http://localhost:3000/docs"
echo ""
echo "🔑 Credenciales de prueba:"
echo "  Administrador: admin / admin123"
echo "  Supervisor: supervisor1 / admin123"
echo "  Técnico: tecnico1 / admin123"
echo ""
python3 main.py
"""
    
    with open("start_system.sh", "w") as f:
        f.write(start_script)
    
    # Hacer ejecutable
    os.chmod("start_system.sh", 0o755)
    
    # 8. Crear archivo de estado
    print_status("Creando archivo de estado...")
    status = {
        "configured": True,
        "timestamp": "2025-01-15T10:30:00Z",
        "version": "1.0.0",
        "system": "Sistema de Mantenimiento Predictivo - Grinding Perú",
        "features": [
            "Agente Inteligente con RAG",
            "Recomendación Automática de Técnicos",
            "Predicción de Fallas con ML",
            "Gestión Inteligente de Incidencias",
            "Análisis y Reportes Avanzados"
        ]
    }
    
    with open("system_status.json", "w") as f:
        json.dump(status, f, indent=2)
    
    # 9. Mensaje final
    print("")
    print("🎉 CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 50)
    print_status("Sistema configurado para GitHub Codespaces", "success")
    print_status("Todas las dependencias instaladas", "success")
    print_status("Variables de entorno configuradas", "success")
    print_status("Estructura del proyecto verificada", "success")
    print("")
    print_status("Próximos pasos:", "info")
    print("1. Ejecutar: ./start_system.sh")
    print("2. Acceder a: http://localhost:3000")
    print("3. Documentación: http://localhost:3000/docs")
    print("4. Probar endpoints con Postman o curl")
    print("")
    print_status("¡Sistema listo para usar en GitHub Codespaces! 🚀", "success")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print_status("Error en la configuración", "error")
        sys.exit(1)
