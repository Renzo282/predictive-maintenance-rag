# Requerimientos Funcionales - Grinding Perú

## Sistema de Gestión de Servicios IT con RAG y ML

### 1. Inicio de Sesión (Logeo de Usuarios) ✅

**Descripción**: Implementar una interfaz segura para que los usuarios inicien sesión mediante credenciales, validando su identidad y asignando accesos según su rol dentro del sistema.

**Implementación**:
- Autenticación JWT con hash de contraseñas bcrypt
- Tres roles: técnico, supervisor, administrador
- Validación de credenciales en base de datos
- Tokens con expiración configurable

**Endpoints**:
- `POST /api/v1/grinding-peru/auth/login` - Iniciar sesión
- `GET /api/v1/grinding-peru/auth/me` - Obtener usuario actual
- `POST /api/v1/grinding-peru/auth/register` - Registrar usuario (solo admin)

**Ejemplo de uso**:
```json
{
  "username": "tecnico1",
  "password": "admin123"
}
```

### 2. Gestión de Usuarios y Roles ✅

**Descripción**: Crear perfiles de acceso diferenciados (técnico, supervisor, administrador) con permisos específicos para garantizar trazabilidad y control de acciones.

**Roles Implementados**:

#### Técnico
- Ver incidencias asignadas
- Crear incidencias
- Actualizar incidencias asignadas
- Ver equipos
- Actualizar estado de equipos
- Ver historial de mantenimiento

#### Supervisor
- Todas las funciones de técnico
- Asignar incidencias
- Ver todas las incidencias
- Ver reportes
- Gestionar técnicos

#### Administrador
- Todas las funciones de supervisor
- Eliminar incidencias
- Crear/editar/eliminar equipos
- Crear registros de mantenimiento
- Gestionar usuarios
- Ver logs de auditoría
- Configuración del sistema

**Endpoints**:
- `GET /api/v1/grinding-peru/auth/users` - Listar usuarios
- `GET /api/v1/grinding-peru/auth/users/by-role/{role}` - Usuarios por rol

### 3. Registro de Incidencias ✅

**Descripción**: Permitir que cualquier usuario autorizado registre incidencias técnicas mediante un formulario digital con campos como tipo de falla, equipo involucrado, ubicación, prioridad y descripción.

**Campos del Formulario**:
- Tipo de falla (hardware, software, red, eléctrico, mecánico, otros)
- Equipo involucrado
- Ubicación
- Prioridad (crítica, alta, media, baja)
- Descripción detallada
- Fotos (opcional)
- Archivos adjuntos (opcional)

**Asignación Automática**:
- Análisis RAG para determinar especialidad requerida
- Asignación basada en carga laboral, especialidad y experiencia
- Escalamiento automático según prioridad

**Endpoints**:
- `POST /api/v1/grinding-peru/incidents` - Crear incidencia
- `GET /api/v1/grinding-peru/incidents` - Listar incidencias
- `GET /api/v1/grinding-peru/incidents/{id}` - Detalles de incidencia

**Ejemplo de uso**:
```json
{
  "tipo_falla": "hardware",
  "equipo_involucrado": "Servidor Principal",
  "ubicacion": "Data Center",
  "prioridad": "critica",
  "descripcion": "El servidor no responde a las peticiones",
  "fotos": ["foto1.jpg"],
  "archivos": ["log.txt"]
}
```

### 4. Asignación Automática de Tareas ✅

**Descripción**: Analizar las características de la incidencia para asignar automáticamente al técnico más adecuado según especialidad, carga laboral y disponibilidad.

**Algoritmo de Asignación**:
1. **Análisis RAG**: Determinar especialidad técnica requerida
2. **Filtrado**: Buscar técnicos con especialidad adecuada
3. **Scoring**: Calcular puntuación basada en:
   - Especialidad técnica (40%)
   - Carga laboral actual (30%)
   - Años de experiencia (20%)
   - Ubicación (10%)
4. **Asignación**: Seleccionar técnico con mayor puntuación

**Factores Considerados**:
- Especialidad técnica (hardware, software, red, eléctrico, mecánico)
- Carga laboral actual vs máxima
- Experiencia en años
- Proximidad geográfica
- Historial de resolución similar

