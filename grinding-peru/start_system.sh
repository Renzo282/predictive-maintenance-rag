#!/bin/bash

# Script de inicio del sistema
# Sistema de Soporte a la Decisión para Mantenimiento Predictivo
# Grinding Perú - Arequipa, 2025

echo "🚀 INICIANDO SISTEMA DE MANTENIMIENTO PREDICTIVO"
echo "================================================"
echo "Sistema: Grinding Perú - Arequipa, 2025"
echo "Versión: 1.0.0"
echo ""

# Verificar que el archivo .env existe
if [ ! -f ".env" ]; then
    echo "⚠️ Archivo .env no encontrado. Ejecutando configuración..."
    ./scripts/codespace_setup.sh
fi

# Verificar dependencias
echo "🔍 Verificando dependencias..."
python3 -c "
try:
    import fastapi
    import uvicorn
    import supabase
    import openai
    print('✅ Dependencias verificadas')
except ImportError as e:
    print(f'❌ Dependencia faltante: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Error en dependencias. Instalando..."
    pip install -r requirements.txt
fi

echo ""
echo "🌐 Iniciando servidor en puerto 3000..."
echo "Accede a: http://localhost:3000"
echo "Documentación: http://localhost:3000/docs"
echo "ReDoc: http://localhost:3000/redoc"
echo ""
echo "🔑 Credenciales de prueba:"
echo "  Administrador: admin / admin123"
echo "  Supervisor: supervisor1 / admin123"
echo "  Técnico: tecnico1 / admin123"
echo ""
echo "📋 Funcionalidades disponibles:"
echo "  ✅ Gestión de usuarios y roles"
echo "  ✅ Registro de equipos"
echo "  ✅ Gestión de incidencias"
echo "  ✅ Predicción de fallas"
echo "  ✅ Recomendación de técnicos"
echo "  ✅ Análisis y reportes"
echo ""

# Iniciar el servidor
python3 main.py
