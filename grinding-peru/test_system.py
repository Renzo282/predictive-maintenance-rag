"""
Script de prueba del sistema
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Probar imports básicos"""
    try:
        print("🔍 Probando imports...")
        
        # Test 1: FastAPI
        import fastapi
        print("✅ FastAPI importado correctamente")
        
        # Test 2: Uvicorn
        import uvicorn
        print("✅ Uvicorn importado correctamente")
        
        # Test 3: Supabase
        import supabase
        print("✅ Supabase importado correctamente")
        
        # Test 4: OpenAI
        import openai
        print("✅ OpenAI importado correctamente")
        
        # Test 5: Variables de entorno
        from dotenv import load_dotenv
        load_dotenv()
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if supabase_url and supabase_key and openai_key:
            print("✅ Variables de entorno configuradas")
        else:
            print("❌ Variables de entorno faltantes")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importando: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_app_creation():
    """Probar creación de la aplicación"""
    try:
        print("\n🔍 Probando creación de aplicación...")
        
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        
        app = FastAPI(title="Test App")
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @app.get("/")
        async def root():
            return {"message": "Test successful"}
        
        print("✅ Aplicación FastAPI creada correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error creando aplicación: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("🚀 PRUEBA DEL SISTEMA")
    print("=" * 50)
    
    # Test 1: Imports
    if not test_imports():
        print("\n❌ FALLÓ: Imports básicos")
        return False
    
    # Test 2: Creación de app
    if not test_app_creation():
        print("\n❌ FALLÓ: Creación de aplicación")
        return False
    
    print("\n🎉 TODAS LAS PRUEBAS PASARON")
    print("=" * 50)
    print("✅ Sistema listo para usar")
    print("\n📋 Para iniciar el servidor:")
    print("py main.py")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Algunas pruebas fallaron. Revise los errores anteriores.")
        sys.exit(1)
