# Agente Inteligente de Mantenimiento Predictivo con RAG

## Descripción
Sistema de mantenimiento predictivo basado en RAG (Retrieval-Augmented Generation) que utiliza Supabase como base de datos y GitHub para versionado.

## Características
- Análisis de datos en tiempo real
- Predicciones de mantenimiento usando ML
- Sistema de notificaciones inteligente
- API RESTful para integración
- Dashboard web para monitoreo

## Arquitectura
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Supabase DB   │◄───┤   RAG Agent     │◄───│   ML Models     │
│   (Time Series) │    │   (Analysis)    │    │   (Predictions) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Ingestion│    │  Notifications  │    │   Dashboard     │
│   (Real-time)   │    │   (Alerts)      │    │   (Monitoring)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Instalación
```bash
git clone <repository-url>
cd predictive-maintenance-rag
pip install -r requirements.txt
```

## Configuración
1. Configurar variables de entorno en `.env`
2. Configurar conexión a Supabase
3. Entrenar modelos de ML
4. Configurar notificaciones

## Uso
```bash
python main.py
```

## Contribución
1. Fork el proyecto
2. Crear feature branch
3. Commit cambios
4. Push al branch
5. Crear Pull Request