### 5. Visualización y Actualización de Incidencias ✅

**Descripción**: Mostrar el estado actual de cada incidencia (pendiente, en proceso, finalizada) y permitir su actualización con comentarios, fotos y archivos.

**Estados de Incidencia**:
- Pendiente
- En Proceso
- Finalizada
- Cancelada

**Funcionalidades de Actualización**:
- Cambio de estado
- Comentarios con timestamps
- Subida de fotos
- Subida de archivos
- Historial de cambios
- Notificaciones automáticas

**Endpoints**:
- `PUT /api/v1/grinding-peru/incidents/{id}/update` - Actualizar incidencia
- `POST /api/v1/grinding-peru/incidents/{id}/assign` - Asignar manualmente

**Ejemplo de actualización**:
```json
{
  "estado": "en_proceso",
  "comentarios": "Iniciando diagnóstico del problema",
  "fotos": ["diagnostico1.jpg"],
  "archivos": ["diagnostico.txt"]
}
```

### 6. Panel Administrativo y de Auditoría ✅

**Descripción**: Supervisar el desempeño técnico, realizar auditorías internas y generar estadísticas para verificar cumplimiento de protocolos.

**Métricas del Panel**:
- Total de incidencias por período
- Tiempo promedio de resolución
- Cumplimiento de SLA por prioridad
- Incidencias por tipo de falla
- Desempeño por técnico
- Tendencias temporales

**Funcionalidades de Auditoría**:
- Log de todas las acciones del sistema
- Trazabilidad completa de cambios
- Filtros por usuario, acción y fecha
- Exportación de reportes de auditoría

**Endpoints**:
- `GET /api/v1/grinding-peru/admin/dashboard` - Dashboard administrativo
- `GET /api/v1/grinding-peru/admin/audit-logs` - Logs de auditoría
- `GET /api/v1/grinding-peru/admin/performance-metrics` - Métricas de rendimiento

### 7. Módulo de Predicción de Fallas Técnicas ✅

**Descripción**: Implementar un modelo de machine learning entrenado con datos históricos para anticipar fallas y generar alertas de mantenimiento preventivo.

**Modelos Implementados**:
- **Random Forest**: Predicción de fallas
- **Isolation Forest**: Detección de anomalías
- **Análisis de Tendencias**: Patrones temporales

**Características Analizadas**:
- Temperatura
- Vibración
- Presión
- Humedad
- Voltaje
- Corriente

**Funcionalidades**:
- Predicción de probabilidad de falla
- Detección de anomalías en tiempo real
- Recomendaciones de mantenimiento
- Alertas automáticas
- Dashboard de análisis predictivo

**Endpoints**:
- `POST /api/v1/grinding-peru/maintenance/predict/{equipment_id}` - Predecir falla
- `POST /api/v1/grinding-peru/maintenance/train-models` - Entrenar modelos
- `GET /api/v1/grinding-peru/maintenance/equipment/{id}/health` - Salud del equipo
- `GET /api/v1/grinding-peru/maintenance/predictive-dashboard` - Dashboard predictivo

### 8. Historial Técnico Consolidado por Equipo ✅

**Descripción**: Registrar el historial completo de mantenimiento por equipo, incluyendo tiempos, responsables, materiales utilizados y observaciones para trazabilidad.

**Información Registrada**:
- Tipo de mantenimiento (preventivo, correctivo, predictivo)
- Descripción detallada
- Técnico responsable
- Tiempo de inicio y fin
- Materiales utilizados
- Observaciones y recomendaciones
- Costo del mantenimiento
- Fotos y documentación

**Funcionalidades**:
- Búsqueda por equipo
- Filtros por tipo y fecha
- Estadísticas de mantenimiento
- Alertas de mantenimiento programado
- Análisis de costos

**Endpoints**:
- `POST /api/v1/grinding-peru/maintenance/record` - Registrar mantenimiento
- `GET /api/v1/grinding-peru/maintenance/equipment/{id}/history` - Historial del equipo

