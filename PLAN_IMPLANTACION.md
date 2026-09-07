# Plan de Implantación — API EDI

Proyecto: **API EDI** (Flask + PostgreSQL + Docker)
Autor: Eduar JIM
Fecha de elaboración: 07/09/2026

---

## 1. Estrategia de implantación

**Tipo:** Implantación **directa** (por ser un proyecto pequeño y de un solo servicio acoplado a su base de datos).

Se justifica porque:
- La aplicación es un monolito sencillo (una API + una BD), sin dependencias escalonadas.
- El stack es reproducible con imágenes Docker versionadas.
- No existe una solución anterior que migrar (proyecto verde).

| Ventajas | Desventajas |
|----------|-------------|
| Rápida y simple | Corte total si solo hubiera una instancia |
| Coste mínimo (plan free de Render) | Sin balanceo automático en el plan free |
| Riesgo controlado (laboratorio) | Escalado manual |

## 2. Alcance

- API REST de proveedores, productos y pedidos (tipo EDI).
- Base de datos PostgreSQL 16.
- Despliegue local con Docker Compose.
- Despliegue en nube con Render (servicio web + PostgreSQL).

## 3. Cronograma

| Fase | Actividad | Duración | Fecha prevista | Estado |
|------|-----------|----------|----------------|--------|
| 1 | Desarrollo de la API (modelos, rutas, validación) | 2 h | 07/09/2026 | ✔ Completada |
| 2 | Pruebas unitarias y de integración (pytest) | 1 h | 07/09/2026 | ✔ Completada |
| 3 | Contenerización (Dockerfile + docker-compose.yml) | 1 h | 07/09/2026 | ✔ Completada |
| 4 | Despliegue local verificado (app + BD + Adminer) | 30 min | 07/09/2026 | ✔ Completada |
| 5 | Despliegue en la nube (Render) | 1 h | 07/09/2026 | ✔ Completada |
| 6 | Documentación (README + este plan) | 1 h | 07/09/2026 | ✔ Completada |

**Total estimado:** 4–6 horas (acorde al laboratorio).

## 4. Análisis de riesgos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Caída del servicio en Render por plan gratuito (sleep por inactividad) | Alta | Medio | Aceptar el retardo inicial; documentado en README; plan individual si se requiere |
| Pérdida de datos del volumen PostgreSQL | Media | Alto | Volumen persistente `postgres_data`; backup en Render (plan free no incluye, documentar) |
| Puerto en conflicto en local (5000/5432/8081) | Media | Bajo | Puertos de host difieren del contenedor (5433→5432, 8081→8080) |
| Fuga de secretos (`SECRET_KEY`, credenciales BD) | Baja | Alto | No commitear `.env`; `SECRET_KEY` generada en Render; credenciales por variables de entorno |
| Falla en el arranque por BD no lista | Baja | Medio | `depends_on: condition: service_healthy` + healthcheck de la app |
| Código roto tras cambios | Baja | Medio | Suite `pytest` (12 pruebas) ejecutable con un comando |

## 5. Actividades de implantación

1. **Preparación del entorno**
   - Git, Docker Desktop, Python 3.11+ verificados.
   - Repositorio en GitHub: `https://github.com/EduarJIM/api-edi`.
2. **Implantación local**
   - `docker compose up --build -d` → app en `http://localhost:5000`, BD en el contenedor `api-edu-postgres`, Adminer en `http://localhost:8081`.
   - Verificado: `GET /api/health` responde `{"status": "healthy"}`.
3. **Implantación en la nube (Render)**
   - Desplegado vía API de Render con la API key de la cuenta.
   - Render creó: base PostgreSQL `api-edi-db` (plan free, oregon) + web service `api-edi` (runtime docker, plan free).
   - App en **https://api-edi-iqx3.onrender.com** · BD en `dpg-dafgi4n40ujc73b71rfg-a.oregon-postgres.render.com:5432` (base `edi_db_yixs`, usuario `edi_db_yixs_user`).
   - Variables de entorno inyectadas por Render: `DATABASE_URL` (de la BD provista) y `SECRET_KEY` (generada).
   - Verificado end-to-end: `POST /api/proveedores` → 201 (registro insertado en la BD de Render).

## 6. Pruebas de aceptación

| N.º | Prueba | Resultado esperado | Resultado obtenido |
|-----|--------|--------------------|--------------------|
| 1 | Health check local | 200 `status: healthy` | ✔ |
| 2 | CRUD de proveedores | Crear/listar/actualizar/eliminar | ✔ (Postman) |
| 3 | CRUD de productos con FK a proveedor | Validación de proveedor | ✔ |
| 4 | Crear pedido EDI con detalles | Total calculado + descuento de stock | ✔ |
| 5 | Número EDI duplicado | HTTP 409 | ✔ |
| 6 | Suite pytest | 12/12 aprobadas | ✔ |
| 7 | Health check en Render | 200 desde `https://api-edi-iqx3.onrender.com/api/health` | ✔ |
| 8 | Ver BD (Adminer local y credenciales Render) | Consultar tablas creadas | ✔ |
| 9 | Escribir en la BD de Render desde la API | `POST /api/proveedores` → 201 | ✔ (proveedor id=1 creado) |

## 7. Evidencias (capturas)

> Las evidencias se recogen en la práctica presencial:
> 1. API funcionando en local — `http://localhost:5000/` (raíz con info) y `/api/health`.
> 2. `docker compose ps` mostrando los tres contenedores (`app`, `postgres`, `adminer`) en estado *healthy/running*.
> 3. Postman/Insomnia con una petición exitosa (ej. `POST /api/pedidos` 201).
> 4. URL de Render respondiendo `GET /api/health` → 200 en https://api-edi-iqx3.onrender.com.

## 8. Mantenimiento y operaciones

- **Reinicio local:** `docker compose down` y `docker compose up -d`.
- **Logs:** `docker compose logs -f app`.
- **Ver BD:** Adminer en `http://localhost:8081` (sistema PostgreSQL, servidor `postgres`, usuario `edi_user`, BD `edi_db`, clave `edi_pass`).
- **Repositorio:** `git pull` + `docker compose up --build -d` para actualizar.

## 9. Aprobación

| Rol | Nombre | Firma | Fecha |
|-----|--------|-------|-------|
| Responsable | Eduar JIM | | 07/09/2026 |