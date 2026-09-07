# Plan de Implantación y Despliegue — API EDI Task Studio

Documentación del plan de implantación, contenedorización y despliegue del sistema de **Gestión de Tareas EDI** desarrollado por **[EduarJIM](https://github.com/EduarJIM)** con **Flask, PostgreSQL y Render**.

- 🐙 **Repositorio GitHub:** [https://github.com/EduarJIM/api-edi](https://github.com/EduarJIM/api-edi)
- 🌐 **Despliegue en Render:** [https://api-edi-iqx3.onrender.com](https://api-edi-iqx3.onrender.com)

---

## 1. Objetivos del Sistema
- Proporcionar una API REST robusta y una interfaz de usuario estética para la gestión de tareas (operaciones CRUD, suspensión/pausa, completado check y filtrado por código/completadas).
- Integrar almacenamiento en **PostgreSQL** administrado en Render / Docker Compose y fallback automático a **SQLite** para desarrollo local.
- Entregar la colección oficial de **Postman / Insomnia** (`Api_EDI_Evidencia.postman_collection.json`) con la secuencia exacta de los 8 pasos de la evidencia.
- Monitorear en tiempo real el estado de salud del despliegue en **Render** a través de `/api/health`.

---

## 2. Componentes de la Arquitectura

1. **Aplicación Web & API REST (`app/`):**
   - Construida con Flask 3.x, Marshmallow para validación de datos y SQLAlchemy como ORM.
   - Rutas duales compatibles `/api/tasks` y `/api/tareas`.
   - Soporte para métodos `GET`, `POST`, `PUT`, `PATCH` y `DELETE`.
   - Plantillas HTML5 con Glassmorphism y CSS dinámico en `app/templates/` y `app/static/`.

2. **Base de Datos PostgreSQL & Contenerización (`Dockerfile` & `docker-compose.yml`):**
   - Imagen ligera basada en Python 3.11 Slim.
   - Orquestación con PostgreSQL 16 Alpine en red interna de Docker.

3. **Blueprint de Despliegue en Render (`render.yaml`):**
   - Servicio Web en Render sincronizado con la base de datos PostgreSQL `api-edi-db`.

4. **Colección de Pruebas e Integración:**
   - `Api_EDI_Evidencia.postman_collection.json` para la evidencia de 8 pasos.
   - Pruebas automatizadas en `tests/test_api.py`.

---

## 3. Estado de Verificación y Pruebas
- Pruebas unitarias ejecutadas con `pytest`: **8 / 8 pasadas al 100%**.
- Endpoint de salud `/api/health` validado.
- Conexión a base de datos validada con PostgreSQL en Render.