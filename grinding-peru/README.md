# 🤖 Sistema de Soporte a la Decisión para Mantenimiento Predictivo
## Grinding Perú - Arequipa, 2025

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)](https://fastapi.tiangolo.com)
[![Supabase](https://img.shields.io/badge/Supabase-Database-orange.svg)](https://supabase.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-purple.svg)](https://openai.com)

## 📋 Descripción

Sistema inteligente de mantenimiento predictivo que implementa un **agente RAG (Retrieval-Augmented Generation)** para optimizar la gestión de mantenimiento en la empresa Grinding Perú.

## 🚀 Inicio Rápido en GitHub Codespaces

### **Opción 1: GitHub Codespaces (Recomendado)**

1. **Abrir en Codespaces**
   - Hacer clic en "Code" > "Codespaces" > "Create codespace"

2. **Configuración automática**
   ```bash
   ./scripts/codespace_setup.sh
   ```

3. **Iniciar sistema**
   ```bash
   ./start_system.sh
   ```

4. **Acceder al sistema**
   - **URL**: http://localhost:3000
   - **Documentación**: http://localhost:3000/docs

## ✨ Características Principales

### 🤖 **Agente Inteligente con RAG**
- Análisis contextual de incidencias
- Recomendaciones inteligentes
- Predicción de fallas con ML
- Detección de anomalías

### 👥 **Gestión de Usuarios**
- Administrador, Supervisor, Técnico
- Autenticación segura con JWT
- Roles diferenciados

### 🔧 **Recomendación Automática**
- Asignación inteligente de técnicos
- Análisis de carga de trabajo
- Optimización de recursos

### 📊 **Predicción y Análisis**
- Predicción de fallas
- Análisis de tendencias
- Alertas proactivas
- Cronogramas personalizados

## 🔑 Credenciales de Prueba

```
Administrador: admin / admin123
Supervisor: supervisor1 / admin123
Técnico: tecnico1 / admin123
```

## 🛠️ Tecnologías

- **Backend**: FastAPI + Python 3.9+
- **Base de Datos**: Supabase (PostgreSQL)
- **IA/ML**: OpenAI GPT-4, Scikit-learn
- **RAG**: LangChain, ChromaDB
- **Autenticación**: JWT, Bcrypt

## 📚 API Endpoints

### **Autenticación**
```http
POST /api/v1/auth/login
POST /api/v1/auth/register
```

### **Usuarios**
```http
GET /api/v1/grinding-peru/users
POST /api/v1/grinding-peru/users
```

### **Equipos**
```http
GET /api/v1/equipment
POST /api/v1/grinding-peru/equipment
```

### **Incidencias**
```http
GET /api/v1/incidents
POST /api/v1/incidents
PUT /api/v1/incidents/{id}
```

### **Predicciones**
```http
POST /api/v1/predictions/failure
POST /api/v1/predictions/anomaly-detection
```

### **Recomendaciones**
```http
POST /api/v1/technicians/recommendations
```

## 🎯 Casos de Uso

### **Caso 1: Incidencia Crítica**
- Registro automático
- Análisis inteligente
- Recomendación de técnico
- Asignación inmediata

### **Caso 2: Predicción de Falla**
- Análisis de sensores
- Detección de anomalías
- Predicción con probabilidad
- Alertas proactivas

## 🚀 Despliegue

### **GitHub Codespaces**
- ✅ Configuración automática
- ✅ Entorno preconfigurado
- ✅ Acceso inmediato

## 📞 Soporte

- **Documentación**: CODESPACE_README.md
- **API Docs**: http://localhost:3000/docs
- **Issues**: GitHub Issues

## 🎉 ¡Sistema Listo!

El sistema está completamente configurado y listo para optimizar el mantenimiento predictivo en Grinding Perú.

**¡Bienvenido al futuro del mantenimiento predictivo inteligente!** 🚀