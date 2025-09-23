"""
Configuración Simple del Sistema
"""

import os
import sys

def main():
    print("🚀 CONFIGURACIÓN SIMPLE DEL SISTEMA")
    print("=" * 50)
    
    # Crear archivos __init__.py necesarios
    init_files = [
        "app/__init__.py",
        "app/core/__init__.py", 
        "app/services/__init__.py",
        "app/api/__init__.py",
        "app/auth/__init__.py"
    ]
    
    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, "w", encoding="utf-8") as f:
                f.write('"""Paquete de módulos"""\n')
            print(f"✅ Creado: {init_file}")
        else:
            print(f"✅ Existe: {init_file}")
    
    print("\n🎉 CONFIGURACIÓN COMPLETADA")
    print("=" * 50)
    print("✅ Sistema listo para usar")
    print("\n📋 Próximos pasos:")
    print("1. Ejecutar: py main.py")
    print("2. Acceder a: http://localhost:3000")
    print("3. Documentación: http://localhost:3000/docs")

if __name__ == "__main__":
    main()
