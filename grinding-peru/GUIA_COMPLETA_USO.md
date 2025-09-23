# 🚀 GUÍA COMPLETA DE USO DEL SISTEMA
## Sistema de Soporte a la Decisión para Mantenimiento Predictivo
### Grinding Perú - Arequipa, 2025

---

## 📋 **ÍNDICE**

1. [Configuración Inicial](#configuración-inicial)
2. [Funcionalidades del Sistema](#funcionalidades-del-sistema)
3. [Guía Paso a Paso](#guía-paso-a-paso)
4. [Casos de Uso Prácticos](#casos-de-uso-prácticos)
5. [API Endpoints](#api-endpoints)
6. [Troubleshooting](#troubleshooting)

---

## 🔧 **CONFIGURACIÓN INICIAL**

### **Paso 1: Verificar Requisitos**
```bash
# Verificar Python
py --version  # Debe ser 3.9+

# Verificar pip
py -m pip --version
```

### **Paso 2: Instalar Dependencias**
```bash
# Navegar al directorio del proyecto
cd predictive-maintenance-rag\grinding-peru

# Instalar dependencias
py -m pip install -r requirements.txt
```

### **Paso 3: Configurar Variables de Entorno**
```bash
# Verificar archivo .env
Get-Content .env
```

### **Paso 4: Inicializar Base de Datos**
```bash
# Ejecutar script de configuración completa
py scripts\setup_complete_system.py
```

### **Paso 5: Iniciar Sistema**
```bash
# Iniciar servidor
py main.py
```

---

## 🎯 **FUNCIONALIDADES DEL SISTEMA**

### **1. 🤖 Agente Inteligente con RAG**
- **Análisis contextual** de incidencias
- **Recomendaciones inteligentes** basadas en conocimiento técnico
- **Predicción de fallas** usando machine learning
- **Detección de anomalías** en tiempo real

### **2. 👥 Gestión de Usuarios y Roles**
- **Administrador**: Control total del sistema
- **Supervisor**: Gestión de técnicos y incidencias
- **Técnico**: Resolución de incidencias asignadas

### **3. 🔧 Recomendación Automática de Técnicos**
- **Asignación inteligente** basada en especialidad
- **Análisis de carga de trabajo** en tiempo real
- **Recomendación de equipos** para incidencias complejas
- **Optimización de recursos** humanos

### **4. 📊 Predicción y Análisis**
- **Predicción de fallas** con probabilidades
- **Análisis de tendencias** históricas
- **Alertas proactivas** de mantenimiento
- **Cronogramas personalizados** por equipo

### **5. 📋 Gestión Inteligente de Incidencias**
- **Registro automático** con análisis
- **Clasificación inteligente** de prioridades
- **Escalamiento automático** según criticidad
- **Seguimiento completo** del ciclo de vida

---

## 📖 **GUÍA PASO A PASO**

### **🔐 PASO 1: INICIO DE SESIÓN**

#### **1.1 Acceder al Sistema**
```bash
# El sistema estará disponible en:
http://localhost:3000
```

#### **1.2 Credenciales de Prueba**
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

#### **1.3 Endpoint de Login**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
    "username": "admin",
    "password": "admin123"
}
```

### **👥 PASO 2: GESTIÓN DE USUARIOS**

#### **2.1 Crear Nuevo Técnico**
```http
POST /api/v1/grinding-peru/users
Authorization: Bearer {token}
Content-Type: application/json

{
    "username": "nuevo_tecnico",
    "email": "tecnico@grindingperu.com",
    "password": "password123",
    "name": "Nuevo Técnico",
    "role": "technician",
    "specialty": "mecanico",
    "experience_years": 3,
    "location": "Arequipa",
    "skill_level": "intermediate",
    "certifications": ["Mantenimiento Industrial"],
    "preferred_equipment_types": ["motor", "bomba"]
}
```

#### **2.2 Listar Usuarios**
```http
GET /api/v1/grinding-peru/users
Authorization: Bearer {token}
```

### **🔧 PASO 3: GESTIÓN DE EQUIPOS**

#### **3.1 Registrar Nuevo Equipo**
```http
POST /api/v1/grinding-peru/equipment
Authorization: Bearer {token}
Content-Type: application/json

{
    "name": "Motor Principal Planta 2",
    "type": "motor_electrico",
    "model": "ABB M2BA 160",
    "serial_number": "MOT002",
    "location": "Planta Secundaria",
    "criticality": "high",
    "age_months": 12,
    "operating_hours": 5000,
    "maintenance_frequency": 30
}
```

#### **3.2 Listar Equipos**
```http
GET /api/v1/grinding-peru/equipment
Authorization: Bearer {token}
```

### **📋 PASO 4: GESTIÓN DE INCIDENCIAS**

#### **4.1 Crear Nueva Incidencia**
```http
POST /api/v1/incidents
Authorization: Bearer {token}
Content-Type: application/json

{
    "title": "Vibración excesiva en Motor Principal",
    "description": "Se detectó vibración anormal en el motor principal de la planta 1. El nivel de vibración supera los 4.5 mm/s, lo cual está por encima del límite permitido de 2.8 mm/s.",
    "equipment_id": "1",
    "location": "Planta Principal",
    "equipment_criticality": "critical",
    "production_impact": "high",
    "attachments": ["vibracion_medicion.pdf"],
    "auto_assign": true
}
```

#### **4.2 Respuesta del Sistema**
```json
{
    "success": true,
    "message": "Incidencia creada exitosamente",
    "data": {
        "incident": {
            "id": "uuid-generado",
            "title": "Vibración excesiva en Motor Principal",
            "priority": "critical",
            "status": "pending",
            "assigned_technician": "3",
            "estimated_duration": 180
        },
        "analysis": {
            "suggested_tags": ["mecanica", "vibracion", "critico"],
            "risk_level": "high",
            "complexity": "medium",
            "required_specialties": ["mecanico"]
        },
        "assignment": {
            "success": true,
            "technician_id": "3",
            "technician_name": "Juan Pérez",
            "score": 0.85,
            "reasons": [
                "Especialidad en mecánica ideal para este tipo de falla",
                "Experiencia sólida de 5 años",
                "Disponibilidad inmediata"
            ]
        },
        "recommendations": [
            {
                "type": "tools",
                "suggestion": "Herramientas de medición de vibraciones",
                "priority": "high"
            },
            {
                "type": "safety",
                "suggestion": "Procedimiento de seguridad especial requerido",
                "priority": "high"
            }
        ]
    }
}
```

### **🤖 PASO 5: PREDICCIÓN DE FALLAS**

#### **5.1 Analizar Equipo con Datos de Sensores**
```http
POST /api/v1/predictions/failure
Authorization: Bearer {token}
Content-Type: application/json

{
    "equipment_id": "1",
    "sensor_data": [
        {
            "sensor_type": "temperature",
            "value": 85.5,
            "unit": "°C",
            "timestamp": "2025-01-15T10:30:00Z"
        },
        {
            "sensor_type": "vibration",
            "value": 4.2,
            "unit": "mm/s",
            "timestamp": "2025-01-15T10:30:00Z"
        },
        {
            "sensor_type": "current",
            "value": 18.5,
            "unit": "A",
            "timestamp": "2025-01-15T10:30:00Z"
        }
    ],
    "analysis_type": "comprehensive"
}
```

#### **5.2 Respuesta de Predicción**
```json
{
    "success": true,
    "data": {
        "failure_probability": 0.78,
        "anomaly_score": 0.85,
        "criticality": "critical",
        "recommendations": [
            {
                "type": "preventive",
                "action": "Verificar lubricación",
                "priority": "high",
                "technician_type": "mecanico"
            },
            {
                "type": "measurement",
                "action": "Medir vibraciones",
                "priority": "high",
                "technician_type": "mecanico"
            }
        ],
        "predicted_failure_type": "sobrecalentamiento",
        "time_to_failure": 48,
        "confidence": 0.82,
        "timestamp": "2025-01-15T10:30:00Z"
    }
}
```

### **👥 PASO 6: RECOMENDACIÓN DE TÉCNICOS**

#### **6.1 Obtener Recomendaciones**
```http
POST /api/v1/technicians/recommendations
Authorization: Bearer {token}
Content-Type: application/json

{
    "incident_data": {
        "equipment_type": "motor_electrico",
        "failure_type": "vibracion_excesiva",
        "location": "Planta Principal",
        "priority": "critical"
    },
    "limit": 5
}
```

#### **6.2 Respuesta de Recomendaciones**
```json
{
    "success": true,
    "data": [
        {
            "technician": {
                "id": "3",
                "name": "Juan Pérez",
                "specialty": "mecanico",
                "experience_years": 5,
                "skill_level": "senior",
                "current_workload": 2
            },
            "score": 0.85,
            "reasons": [
                "Especialidad en mecánica ideal para este tipo de falla",
                "Experiencia sólida de 5 años",
                "Disponibilidad inmediata"
            ]
        },
        {
            "technician": {
                "id": "4",
                "name": "María González",
                "specialty": "electrico",
                "experience_years": 4,
                "skill_level": "intermediate",
                "current_workload": 1
            },
            "score": 0.72,
            "reasons": [
                "Especialidad complementaria en sistemas eléctricos",
                "Experiencia en motores eléctricos",
                "Disponibilidad alta"
            ]
        }
    ],
    "count": 2
}
```

### **📊 PASO 7: ANÁLISIS Y REPORTES**

#### **7.1 Obtener Análisis de Incidencias**
```http
GET /api/v1/analytics/incidents?days=30
Authorization: Bearer {token}
```

#### **7.2 Respuesta de Análisis**
```json
{
    "success": true,
    "data": {
        "period_days": 30,
        "total_incidents": 45,
        "completed_incidents": 42,
        "critical_incidents": 8,
        "completion_rate": 93.33,
        "avg_resolution_time": 145.5,
        "recent_incidents": 12
    }
}
```

#### **7.3 Obtener Análisis de Rendimiento**
```http
GET /api/v1/analytics/performance?period=month
Authorization: Bearer {token}
```

---

## 🎯 **CASOS DE USO PRÁCTICOS**

### **CASO 1: Incidencia Crítica de Motor**

#### **Escenario:**
- Motor principal con vibración excesiva
- Prioridad crítica
- Impacto en producción

#### **Flujo del Sistema:**
1. **Registro automático** de la incidencia
2. **Análisis inteligente** determina criticidad
3. **Recomendación automática** del técnico más adecuado
4. **Asignación inmediata** con notificaciones
5. **Seguimiento en tiempo real** del progreso

#### **Resultado:**
- Técnico asignado en < 2 minutos
- Recomendaciones específicas de herramientas
- Procedimientos de seguridad automáticos
- Tiempo de resolución optimizado

### **CASO 2: Predicción de Falla**

#### **Escenario:**
- Análisis de datos de sensores
- Detección de anomalías
- Predicción de falla inminente

#### **Flujo del Sistema:**
1. **Recepción de datos** de sensores
2. **Análisis ML** de patrones
3. **Detección de anomalías** automática
4. **Predicción de falla** con probabilidad
5. **Generación de alertas** proactivas

#### **Resultado:**
- Alerta temprana de falla
- Recomendaciones de mantenimiento preventivo
- Optimización de recursos
- Reducción de tiempo de inactividad

### **CASO 3: Gestión de Equipos**

#### **Escenario:**
- Nuevo equipo en planta
- Configuración de mantenimiento
- Cronograma personalizado

#### **Flujo del Sistema:**
1. **Registro del equipo** con especificaciones
2. **Análisis de criticidad** automático
3. **Generación de cronograma** personalizado
4. **Asignación de responsabilidades**
5. **Configuración de alertas**

#### **Resultado:**
- Cronograma optimizado por equipo
- Mantenimiento preventivo eficiente
- Reducción de costos operativos
- Mejora en disponibilidad

---

## 🔗 **API ENDPOINTS COMPLETOS**

### **🔐 Autenticación**
```http
POST /api/v1/auth/login          # Iniciar sesión
POST /api/v1/auth/register       # Registrar usuario
POST /api/v1/auth/refresh        # Renovar token
```

### **👥 Usuarios**
```http
GET    /api/v1/grinding-peru/users           # Listar usuarios
POST   /api/v1/grinding-peru/users           # Crear usuario
GET    /api/v1/grinding-peru/users/{id}       # Obtener usuario
PUT    /api/v1/grinding-peru/users/{id}       # Actualizar usuario
DELETE /api/v1/grinding-peru/users/{id}     # Eliminar usuario
```

### **🔧 Equipos**
```http
GET    /api/v1/equipment                     # Listar equipos
GET    /api/v1/equipment/{id}                 # Obtener equipo
POST   /api/v1/grinding-peru/equipment      # Crear equipo
PUT    /api/v1/grinding-peru/equipment/{id}  # Actualizar equipo
```

### **📋 Incidencias**
```http
GET    /api/v1/incidents                     # Listar incidencias
POST   /api/v1/incidents                      # Crear incidencia
GET    /api/v1/incidents/{id}                # Obtener incidencia
PUT    /api/v1/incidents/{id}                # Actualizar incidencia
```

### **🤖 Predicciones**
```http
POST /api/v1/predictions/failure             # Predecir falla
POST /api/v1/predictions/anomaly-detection   # Detectar anomalías
GET  /api/v1/predictions/maintenance-schedule/{id} # Cronograma
```

### **👥 Recomendaciones de Técnicos**
```http
POST /api/v1/technicians/recommendations     # Recomendar técnicos
POST /api/v1/technicians/team-recommendations # Recomendar equipos
GET  /api/v1/technicians/{id}/workload       # Carga de trabajo
```

### **📊 Análisis**
```http
GET /api/v1/analytics/incidents              # Análisis de incidencias
GET /api/v1/analytics/performance            # Análisis de rendimiento
```

### **🏥 Salud del Sistema**
```http
GET /api/v1/health                           # Estado del sistema
GET /system/status                          # Estado completo
```

---

## 🔧 **TROUBLESHOOTING**

### **Problema 1: Error de Conexión a Base de Datos**
```bash
# Verificar variables de entorno
Get-Content .env

# Verificar conexión
py -c "from app.core.database import get_db_connection; print('Conexión OK')"
```

### **Problema 2: Dependencias Faltantes**
```bash
# Reinstalar dependencias
py -m pip install -r requirements.txt --force-reinstall
```

### **Problema 3: Puerto en Uso**
```bash
# Cambiar puerto en .env
echo "PORT=3001" >> .env
```

### **Problema 4: Error de OpenAI API**
```bash
# Verificar API key
echo $env:OPENAI_API_KEY
```

### **Problema 5: Base de Datos No Inicializada**
```bash
# Ejecutar script de inicialización
py scripts\setup_complete_system.py
```

---

## 📞 **SOPORTE Y CONTACTO**

### **Información del Sistema**
- **Empresa**: Grinding Perú
- **Ubicación**: Arequipa, Perú
- **Versión**: 1.0.0
- **Año**: 2025

### **Características Técnicas**
- **Backend**: FastAPI + Python 3.9+
- **Base de Datos**: Supabase (PostgreSQL)
- **IA/ML**: OpenAI GPT-4, Scikit-learn
- **RAG**: LangChain, ChromaDB
- **Autenticación**: JWT, Bcrypt

### **Documentación Adicional**
- **API Docs**: http://localhost:3000/docs
- **ReDoc**: http://localhost:3000/redoc
- **Health Check**: http://localhost:3000/api/v1/health

---

## 🎉 **¡SISTEMA LISTO PARA USAR!**

El sistema está completamente configurado y listo para optimizar el mantenimiento predictivo en Grinding Perú. Todas las funcionalidades están operativas y el agente inteligente con RAG está preparado para brindar soporte a la decisión en tiempo real.

**¡Bienvenido al futuro del mantenimiento predictivo inteligente!** 🚀
