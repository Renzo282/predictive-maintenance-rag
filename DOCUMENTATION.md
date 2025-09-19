# Documentación del Agente Inteligente de Mantenimiento Predictivo con RAG

## Descripción General

Este sistema implementa un agente inteligente basado en RAG (Retrieval-Augmented Generation) para mantenimiento predictivo, utilizando Supabase como base de datos y GitHub para versionado. El sistema puede analizar datos de sensores, generar predicciones precisas y enviar notificaciones automáticas.

## Arquitectura del Sistema

### Componentes Principales

1. **RAG Agent** (`app/services/rag_agent.py`)
   - Análisis de patrones en datos históricos
   - Generación de predicciones usando embeddings
   - Base de conocimiento vectorial con ChromaDB

2. **Modelos de ML** (`app/services/ml_models.py`)
   - Detección de anomalías con Isolation Forest
   - Predicción de fallas con Random Forest
   - Preprocesamiento y escalado de datos

3. **Sistema de Notificaciones** (`app/services/notifications.py`)
   - Alertas por email
   - Notificaciones de Slack
   - Webhooks personalizados

4. **Monitoreo Continuo** (`app/services/monitoring.py`)
   - Análisis en tiempo real
   - Actualización automática de modelos
   - Procesamiento de alertas

## Configuración del Proyecto

### 1. Instalación

```bash
# Clonar el repositorio
git clone <repository-url>
cd predictive-maintenance-rag

# Ejecutar script de instalación
./install.sh

# O instalar manualmente
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuración de Variables de Entorno

Crear archivo `.env` con las siguientes variables:

```env
# Supabase Configuration
SUPABASE_URL=https://bcdfjbnxetnhmfxlofvc.supabase.co
SUPABASE_KEY=tu_clave_anon_key
SUPABASE_SERVICE_KEY=tu_clave_service_key

# OpenAI Configuration
OPENAI_API_KEY=tu_clave_openai

# Database Configuration
DATABASE_URL=postgresql://postgres:password@db.bcdfjbnxetnhmfxlofvc.supabase.co:5432/postgres

# Notification Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu_email@gmail.com
SMTP_PASSWORD=tu_app_password

# Security
SECRET_KEY=tu_clave_secreta_muy_segura
```

### 3. Inicialización de la Base de Datos

```bash
python scripts/init_database.py
```

## Estructura de la Base de Datos

### Tablas Principales

1. **equipment**
   - `id`: UUID (Primary Key)
   - `name`: Nombre del equipo
   - `type`: Tipo de equipo (motor, bomba, compresor, etc.)
   - `location`: Ubicación del equipo
   - `status`: Estado del equipo (active, inactive, maintenance)

2. **sensor_data**
   - `id`: UUID (Primary Key)
   - `equipment_id`: ID del equipo (Foreign Key)
   - `timestamp`: Marca de tiempo
   - `temperature`: Temperatura
   - `vibration`: Vibración
   - `pressure`: Presión
   - `humidity`: Humedad
   - `voltage`: Voltaje
   - `current`: Corriente

3. **maintenance_records**
   - `id`: UUID (Primary Key)
   - `equipment_id`: ID del equipo
   - `maintenance_type`: Tipo de mantenimiento
   - `description`: Descripción
   - `performed_at`: Fecha de realización
   - `technician`: Técnico responsable

4. **predictions**
   - `id`: UUID (Primary Key)
   - `equipment_id`: ID del equipo
   - `prediction_type`: Tipo de predicción
   - `confidence_score`: Puntuación de confianza
   - `predicted_date`: Fecha predicha

5. **alerts**
   - `id`: UUID (Primary Key)
   - `equipment_id`: ID del equipo
   - `alert_type`: Tipo de alerta
   - `severity`: Severidad (low, medium, high, critical)
   - `message`: Mensaje de la alerta
   - `is_resolved`: Estado de resolución

## API Endpoints

### Endpoints Principales

#### 1. Health Check
```http
GET /api/v1/health
```

#### 2. Ingestión de Datos
```http
POST /api/v1/data/ingest
Content-Type: application/json

