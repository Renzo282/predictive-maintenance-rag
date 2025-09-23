# 🚀 Guía de Uso en GitHub Codespaces
## Sistema de Mantenimiento Predictivo - Grinding Perú

## 🎯 Inicio Rápido

### **1. Abrir en Codespaces**
- Hacer clic en "Code" > "Codespaces" > "Create codespace"
- Esperar a que se configure el entorno

### **2. Configuración Automática**
```bash
# Ejecutar script de configuración
./scripts/codespace_setup.sh
```

### **3. Iniciar Sistema**
```bash
# Iniciar el sistema completo
./start_system.sh
```

### **4. Acceder al Sistema**
- **URL Principal**: http://localhost:3000
- **Documentación API**: http://localhost:3000/docs
- **ReDoc**: http://localhost:3000/redoc

## 🔑 Credenciales de Prueba

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

## 📋 Funcionalidades Implementadas

### **🔐 Autenticación y Usuarios**
- Login seguro con JWT
- Gestión de roles (Administrador, Supervisor, Técnico)
- Registro de nuevos usuarios
- Perfiles diferenciados

### **🔧 Gestión de Equipos**
- Registro de equipos industriales
- Clasificación por criticidad
- Historial de mantenimiento
- Datos de sensores en tiempo real

### **📋 Gestión de Incidencias**
- Registro inteligente de incidencias
- Clasificación automática de prioridades
- Asignación automática de técnicos
- Seguimiento en tiempo real
- Escalamiento automático

### **🤖 Predicción Inteligente**
- Predicción de fallas con ML
- Detección de anomalías
- Análisis de tendencias
- Alertas proactivas
- Cronogramas personalizados

### **👥 Recomendación de Técnicos**
- Asignación inteligente basada en especialidad
- Análisis de carga de trabajo
- Recomendación de equipos
- Optimización de recursos

### **📊 Análisis y Reportes**
- Métricas de rendimiento
- Análisis de tendencias
- Reportes automáticos
- Dashboard ejecutivo

## 🛠️ API Endpoints Principales

### **Autenticación**
```http
POST /api/v1/auth/login
POST /api/v1/auth/register
```

### **Usuarios**
```http
GET /api/v1/grinding-peru/users
POST /api/v1/grinding-peru/users
GET /api/v1/grinding-peru/users/{id}
PUT /api/v1/grinding-peru/users/{id}
```

### **Equipos**
```http
GET /api/v1/equipment
POST /api/v1/grinding-peru/equipment
GET /api/v1/equipment/{id}
```

### **Incidencias**
```http
GET /api/v1/incidents
POST /api/v1/incidents
GET /api/v1/incidents/{id}
PUT /api/v1/incidents/{id}
```

### **Predicciones**
```http
POST /api/v1/predictions/failure
POST /api/v1/predictions/anomaly-detection
GET /api/v1/predictions/maintenance-schedule/{id}
```

### **Recomendaciones**
```http
POST /api/v1/technicians/recommendations
POST /api/v1/technicians/team-recommendations
GET /api/v1/technicians/{id}/workload
```

### **Análisis**
```http
GET /api/v1/analytics/incidents
GET /api/v1/analytics/performance
```

## 🎯 Casos de Uso Prácticos

### **Caso 1: Incidencia Crítica de Motor**

**Escenario**: Motor principal con vibración excesiva
**Flujo del Sistema**:
1. Registro automático de la incidencia
2. Análisis inteligente determina criticidad
3. Recomendación automática del técnico más adecuado
4. Asignación inmediata con notificaciones
5. Seguimiento en tiempo real del progreso

**Resultado**: Técnico asignado en < 2 minutos con recomendaciones específicas

### **Caso 2: Predicción de Falla**

**Escenario**: Análisis de datos de sensores
**Flujo del Sistema**:
1. Recepción de datos de sensores
2. Análisis ML de patrones
3. Detección de anomalías automática
4. Predicción de falla con probabilidad
5. Generación de alertas proactivas

**Resultado**: Alerta temprana de falla con recomendaciones de mantenimiento

### **Caso 3: Gestión de Equipos**

**Escenario**: Nuevo equipo en planta
**Flujo del Sistema**:
1. Registro del equipo con especificaciones
2. Análisis de criticidad automático
3. Generación de cronograma personalizado
4. Asignación de responsabilidades
5. Configuración de alertas

**Resultado**: Cronograma optimizado por equipo con mantenimiento preventivo eficiente

## 🔧 Comandos Útiles

### **Verificar Estado del Sistema**
```bash
# Verificar que el sistema esté funcionando
curl http://localhost:3000/health
```

### **Probar Autenticación**
```bash
# Login de prueba
curl -X POST "http://localhost:3000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### **Crear Nueva Incidencia**
```bash
# Crear incidencia de prueba
curl -X POST "http://localhost:3000/api/v1/incidents" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "Vibración excesiva en Motor Principal",
    "description": "Se detectó vibración anormal en el motor principal",
    "equipment_id": "1",
    "location": "Planta Principal",
    "equipment_criticality": "critical",
    "production_impact": "high"
  }'
```

### **Obtener Recomendaciones de Técnicos**
```bash
# Obtener recomendaciones
curl -X POST "http://localhost:3000/api/v1/technicians/recommendations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "incident_data": {
      "equipment_type": "motor_electrico",
      "failure_type": "vibracion_excesiva",
      "location": "Planta Principal",
      "priority": "critical"
    }
  }'
```

## 🛠️ Tecnologías Utilizadas

- **Backend**: FastAPI + Python 3.9+
- **Base de Datos**: Supabase (PostgreSQL)
- **IA/ML**: OpenAI GPT-4, Scikit-learn
- **RAG**: LangChain, ChromaDB
- **Autenticación**: JWT, Bcrypt
- **Notificaciones**: Email, Slack, Teams
- **Monitoreo**: Prometheus + Grafana

## 📊 Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Supabase DB   │◄───┤   RAG Agent     │◄───│   ML Models     │
│   (PostgreSQL)  │    │   (Analysis)    │    │   (Predictions) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI      │    │  Notifications  │    │   Dashboard     │
│   (REST API)   │    │   (Alerts)      │    │   (Monitoring)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚨 Troubleshooting

### **Problema: Puerto en uso**
```bash
# Cambiar puerto en .env
echo "PORT=3001" >> .env
```

### **Problema: Dependencias faltantes**
```bash
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### **Problema: Base de datos no conecta**
```bash
# Verificar variables de entorno
cat .env
```

### **Problema: OpenAI API no funciona**
```bash
# Verificar API key
echo $OPENAI_API_KEY
```

## 📞 Soporte

- **Documentación**: Este archivo
- **API Docs**: http://localhost:3000/docs
- **Issues**: [GitHub Issues](https://github.com/Renzo282/predictive-maintenance-rag/issues)

## 🎉 ¡Sistema Listo!

El sistema está completamente configurado y listo para optimizar el mantenimiento predictivo en Grinding Perú. Todas las funcionalidades están operativas y el agente inteligente con RAG está preparado para brindar soporte a la decisión en tiempo real.

**¡Bienvenido al futuro del mantenimiento predictivo inteligente!** 🚀
