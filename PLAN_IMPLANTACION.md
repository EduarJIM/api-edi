# Plan de Implantación y Despliegue — API EDI Task Studio

Documentación del plan de implantación, contenedorización y despliegue del sistema de **Gestión de Tareas EDI** con **Flask, PostgreSQL y Render**.

---

## 1. Objetivos del Sistema
- Proporcionar una API REST robusta y una interfaz de usuario estética para la gestión de tareas (operaciones CRUD, suspensión/pausa, completado check y filtrado por código).
- Integrar almacenamiento en **PostgreSQL** para producción/Docker Compose y fallback a **SQLite** para desarrollo local rápido.
- Entregar una colección oficial de **Postman / Insomnia** para simplificar la integración.
- Monitorear en tiempo real el estado de salud del despliegue en **Render** a través de `/api/health`.

---

## 2. Componentes de la Arquitectura

1. **Aplicación Web & API REST (`app/`):**
   - Construida con Flask 3.x, Marshmallow para validación de datos y SQLAlchemy como ORM.
   - Plantillas HTML5 con Glassmorphism y CSS dinámico en `app/templates/` y `app/static/`.

2. **Base de Datos PostgreSQL & Contenerización (`Dockerfile` & `docker-compose.yml`):**
   - Imagen ligera basada en Python 3.11 Slim.
   - Orquestación con PostgreSQL 16 Alpine en red interna de Docker.

3. **Blueprint de Despliegue en Render (`render.yaml`):**
   - Servicio Web en Render sincronizado con la base de datos PostgreSQL `api-edi-db`.

4. **Colección de Pruebas de Integración:**
   - `Api_EDI_Tasks.postman_collection.json` para Postman / Insomnia.
   - Pruebas automatizadas en `tests/test_api.py`.

---

## 3. Estado de Verificación y Pruebas
- Pruebas unitarias ejecutadas con `pytest`: **10 / 10 pasadas al 100%**.
- Endpoint de salud `/api/health` validado.
- Conexión a base de datos validada con fallback transparente a SQLite local en desarrollo sin PostgreSQL.