**Ejemplo de registro**:
```json
{
  "equipo_id": "equipment-uuid",
  "tipo_mantenimiento": "preventivo",
  "descripcion": "Mantenimiento mensual del servidor",
  "materiales_utilizados": ["Aire comprimido", "Paños de limpieza"],
  "observaciones": "Equipo en buen estado",
  "tiempo_inicio": "2024-01-15T08:00:00Z",
  "tiempo_fin": "2024-01-15T12:00:00Z"
}
```

### 9. Generación de Reportes Automáticos ✅

**Descripción**: Crear reportes visuales periódicos con indicadores como cantidad de incidencias, tipo de falla más frecuente, tiempo promedio de atención y reincidencias.

**Tipos de Reportes**:
1. **Resumen de Incidencias**
   - Total de incidencias por período
   - Incidencias por estado y prioridad
   - Tiempo promedio de resolución
   - Cumplimiento de SLA
   - Tendencias temporales

2. **Resumen de Mantenimiento**
   - Registros por tipo y equipo
   - Costos de mantenimiento
   - Eficiencia por técnico
   - Materiales más utilizados

3. **Salud de Equipos**
   - Estado actual de todos los equipos
   - Predicciones de falla
   - Recomendaciones de mantenimiento
   - Análisis de tendencias

4. **Métricas de Rendimiento**
   - KPIs del sistema
   - Desempeño por departamento
   - Satisfacción del usuario
   - Análisis de costos

**Endpoints**:
- `POST /api/v1/grinding-peru/reports/generate` - Generar reporte
- `GET /api/v1/grinding-peru/reports/incident-summary` - Reporte de incidencias
- `GET /api/v1/grinding-peru/reports/maintenance-summary` - Reporte de mantenimiento

## Características Adicionales Implementadas

### Seguridad y Auditoría
- Autenticación JWT con expiración
- Hash seguro de contraseñas
- Logs de auditoría completos
- Control de acceso basado en roles
- Validación de entrada en todos los endpoints

### Integración con RAG
- Análisis inteligente de incidencias
- Recomendaciones contextuales
- Clasificación automática
- Asignación inteligente de técnicos

### Machine Learning
- Predicción de fallas con Random Forest
- Detección de anomalías con Isolation Forest
- Análisis de tendencias temporales
- Recomendaciones de mantenimiento

### Notificaciones
- Alertas por email
- Notificaciones de Slack
- Integración con Microsoft Teams
- Escalamiento automático

### Métricas y KPIs
- Dashboard ejecutivo
- Métricas en tiempo real
- Análisis de tendencias
- Reportes de cumplimiento

## Instalación y Configuración

### 1. Instalación
```bash
cd grinding-peru
./install_grinding_peru.sh
```

### 2. Inicialización de Base de Datos
```bash
python scripts/init_enhanced_db.py
```

### 3. Ejecutar Aplicación
```bash
python main.py
```

### 4. Acceder al Sistema
- **API**: http://localhost:3000/api/v1/grinding-peru
- **Documentación**: http://localhost:3000/docs
- **Dashboard**: http://localhost:3000/api/v1/grinding-peru/admin/dashboard

### 5. Usuarios de Prueba
- **admin** / admin123 (Administrador)
- **supervisor1** / admin123 (Supervisor)
- **tecnico1** / admin123 (Técnico Hardware)
- **tecnico2** / admin123 (Técnico Software)

## Cumplimiento de Requerimientos

✅ **Inicio de sesión seguro** - Implementado con JWT y bcrypt
✅ **Gestión de usuarios y roles** - Tres roles con permisos específicos
✅ **Registro de incidencias** - Formulario completo con validación
✅ **Asignación automática** - Algoritmo inteligente con RAG
✅ **Visualización y actualización** - Estados y comentarios con archivos
✅ **Panel administrativo** - Dashboard con métricas y auditoría
✅ **Predicción de fallas** - ML con Random Forest e Isolation Forest
✅ **Historial técnico** - Registro completo con trazabilidad
✅ **Reportes automáticos** - Múltiples tipos con indicadores clave

El sistema está **100% funcional** y cumple con todos los requerimientos funcionales solicitados para Grinding Perú.
