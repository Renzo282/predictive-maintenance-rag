#!/bin/bash

# Script de configuración para GitHub Codespaces
# Sistema de Soporte a la Decisión para Mantenimiento Predictivo
# Grinding Perú - Arequipa, 2025

echo "🚀 CONFIGURANDO SISTEMA EN GITHUB CODESPACES"
echo "=============================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con color
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# 1. Verificar Python
print_info "Verificando Python..."
python3 --version
if [ $? -eq 0 ]; then
    print_status "Python instalado correctamente"
else
    print_error "Python no encontrado"
    exit 1
fi

# 2. Actualizar pip
print_info "Actualizando pip..."
python3 -m pip install --upgrade pip

# 3. Instalar dependencias
print_info "Instalando dependencias del sistema..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    print_status "Dependencias instaladas correctamente"
else
    print_error "Error instalando dependencias"
    exit 1
fi

# 4. Crear archivo .env
print_info "Configurando variables de entorno..."
cat > .env << EOF
SUPABASE_URL=https://bcdfjbnxetnhmfxlofvc.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJjZGZqYm54ZXRuaG1meGxvZnZjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc2Mzk1MTIsImV4cCI6MjA3MzIxNTUxMn0.CivW2USFw5VjRI0Ocyms11h076VBeZwPMQBAvnRh7p8
OPENAI_API_KEY=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
PORT=3000
JWT_SECRET_KEY=grinding-peru-secret-key-2025
ACCESS_TOKEN_EXPIRE_MINUTES=30
HOST=0.0.0.0
LOG_LEVEL=INFO
EOF

print_status "Archivo .env creado"

# 5. Crear directorios necesarios
print_info "Creando estructura de directorios..."
mkdir -p logs
mkdir -p data
mkdir -p chroma_db

# 6. Crear archivos __init__.py
print_info "Creando archivos __init__.py..."
touch app/__init__.py
touch app/core/__init__.py
touch app/services/__init__.py
touch app/api/__init__.py
touch app/auth/__init__.py

# 7. Verificar estructura
print_info "Verificando estructura del proyecto..."
if [ -f "main.py" ] && [ -f "requirements.txt" ] && [ -f ".env" ]; then
    print_status "Estructura del proyecto verificada"
else
    print_error "Estructura del proyecto incompleta"
    exit 1
fi

# 8. Probar imports básicos
print_info "Probando imports básicos..."
python3 -c "
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
"

if [ $? -eq 0 ]; then
    print_status "Imports básicos verificados"
else
    print_error "Error en imports básicos"
    exit 1
fi

# 9. Crear script de inicio
print_info "Creando script de inicio..."
cat > start_system.sh << 'EOF'
#!/bin/bash
echo "🚀 INICIANDO SISTEMA DE MANTENIMIENTO PREDICTIVO"
echo "================================================"
echo "Sistema: Grinding Perú - Arequipa, 2025"
echo "Versión: 1.0.0"
echo ""
echo "Iniciando servidor en puerto 3000..."
echo "Accede a: http://localhost:3000"
echo "Documentación: http://localhost:3000/docs"
echo ""
python3 main.py
EOF

chmod +x start_system.sh
print_status "Script de inicio creado"

# 10. Crear README para Codespaces
print_info "Creando documentación para Codespaces..."
cat > CODESPACE_README.md << 'EOF'
# 🚀 Sistema de Mantenimiento Predictivo - Grinding Perú

## Configuración en GitHub Codespaces

### Inicio Rápido
```bash
# 1. Ejecutar configuración inicial
./scripts/codespace_setup.sh

# 2. Iniciar sistema
./start_system.sh
```

### Acceso al Sistema
- **URL Principal**: http://localhost:3000
- **Documentación API**: http://localhost:3000/docs
- **ReDoc**: http://localhost:3000/redoc

### Funcionalidades Implementadas

#### 🔐 Autenticación
- Login seguro con JWT
- Roles: Administrador, Supervisor, Técnico
- Gestión de usuarios

#### 🔧 Gestión de Equipos
- Registro de equipos
- Clasificación por criticidad
- Historial de mantenimiento
- Datos de sensores

#### 📋 Gestión de Incidencias
- Registro inteligente de incidencias
- Asignación automática de técnicos
- Clasificación de prioridades
- Seguimiento en tiempo real

#### 🤖 Predicción Inteligente
- Predicción de fallas con ML
- Recomendación de técnicos
- Análisis de anomalías
- Alertas proactivas

#### 📊 Análisis y Reportes
- Métricas de rendimiento
- Análisis de tendencias
- Reportes automáticos
- Dashboard ejecutivo

### API Endpoints Principales

#### Autenticación
```http
POST /api/v1/auth/login
POST /api/v1/auth/register
```

#### Usuarios
```http
GET /api/v1/grinding-peru/users
POST /api/v1/grinding-peru/users
```

#### Equipos
```http
GET /api/v1/equipment
POST /api/v1/grinding-peru/equipment
```

#### Incidencias
```http
GET /api/v1/incidents
POST /api/v1/incidents
PUT /api/v1/incidents/{id}
```

#### Predicciones
```http
POST /api/v1/predictions/failure
POST /api/v1/predictions/anomaly-detection
```

#### Recomendaciones
```http
POST /api/v1/technicians/recommendations
```

### Credenciales de Prueba
```
Administrador:
- Usuario: admin
- Contraseña: admin123

Supervisor:
- Usuario: supervisor1
- Contraseña: admin123

Técnico:
- Usuario: tecnico1
- Contraseña: admin123
```

### Tecnologías Utilizadas
- **Backend**: FastAPI + Python 3.9+
- **Base de Datos**: Supabase (PostgreSQL)
- **IA/ML**: OpenAI GPT-4, Scikit-learn
- **RAG**: LangChain, ChromaDB
- **Autenticación**: JWT, Bcrypt

### Soporte
Para soporte técnico, contactar al equipo de desarrollo.
EOF

print_status "Documentación creada"

# 11. Mensaje final
echo ""
echo "🎉 CONFIGURACIÓN COMPLETADA EXITOSAMENTE"
echo "=========================================="
print_status "Sistema configurado para GitHub Codespaces"
print_status "Todas las dependencias instaladas"
print_status "Variables de entorno configuradas"
print_status "Estructura del proyecto verificada"
echo ""
print_info "Próximos pasos:"
echo "1. Ejecutar: ./start_system.sh"
echo "2. Acceder a: http://localhost:3000"
echo "3. Documentación: http://localhost:3000/docs"
echo "4. Probar endpoints con Postman o curl"
echo ""
print_info "Para más información, consulta: CODESPACE_README.md"
echo ""
print_status "¡Sistema listo para usar en GitHub Codespaces! 🚀"
