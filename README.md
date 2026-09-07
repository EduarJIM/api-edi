# API EDI — Gestión de Tareas Studio & Plataforma Cloud

[![Repository](https://img.shields.io/badge/GitHub-EduarJIM%2Fapi--edi-indigo?style=for-the-badge&logo=github)](https://github.com/EduarJIM/api-edi)
[![Deploy Status](https://img.shields.io/badge/Render-Live%20Deployment-emerald?style=for-the-badge&logo=render)](https://api-edi-iqx3.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-black?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?style=for-the-badge&logo=postgresql)](https://postgresql.org)
[![Postman Collection](https://img.shields.io/badge/Postman-Evidencia%208%20Pasos-orange?style=for-the-badge&logo=postman)](https://github.com/EduarJIM/api-edi/blob/main/Api_EDI_Evidencia.postman_collection.json)

Plataforma Web Interactiva y API REST para la **Gestión Integral de Tareas Registradas**, desarrollada por **[EduarJIM](https://github.com/EduarJIM)**. Construida con **Flask + PostgreSQL / SQLite**, contenerizada con **Docker** y desplegada en **Render Cloud**.

---

## 🔗 Enlaces Rápidos y Repositorio Oficial

- 🐙 **Repositorio GitHub:** [https://github.com/EduarJIM/api-edi](https://github.com/EduarJIM/api-edi)
- 🌐 **Aplicación Web & API (Render):** [https://api-edi-iqx3.onrender.com](https://api-edi-iqx3.onrender.com)
- 🟢 **Health Check en Vivo:** [https://api-edi-iqx3.onrender.com/api/health](https://api-edi-iqx3.onrender.com/api/health)
- 📄 **Colección de Postman Evidencia:** [`Api_EDI_Evidencia.postman_collection.json`](https://github.com/EduarJIM/api-edi/blob/main/Api_EDI_Evidencia.postman_collection.json)

---

## 🎨 Arquitectura del Sistema

```text
┌─────────────────────────────────────────────────────────────┐
│                    Cliente & Postman                        │
│   (Navegador Web / Postman Collection / Insomnia / cURL)   │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP (JSON / HTML5)
┌──────────────────────────────▼──────────────────────────────┐
│                    Contenedor app                           │
│          Flask 3 + Gunicorn + Interfaz UI (Glassmorphism)    │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
┌──────────────▼──────────────┐     ┌─────────▼──────────────┐
│ PostgreSQL (Render Cloud)   │     │ Monitoreo en Render    │
│ Tabla 'tareas'              │     │ Endpoint /api/health   │
└─────────────────────────────┘     └────────────────────────┘
```

---

## 📋 Modelo de Datos — `tareas`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer (PK) | Identificador único autoincremental |
| `codigo` | String(50) | Código único de referencia (ej: `TSK-001`, `EDI-850`) |
| `titulo` / `title` | String(150) | Título o nombre de la tarea |
| `descripcion` / `description` | Text | Descripción detallada o instrucciones de la tarea |
| `estado` | String(30) | `pendiente` · `en_progreso` · `suspendido` · `completado` |
| `completed` | Boolean | `true` si estado es completado, `false` en otro caso |
| `prioridad` | String(30) | `baja` · `media` · `alta` · `critica` |
| `creado_en` | DateTime | Timestamp de creación (UTC) |
| `actualizado_en` | DateTime | Timestamp de actualización |

---

## 🚀 Secuencia Completa de los 8 Pasos de Evidencia Postman

Todas las peticiones aceptan tanto las URLs locales (`http://localhost:5000`) como el servidor desplegado en **Render Cloud (`https://api-edi-iqx3.onrender.com`)**.

### 1. Health Check (`GET`)
```bash
curl -X GET https://api-edi-iqx3.onrender.com/api/health
```
**Código esperado:** `200 OK`
```json
{
  "service": "api-edi",
  "status": "healthy"
}
```

### 2. Crear Nueva Tarea (`POST`)
```bash
curl -X POST https://api-edi-iqx3.onrender.com/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Aprender Postman y Docker",
    "description": "Prueba de creación de tarea para la evidencia",
    "completed": false
  }'
```
**Código esperado:** `201 Created`

### 3. Listar Todas las Tareas (`GET`)
```bash
curl -X GET https://api-edi-iqx3.onrender.com/api/tasks
```
**Código esperado:** `200 OK`

### 4. Consultar Tarea por ID (`GET`)
```bash
curl -X GET https://api-edi-iqx3.onrender.com/api/tasks/1
```
**Código esperado:** `200 OK`

### 5. Actualizar Estado a Completada (`PATCH`)
```bash
curl -X PATCH https://api-edi-iqx3.onrender.com/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```
**Código esperado:** `200 OK`

### 6. Modificar Tarea por Completo (`PUT`)
```bash
curl -X PUT https://api-edi-iqx3.onrender.com/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tarea 100% Finalizada y Documentada",
    "description": "Desplegada en Render con PostgreSQL administrado",
    "completed": true
  }'
```
**Código esperado:** `200 OK`

### 7. Filtrar Tareas Completadas (`GET Query Params`)
```bash
curl -X GET "https://api-edi-iqx3.onrender.com/api/tasks?completed=true"
```
**Código esperado:** `200 OK`

### 8. Eliminar Tarea (`DELETE`)
```bash
curl -X DELETE https://api-edi-iqx3.onrender.com/api/tasks/1
```
**Código esperado:** `200 OK`

---

## 📩 Uso de la Colección de Postman

El repositorio incluye dos colecciones oficiales listas para importar en **Postman** o **Insomnia**:

1. **`Api_EDI_Evidencia.postman_collection.json`**: Contiene la secuencia exacta de los 8 pasos de la evidencia.
2. **`Api_EDI_Tasks.postman_collection.json`**: Colección completa para desarrolladores.

### Cómo Importar:
1. Abre **Postman** y selecciona **Import** (`Ctrl + O`).
2. Elige el archivo `Api_EDI_Evidencia.postman_collection.json`.
3. Ejecuta los pasos secuencialmente.

---

## 🛠️ Ejecución Local

```bash
# Clonar repositorio
git clone https://github.com/EduarJIM/api-edi.git
cd api-edi

# Crear entorno virtual e instalar dependencias
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt

# Iniciar servidor local
.venv\Scripts\python run.py
```
Abre en tu navegador: **http://localhost:5000**

---

## 🧪 Pruebas Automatizadas (Pytest)

```bash
.venv\Scripts\python -m pytest
```
Resultado: **8/8 pruebas pasadas exitosamente (100%)**.

---

## 👥 Autor

**EduarJIM** — *Creador y Propietario del Repositorio*
- GitHub: [@EduarJIM](https://github.com/EduarJIM)