# API EDI — Gestión de Tareas Studio & Plataforma de Despliegue

API REST funcional y Plataforma Web Interactiva para la **Gestión Integral de Tareas Registradas**, construida con **Flask + PostgreSQL / SQLite**, contenerizada con **Docker** y desplegable en **Render**.

---

## 1. Arquitectura del Sistema

```text
┌─────────────────────────────────────────────────────────────┐
│                    Cliente & Postman                        │
│   (Navegador Web / Postman Collection / Insomnia / cURL)   │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP (JSON / HTML5)
┌──────────────────────────────▼──────────────────────────────┐
│                    Contenedor app                           │
│          Flask 3 + Gunicorn + Interfaz UI                    │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
┌──────────────▼──────────────┐     ┌─────────▼──────────────┐
│ PostgreSQL / SQLite DB      │     │ Monitoreo en Render    │
│ Tabla 'tareas'              │     │ Endpoint /api/health   │
└─────────────────────────────┘     └────────────────────────┘
```

- **Backend & Web UI**: Flask 3 + Flask-SQLAlchemy + Marshmallow, servida por Gunicorn en producción.
- **Base de Datos**: PostgreSQL 16 en contenedor Docker / Render, con fallback automático a SQLite local (`edi.db`) si PostgreSQL no está en ejecución localmente.
- **Postman Collection**: `Api_EDI_Tasks.postman_collection.json` lista para importar.

---

## 2. Modelo de Datos — `tareas`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer (PK) | Identificador único serial |
| `codigo` | String(50) | Código único de referencia (ej: `TAR-001`, `EDI-850`) |
| `titulo` | String(150) | Título o nombre de la tarea |
| `descripcion` | Text | Descripción detallada o instrucciones de la tarea |
| `estado` | String(30) | `pendiente` · `en_progreso` · `suspendido` · `completado` |
| `prioridad` | String(30) | `baja` · `media` · `alta` · `critica` |
| `creado_en` | DateTime | Fecha y hora de creación (UTC) |
| `actualizado_en` | DateTime | Fecha y hora de última actualización |

---

## 3. Endpoints de la API REST

### Tareas (`/api/tareas`)
| Método | Ruta | Descripción |
|--------|------|-------------|
| **GET** | `/api/tareas` | Listar todas las tareas. Parámetros opcionales: `?q=`, `?estado=`, `?prioridad=` |
| **GET** | `/api/tareas/<id>` | Obtener una tarea por su ID |
| **POST** | `/api/tareas` | Registrar una nueva tarea |
| **PUT** | `/api/tareas/<id>` | Actualizar campos de una tarea existente |
| **PUT** | `/api/tareas/<id>/suspender` | Suspender (pausar) o reanudar una tarea |
| **DELETE** | `/api/tareas/<id>` | Eliminar una tarea de la base de datos |

### Utilidad
| Método | Ruta | Descripción |
|--------|------|-------------|
| **GET** | `/` | Interfaz Web Interactiva (o JSON de la API si solicita `Accept: application/json`) |
| **GET** | `/api/health` | Health check del servicio (`{"status": "healthy"}`) |

---

## 4. Uso de la Colección de Postman

El repositorio incluye la colección oficial de Postman:
📄 `Api_EDI_Tasks.postman_collection.json`

### Pasos para importar en Postman:
1. Abre **Postman** (o **Insomnia**).
2. Haz clic en **Import** $\rightarrow$ selecciona `Api_EDI_Tasks.postman_collection.json`.
3. La colección cargará las solicitudes agrupadas en:
   - **Utilidad & Salud:** `Health Check` e `Información de la API`.
   - **Tareas:** `Listar`, `Filtrar`, `Obtener`, `Crear`, `Actualizar`, `Suspender` y `Eliminar`.
4. La variable `{{base_url}}` viene configurada por defecto a `http://localhost:5000`. Puedes cambiarla a tu URL de Render (ej. `https://api-edi.onrender.com`).

---

## 5. Ejemplos de Peticiones con cURL

### 1. Registrar una Nueva Tarea (POST)
```bash
curl -X POST http://localhost:5000/api/tareas \
  -H "Content-Type: application/json" \
  -d '{
    "codigo": "TAR-100",
    "titulo": "Sincronizar servicio PostgreSQL",
    "descripcion": "Verificar tablas e índices en PostgreSQL",
    "prioridad": "alta",
    "estado": "pendiente"
  }'
```

### 2. Listar Tareas con Filtro (GET)
```bash
curl "http://localhost:5000/api/tareas?estado=pendiente&prioridad=alta"
```

### 3. Suspender / Pausar Tarea (PUT)
```bash
curl -X PUT http://localhost:5000/api/tareas/1/suspender
```

### 4. Actualizar Tarea (PUT)
```bash
curl -X PUT http://localhost:5000/api/tareas/1 \
  -H "Content-Type: application/json" \
  -d '{"prioridad": "critica", "estado": "en_progreso"}'
```

### 5. Eliminar Tarea (DELETE)
```bash
curl -X DELETE http://localhost:5000/api/tareas/1
```

---

## 6. Ejecución Local y Despliegue

### Con Docker Compose (PostgreSQL + App)
```bash
docker compose up --build -d
```
Accede a la interfaz web en: **http://localhost:5000**

### Sin Docker (Desarrollo directo en Python)
```bash
.venv\Scripts\python run.py
```
El servidor detectará si PostgreSQL está corriendo. Si no lo está, conmuta automáticamente a la base de datos local SQLite (`edi.db`) para que la aplicación inicie al 100% sin errores.

---

## 7. Ejecutar Pruebas Automatizadas
```bash
.venv\Scripts\python -m pytest
```
Resultado: **10/10 pruebas pasadas exitosamente (100%)**.