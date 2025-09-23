"""
Configuración Rápida del Sistema
Sistema de Soporte a la Decisión para Mantenimiento Predictivo
"""

import os
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Configuración rápida del sistema"""
    try:
        print("🚀 CONFIGURACIÓN RÁPIDA DEL SISTEMA")
        print("=" * 50)
        
        # 1. Verificar archivo .env
        print("1. Verificando configuración...")
        if os.path.exists(".env"):
            print("✅ Archivo .env encontrado")
        else:
            print("❌ Archivo .env no encontrado")
            return False
        
        # 2. Verificar dependencias
        print("2. Verificando dependencias...")
        try:
            import fastapi
            import uvicorn
            import supabase
            import openai
            print("✅ Dependencias principales instaladas")
        except ImportError as e:
            print(f"❌ Dependencia faltante: {e}")
            print("Ejecute: py -m pip install -r requirements.txt")
            return False
        
        # 3. Verificar variables de entorno
        print("3. Verificando variables de entorno...")
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "OPENAI_API_KEY"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Variables faltantes: {', '.join(missing_vars)}")
            return False
        else:
            print("✅ Variables de entorno configuradas")
        
        # 4. Crear estructura de directorios
        print("4. Verificando estructura de directorios...")
        directories = [
            "app/core",
            "app/services", 
            "app/api",
            "app/auth",
            "scripts",
            "logs"
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                print(f"✅ Directorio {directory} creado")
            else:
                print(f"✅ Directorio {directory} existe")
        
        # 5. Crear archivos __init__.py
        print("5. Creando archivos __init__.py...")
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
                print(f"✅ Archivo {init_file} creado")
        
        print("\n🎉 CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 50)
        print("✅ Sistema listo para usar")
        print("\n📋 Próximos pasos:")
        print("1. Ejecutar: py main.py")
        print("2. Acceder a: http://localhost:3000")
        print("3. Documentación: http://localhost:3000/docs")
        print("4. Probar endpoints con Postman o curl")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 ¡Sistema configurado y listo para usar!")
    else:
        print("\n❌ Error en la configuración. Revise los pasos anteriores.")