{
  "equipment_id": "uuid",
  "timestamp": "2024-01-15T10:30:00Z",
  "temperature": 75.5,
  "vibration": 2.3,
  "pressure": 5.2,
  "humidity": 55.0,
  "voltage": 220.0,
  "current": 10.5
}
```

#### 3. Análisis de Equipos
```http
GET /api/v1/equipment/{equipment_id}/analysis?days=30
```

#### 4. Predicciones RAG
```http
POST /api/v1/equipment/{equipment_id}/predict
Content-Type: application/json

{
  "query": "¿Cuál es el estado de salud de este equipo?"
}
```

#### 5. Crear Alertas
```http
POST /api/v1/alerts
Content-Type: application/json

{
  "equipment_id": "uuid",
  "alert_type": "maintenance_required",
  "severity": "medium",
  "message": "Equipo requiere mantenimiento programado",
  "recommendations": ["Revisar componentes", "Programar inspección"]
}
```

#### 6. Rendimiento de Modelos
```http
GET /api/v1/models/performance
```

#### 7. Reentrenar Modelos
```http
POST /api/v1/models/retrain
```

## Uso del Sistema

### 1. Iniciar la Aplicación

```bash
# Activar entorno virtual
source venv/bin/activate

# Iniciar servidor
python main.py
```

La aplicación estará disponible en `http://localhost:3000`

### 2. Probar la API

```bash
python scripts/test_api.py
```

### 3. Monitoreo Continuo

El sistema incluye monitoreo automático que:
- Detecta anomalías cada minuto
- Genera predicciones cada 5 minutos
- Actualiza modelos cada hora
- Actualiza base de conocimiento RAG cada hora

## Características de Seguridad

### 1. Autenticación y Autorización
- Tokens JWT para autenticación
- Validación de entrada en todos los endpoints
- Sanitización de datos de usuario

### 2. Protección de Datos
- Encriptación de credenciales sensibles
- Variables de entorno para configuración
- Validación de esquemas con Pydantic

### 3. Logging y Monitoreo
- Logs estructurados con diferentes niveles
- Métricas de rendimiento
- Alertas de seguridad

## Configuración de Notificaciones

### Email
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu_email@gmail.com
SMTP_PASSWORD=tu_app_password
```

### Slack
```env
SLACK_BOT_TOKEN=xoxb-tu-token
SLACK_CHANNEL=#maintenance-alerts
```

## Despliegue

### 1. Docker (Recomendado)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 3000

CMD ["python", "main.py"]
```

### 2. Heroku

```bash
# Crear Procfile
echo "web: python main.py" > Procfile

# Desplegar
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### 3. AWS/GCP/Azure

- Usar contenedores Docker
- Configurar load balancer
- Configurar base de datos gestionada
- Configurar monitoreo y alertas

## Mantenimiento y Actualizaciones

### 1. Actualizar Modelos
```bash
curl -X POST http://localhost:3000/api/v1/models/retrain
```

### 2. Actualizar Base de Conocimiento RAG
```bash
curl -X POST http://localhost:3000/api/v1/rag/update
```

### 3. Monitorear Rendimiento
```bash
curl http://localhost:3000/api/v1/models/performance
```

## Troubleshooting

### Problemas Comunes

1. **Error de conexión a Supabase**
   - Verificar credenciales en `.env`
   - Verificar conectividad de red
   - Verificar configuración de RLS

2. **Error de OpenAI API**
   - Verificar clave API válida
   - Verificar límites de uso
   - Verificar conectividad

3. **Modelos no entrenan**
   - Verificar datos suficientes en la base de datos
   - Verificar permisos de escritura en directorio `models/`
   - Revisar logs para errores específicos

### Logs

Los logs se almacenan en:
- `logs/application.log` - Logs generales
- `logs/errors.log` - Logs de errores
- `logs/performance.log` - Métricas de rendimiento

## Contribución

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## Soporte

Para soporte técnico o preguntas:
- Crear issue en GitHub
- Contactar al equipo de desarrollo
- Revisar documentación y FAQ

## Roadmap

### Versión 1.1
- [ ] Dashboard web interactivo
- [ ] Integración con más sistemas de notificación
- [ ] Análisis de tendencias avanzado

### Versión 1.2
- [ ] Machine Learning con Deep Learning
- [ ] Integración con IoT devices
- [ ] Análisis de costos de mantenimiento

### Versión 2.0
- [ ] Multi-tenant architecture
- [ ] API GraphQL
- [ ] Mobile app
