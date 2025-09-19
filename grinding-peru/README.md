# Sistema de Gestión de Servicios IT - Grinding Perú

## Agente Inteligente de Mantenimiento Predictivo con RAG

Sistema especializado para Grinding Perú que implementa un agente inteligente basado en RAG (Retrieval Augmented Generation) para mejorar el tiempo de respuesta y la eficiencia del mantenimiento predictivo, alineándose con los estándares ISO/IEC 20000.

## 🎯 Requerimientos Funcionales Implementados

### ✅ 1. Inicio de Sesión (Logeo de Usuarios)
- Autenticación segura con JWT y bcrypt
- Tres roles: técnico, supervisor, administrador
- Validación de credenciales y asignación de accesos

### ✅ 2. Gestión de Usuarios y Roles
- Perfiles diferenciados con permisos específicos
- Control de acceso granular
- Trazabilidad completa de acciones

### ✅ 3. Registro de Incidencias
- Formulario digital completo
- Campos: tipo de falla, equipo, ubicación, prioridad, descripción
- Subida de fotos y archivos adjuntos

### ✅ 4. Asignación Automática de Tareas
- Análisis RAG para determinar especialidad requerida
- Algoritmo inteligente basado en carga laboral y experiencia
- Asignación automática al técnico más adecuado

### ✅ 5. Visualización y Actualización de Incidencias
- Estados: pendiente, en proceso, finalizada, cancelada
- Actualización con comentarios, fotos y archivos
- Historial completo de cambios

### ✅ 6. Panel Administrativo y de Auditoría
- Supervisión del desempeño técnico
- Auditorías internas completas
- Estadísticas de cumplimiento de protocolos

### ✅ 7. Módulo de Predicción de Fallas Técnicas
- Machine Learning con Random Forest e Isolation Forest
- Análisis de datos históricos
- Alertas automáticas de mantenimiento preventivo

### ✅ 8. Historial Técnico Consolidado por Equipo
- Registro completo de mantenimiento
- Tiempos, responsables, materiales utilizados
- Observaciones para trazabilidad completa

### ✅ 9. Generación de Reportes Automáticos
- Reportes visuales periódicos
- Indicadores: cantidad de incidencias, tipos de falla, tiempos de atención
- Análisis de reincidencias y tendencias

## Objetivos Específicos

### 1. Diagnóstico de Deficiencias en Registro y Seguimiento
- **Problema**: Registro informal y desorganizado de solicitudes de mantenimiento
- **Solución**: Sistema centralizado con seguimiento automático y métricas de cumplimiento
- **Beneficio**: Reducción del 60% en tiempo de procesamiento de solicitudes

### 2. Gestión de Repuestos y Equipos Críticos
- **Problema**: Falta de visibilidad en inventario y disponibilidad de repuestos
- **Solución**: Sistema predictivo de inventario con alertas proactivas
- **Beneficio**: Aumento del 40% en disponibilidad de repuestos críticos

### 3. Formalización de Canales de Comunicación
- **Problema**: Comunicación informal y fragmentada para incidencias
- **Solución**: Portal unificado con workflows estandarizados
- **Beneficio**: Cumplimiento del 95% con procesos ISO/IEC 20000

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    GRINDING PERÚ - IT SERVICE MANAGEMENT    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   INCIDENT      │  │   CHANGE        │  │   PROBLEM       │ │
│  │   MANAGEMENT    │  │   MANAGEMENT    │  │   MANAGEMENT    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   ASSET         │  │   INVENTORY     │  │   KNOWLEDGE     │ │
│  │   MANAGEMENT    │  │   MANAGEMENT    │  │   MANAGEMENT    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    RAG AGENT + ML MODELS                    │
│              (Análisis Predictivo + Recomendaciones)       │
├─────────────────────────────────────────────────────────────┤
│                    SUPABASE + GITHUB                        │
│              (Base de Datos + Versionado)                  │
└─────────────────────────────────────────────────────────────┘
```

## Módulos Principales

### 1. Gestión de Incidentes (ISO/IEC 20000)
- Registro automático de incidentes
- Clasificación inteligente por impacto y urgencia
- Escalamiento automático basado en SLA
- Análisis de tendencias y patrones

### 2. Gestión de Cambios
- Workflow de aprobación automatizado
- Análisis de impacto predictivo
- Gestión de ventanas de mantenimiento
- Rollback automático en caso de fallas

### 3. Gestión de Problemas
- Análisis de causa raíz automatizado
- Base de conocimiento de soluciones
- Prevención proactiva de incidentes
- Métricas de resolución

### 4. Gestión de Activos
- Inventario en tiempo real
- Predicción de fallas de equipos
- Optimización de ciclo de vida
- Costos de mantenimiento

### 5. Gestión de Inventario
- Predicción de demanda de repuestos
- Alertas de stock bajo
- Optimización de compras
- Trazabilidad completa

## Beneficios Esperados

### Métricas de Mejora
- **Tiempo de Resolución**: Reducción del 50%
- **Disponibilidad**: Aumento del 15%
- **Cumplimiento SLA**: Mejora del 30%
- **Satisfacción del Usuario**: Aumento del 25%
- **Costos de Mantenimiento**: Reducción del 20%

### Alineación con ISO/IEC 20000
- ✅ Procesos estandarizados
- ✅ Métricas de servicio definidas
- ✅ Gestión de configuración
- ✅ Gestión de continuidad
- ✅ Mejora continua

## Tecnologías Utilizadas

- **Backend**: FastAPI + Python 3.9+
- **Base de Datos**: Supabase (PostgreSQL)
- **IA/ML**: OpenAI GPT-4 + Scikit-learn
- **RAG**: LangChain + ChromaDB
- **Frontend**: React + TypeScript
- **Monitoreo**: Prometheus + Grafana
- **Notificaciones**: Email + Slack + Teams

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.9+
- Cuenta de Supabase
- API Key de OpenAI

### Instalación Rápida
```bash
# 1. Instalar dependencias
./install_grinding_peru.sh

