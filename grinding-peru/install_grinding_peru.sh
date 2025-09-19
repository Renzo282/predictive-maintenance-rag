#!/bin/bash

# Script de instalación para Grinding Perú
# Agente Inteligente de Mantenimiento Predictivo con RAG

echo "🏭 Instalando Agente Inteligente de Mantenimiento Predictivo para Grinding Perú..."

# Verificar Python 3.9+
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.9 o superior es requerido. Versión actual: $python_version"
    exit 1
fi

echo "✅ Verificación de Python completada: $python_version"

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv venv

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
echo "⬆️ Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install -r ../requirements.txt

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p data/vector_store
mkdir -p models
mkdir -p logs
mkdir -p reports

# Copiar archivo de configuración
echo "⚙️ Configurando entorno..."
if [ ! -f .env ]; then
    cp ../config.env .env
    echo "📝 Archivo .env creado desde config.env"
    echo "⚠️  Por favor, actualiza .env con las credenciales de Grinding Perú"
else
    echo "✅ Archivo .env ya existe"
fi

# Inicializar base de datos
echo "🗄️ Inicializando base de datos para Grinding Perú..."
python scripts/init_grinding_peru_db.py

echo ""
echo "🎉 Instalación completada exitosamente para Grinding Perú!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Actualizar archivo .env con credenciales de Grinding Perú"
echo "2. Activar entorno virtual: source venv/bin/activate"
echo "3. Iniciar aplicación: python main.py"
echo "4. Acceder a documentación: http://localhost:3000/docs"
echo "5. Probar API: http://localhost:3000/api/v1/grinding-peru/health"
echo ""
echo "🏭 Sistema configurado específicamente para Grinding Perú"
echo "📊 Alineado con estándares ISO/IEC 20000"
echo "🤖 Capacidades de RAG y análisis predictivo habilitadas"
echo ""
echo "Para más información, consulta DOCUMENTATION.md"