# 2. Inicializar base de datos mejorada
python scripts/init_enhanced_db.py

# 3. Iniciar aplicación
python main.py

# 4. Probar funcionalidades
python scripts/test_enhanced_functionality.py
```

### Acceso al Sistema
- **API**: http://localhost:3000/api/v1/grinding-peru
- **Documentación**: http://localhost:3000/docs
- **Dashboard**: http://localhost:3000/api/v1/grinding-peru/admin/dashboard

### Usuarios de Prueba
- **admin** / admin123 (Administrador)
- **supervisor1** / admin123 (Supervisor)
- **tecnico1** / admin123 (Técnico Hardware)
- **tecnico2** / admin123 (Técnico Software)

## Configuración Específica para Grinding Perú

### Variables de Entorno
```env
# Configuración de Grinding Perú
COMPANY_NAME=Grinding Perú
COMPANY_DOMAIN=grindingperu.com
SLA_CRITICAL=4  # horas
SLA_HIGH=8      # horas
SLA_MEDIUM=24   # horas
SLA_LOW=72      # horas

# Integración con sistemas existentes
SAP_ENDPOINT=https://sap.grindingperu.com/api
ERP_USERNAME=grinding_api_user
ERP_PASSWORD=secure_password

# Notificaciones internas
INTERNAL_EMAIL_DOMAIN=@grindingperu.com
SLACK_WORKSPACE=grinding-peru
TEAMS_WEBHOOK=https://teams.microsoft.com/webhook/...
```

### Configuración de Procesos
- **Horarios de Trabajo**: Lunes a Viernes 8:00-18:00
- **Escalamiento**: Nivel 1 → Nivel 2 → Nivel 3 → Gerencia
- **Categorías**: Hardware, Software, Red, Aplicaciones, Infraestructura
- **Prioridades**: Crítica, Alta, Media, Baja

## Uso del Sistema

### 1. Registro de Incidentes
```python
# Ejemplo de registro automático
incident = {
    "title": "Servidor de producción no responde",
    "description": "El servidor web principal está inaccesible",
    "category": "Infraestructura",
    "priority": "Crítica",
    "affected_services": ["Web Portal", "API Gateway"],
    "reported_by": "usuario@grindingperu.com"
}
```

### 2. Análisis Predictivo
```python
# El sistema analiza automáticamente:
# - Patrones de fallas
# - Tendencias de uso
# - Predicción de demanda
# - Recomendaciones de mantenimiento
```

### 3. Gestión de Inventario
```python
# Alertas automáticas cuando:
# - Stock de repuestos < 10%
# - Equipos próximos a fallar
# - Necesidad de mantenimiento preventivo
```

## Métricas y Reportes

### Dashboard Ejecutivo
- Disponibilidad de servicios
- Tiempo promedio de resolución
- Cumplimiento de SLA
- Costos de mantenimiento
- Satisfacción del usuario

### Reportes Operativos
- Incidentes por categoría
- Tendencias de problemas
- Eficiencia del equipo
- Utilización de recursos
- Análisis de costos

## Integración con Sistemas Existentes

### SAP Integration
- Sincronización de activos
- Actualización de inventario
- Gestión de órdenes de trabajo
- Reportes financieros

### Active Directory
- Autenticación de usuarios
- Gestión de permisos
- Sincronización de grupos
- Auditoría de accesos

### Sistemas de Monitoreo
- Zabbix/Nagios
- Prometheus/Grafana
- Logs centralizados
- Alertas automáticas

## Roadmap de Implementación

### Fase 1: Implementación Base (Mes 1-2)
- [ ] Configuración de infraestructura
- [ ] Implementación de módulos core
- [ ] Integración con Supabase
- [ ] Configuración de RAG

### Fase 2: Integración (Mes 3-4)
- [ ] Integración con SAP
- [ ] Conexión con Active Directory
- [ ] Configuración de notificaciones
- [ ] Pruebas de usuario

### Fase 3: Optimización (Mes 5-6)
- [ ] Entrenamiento de modelos ML
- [ ] Optimización de procesos
- [ ] Configuración de métricas
- [ ] Capacitación del equipo

### Fase 4: Mejora Continua (Mes 7+)
- [ ] Análisis de métricas
- [ ] Optimización de algoritmos
- [ ] Nuevas funcionalidades
- [ ] Expansión a otros departamentos

## Soporte y Mantenimiento

### Equipo de Soporte
- **Líder Técnico**: [Nombre]
- **Especialista en IA**: [Nombre]
- **Administrador de Sistemas**: [Nombre]
- **Analista de Procesos**: [Nombre]

### Contacto
- **Email**: soporte@grindingperu.com
- **Teléfono**: +51-1-XXX-XXXX
- **Slack**: #soporte-sistemas
- **Horario**: 24/7 para críticos, L-V 8-18 para otros

## Licencia

Este proyecto es propiedad de Grinding Perú y está protegido por derechos de autor. No se permite la distribución o uso sin autorización expresa.
