# API EDI — Laboratorio de Dockerización, Implantación y Despliegue

API REST funcional para la gestión de **proveedores**, **productos** y **pedidos** (tipo EDI), construida con **Flask + PostgreSQL**, contenerizada con **Docker** y desplegable en **Render**.

---

## 1. Arquitectura

```
┌──────────────────────────────┐
│          Cliente             │
│   (Postman / Insomnia / curl)│
└──────────────┬───────────────┘
               │ HTTP (JSON)
┌──────────────▼───────────────┐      ┌──────────────────────┐
│        Contenedor app        │      │   Contenedor postgres │
│    Flask + Gunicorn :5000    │◄────►│   PostgreSQL :5432    │
└──────────────────────────────┘      └──────────────────────┘
                 docker-compose (red interna "compose default")
```

- **App**: Flask 3 + Flask-SQLAlchemy 2 + Marshmallow, servida por Gunicorn.
- **BD**: PostgreSQL 16 con volumen persistente (`postgres_data`).
- **Comunicación**: los servicios se descubren por nombre de contenedor (`postgres`) dentro de la red de Docker Compose.

---

## 2. Estructura del proyecto

```
Api EDI/                     # directorio del proyecto
├── app/
│   ├── __init__.py          # factory de Flask, registra blueprints
│   ├── config.py            # config por entorno (dev/prod/testing)
│   ├── models/
│   │   ├── proveedor.py     # modelo Proveedor
│   │   ├── producto.py      # modelo Producto (FK a proveedor)
│   │   ├── pedido.py        # modelo Pedido (número EDI, estado)
│   │   └── detalle_pedido.py# modelo línea de pedido
│   ├── routes/
│   │   ├── proveedores.py   # CRUD /api/proveedores
│   │   ├── productos.py     # CRUD /api/productos
│   │   └── pedidos.py       # CRUD /api/pedidos + detalles
│   └── schemas/
│       └── schemas.py       # validación con Marshmallow
├── tests/
│   ├── conftest.py          # fixtures con base SQLite en memoria
│   └── test_api.py          # pruebas del flujo completo
├── Dockerfile               # definición de la imagen de la app
├── docker-compose.yml       # orquestación app + postgres
├── render.yaml              # blueprint para despliegue en Render
├── requirements.txt         # dependencias Python
├── run.py                   # entry point (gunicorn run:app)
├── .env.example             # plantilla de variables de entorno
└── .gitignore
```

---

## 3. Modelo de datos

| Entidad | Campos clave |
|---------|--------------|
| `proveedores` | id, nombre, contacto, email (único), telefono, direccion, activo |
| `productos` | id, nombre, descripcion, precio, stock, categoria, **proveedor_id** (FK) |
| `pedidos` | id, numero_edi (único), estado, observaciones, **proveedor_id** (FK) |
| `detalle_pedidos` | id, **pedido_id** (FK), **producto_id** (FK), cantidad, precio_unitario |

Relaciones:
- `Proveedor 1—N Producto` (borrado en cascada)
- `Proveedor 1—N Pedido`
- `Pedido 1—N DetallePedido` (borrado en cascada)
- `Producto 1—N DetallePedido`

Al crear un pedido, el stock de cada producto se descuenta automáticamente; nunca baja de 0.

---

## 4. Endpoints

### Proveedores
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/proveedores` | Listar (filtros: `?nombre=`, `?activo=true`) |
| GET | `/api/proveedores/<id>` | Obtener uno |
| POST | `/api/proveedores` | Crear |
| PUT | `/api/proveedores/<id>` | Actualizar (parcial) |
| DELETE | `/api/proveedores/<id>` | Eliminar (409 si tiene dependencias) |

### Productos
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/productos` | Listar (filtros: `?categoria=`, `?proveedor_id=`, `?stock_minimo=`, `?nombre=`) |
| GET | `/api/productos/<id>` | Obtener uno |
| POST | `/api/productos` | Crear |
| PUT | `/api/productos/<id>` | Actualizar (parcial) |
| DELETE | `/api/productos/<id>` | Eliminar |

### Pedidos
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/pedidos` | Listar (filtros: `?proveedor_id=`, `?estado=`, `?numero_edi=`) |
| GET | `/api/pedidos/<id>` | Obtener con total y detalles |
| POST | `/api/pedidos` | Crear con `detalles[]` (JSON) |
| PUT | `/api/pedidos/<id>` | Actualizar (no permite reemplazar detalles) |
| DELETE | `/api/pedidos/<id>` | Eliminar |
| GET | `/api/pedidos/<id>/detalles` | Detalles del pedido |
| POST | `/api/pedidos/<id>/detalles` | Añadir línea (bloqueado si estado es enviado/cancelado) |

### Utilidad
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/health` | Health check |

### Notas sobre formato de salida
- Los montos monetarios (`precio`, `precio_unitario`, `subtotal`, `total`) se serializan como **números** en JSON (se implementa un `JSONProvider` que convierte `Decimal` a `float`), evitando strings innecesarios.
- `GET /api/pedidos/<id>` devuelve el total calculado y sus `detalles`.

### Estados válidos de pedido
`pendiente` · `enviado` · `recibido` · `cancelado`

---

## 5. Requisitos previos

- Git
- Docker Desktop (Windows/Mac) o Docker Engine (Linux)
- Postman / Insomnia (opcional, para probar)
- Cuenta gratuita en Render (para el despliegue)

Verifica la instalación:

```bash
git --version
docker --version
docker compose version
```

---

## 6. Ejecución local

### 6.1 Con Docker Compose (recomendado)

```bash
# Levantar app + base de datos
docker compose up --build -d

# Ver logs
docker compose logs -f app

# Comprobar health check
curl http://localhost:5000/api/health
```

La API queda disponible en: **http://localhost:5000**

Para detener:
```bash
docker compose down          # detiene contenedores
docker compose down -v       # además borra el volumen de la BD
```

### 6.2 Sin Docker (desarrollo local)

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt

# Necesitas PostgreSQL corriendo y una BD creada:
#   psql -U edi_user -c "CREATE DATABASE edi_db;"

# Copia la plantilla de entorno y ajusta DATABASE_URL si es necesario
copy .env.example .env        # Windows
cp .env.example .env          # Linux/Mac

python run.py
```

> En Render la app usa `gunicorn run:app`; el mercado de `DATABASE_URL` se define vía `render.yaml` o variables de entorno.

### 6.3 Ejecutar los tests

```bash
pip install -r requirements.txt
pytest -v
```

Los tests usan una base SQLite temporal (sin necesidad de PostgreSQL).

---

## 7. El Dockerfile explicado

```dockerfile
FROM python:3.11-slim            # base ligera
WORKDIR /app                     # directorio de trabajo
COPY requirements.txt .          # primero las dependencias = mejor caché
RUN pip install --no-cache-dir -r requirements.txt
COPY . .                         # código de la app
# Se crea usuario sin privilegios por seguridad (best practice)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 5000
# Healthcheck para que Docker/Render detecten caídas
HEALTHCHECK ... CMD python -c "urllib.request.urlopen('http://127.0.0.1:5000/api/health')"
# Crea las tablas y arranca Gunicorn (servidor de producción)
CMD ["sh", "-c", "flask --app run:app init-db && gunicorn --bind 0.0.0.0:5000 --workers 2 run:app"]
```

Orden de capas pensado para **maximizar la caché de capas** (dependencias antes que el código).

---

## 8. El docker-compose.yml explicado

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment: { POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB }
    ports: ["5433:5432"]      # 5433 en el host para no chocar con un postgres local
    volumes: [postgres_data:/var/lib/postgresql/data]   # persistencia
    healthcheck: pg_isready   # la app espera a que la BD esté lista
  app:
    build: .
    environment: { FLASK_ENV, DATABASE_URL, SECRET_KEY }
    ports: ["5000:5000"]
    depends_on:
      postgres:
        condition: service_healthy   # arranque ordenado
volumes:
  postgres_data:
```

- La app se conecta a `postgres` usando el nombre del *service* como host → `DATABASE_URL=postgresql://edi_user:edi_pass@postgres:5432/edi_db`.
- El `healthcheck` de la BD garantiza que la app no intente conectar antes de tiempo.

---

## 9. Despliegue en Render (gratuito, vía `render.yaml`)

El repositorio incluye `render.yaml`, un *Blueprint* que crea automáticamente la **base de datos PostgreSQL** y el **servicio web**.

### Opción A — Blueprint (automático, recomendado)

1. Sube el proyecto a GitHub:
   ```bash
   git init
   git add .
   git commit -m "API EDI - laboratorio Docker + Render"
   git remote add origin https://github.com/TU_USUARIO/api-edi.git
   git push -u origin main
   ```
2. Entra en [dashboard.render.com](https://dashboard.render.com).
3. **New + → Blueprint** → conecta el repo → Render lee `render.yaml`.
4. Render crea:
   - Base de datos PostgreSQL `api-edi-db` (plan free).
   - Servicio web `api-edi` (runtime docker, plan free).
5. Pulsa **Deploy** (o se auto-despliega con `autoDeploy: true`).
6. La app queda en una URL tipo `https://api-edi.onrender.com`.

### Opción B — Manual (sin Blueprint)

1. **New + → Web Service** → conecta el repo.
2. Runtime: **Docker** → Render usa tu `Dockerfile`.
3. Crea una base de datos: **New + → PostgreSQL** (plan free).
4. En el servicio web, *Environment* → añade:
   - `DATABASE_URL` → copiada del panel de la base PostgreSQL.
   - `SECRET_KEY` → generada (Render ofrece "Generate").
   - `FLASK_ENV=production`
5. **Deploy** y espera. Verifica `https://<tu-app>.onrender.com/api/health`.

### Notas para producción
- Cambia siempre `SECRET_KEY`.
- El plan free duerme el servicio tras inactividad (~15 min); el primer request tarda más.
- La conexión SSL de PostgreSQL de Render funciona con `psycopg2-binary` sin cambios.

---

## 10. Probar la API con Postman / Insomnia

Ejemplo de flujo completo:

**1. Crear un proveedor**
```
POST http://localhost:5000/api/proveedores
Content-Type: application/json

{
  "nombre": "Ferretería Central",
  "contacto": "Ana Gómez",
  "email": "ana@ferreteria.com",
  "telefono": "+34911000000",
  "direccion": "Av. Principal 45",
  "activo": true
}
```

**2. Crear un producto** (usa el `id` del proveedor devuelto)
```
POST http://localhost:5000/api/productos
{
  "nombre": "Tornillo 5mm",
  "descripcion": "Tornillo galvanizado",
  "precio": 0.35,
  "stock": 1000,
  "categoria": "Ferretería",
  "proveedor_id": 1
}
```

**3. Crear un pedido EDI** con sus líneas
```
POST http://localhost:5000/api/pedidos
{
  "numero_edi": "PO-850-0001",
  "estado": "pendiente",
  "observaciones": "Pedido mensual",
  "proveedor_id": 1,
  "detalles": [
    { "producto_id": 1, "cantidad": 200, "precio_unitario": 0.35 }
  ]
}
```

**4. Consultar el pedido** y su total
```
GET http://localhost:5000/api/pedidos/1
```

---

## 11. Comandos útiles de Docker

| Comando | Descripción |
|---------|-------------|
| `docker compose up --build -d` | Construye y levanta en segundo plano |
| `docker compose logs -f app` | Sigue los logs de la app |
| `docker compose ps` | Estado de los servicios |
| `docker compose down` | Detiene y borra contenedores |
| `docker compose down -v` | Igual + borra el volumen de datos |
| `docker compose restart app` | Reinicia solo la app |
| `docker exec -it api-edu-app bash` | Terminal dentro del contenedor app |
| `docker exec -it api-edu-postgres psql -U edi_user -d edi_db` | Consola SQL dentro de la BD |

---

## 12. Posibles errores y soluciones

| Problema | Causa | Solución |
|----------|-------|----------|
| `connection refused` al iniciar la app | La BD aún no estaba lista | `depends_on: condition: service_healthy` ya lo evita; revisa `docker compose logs postgres` |
| Puerto 5432 ocupado en el host | Hay un PostgreSQL local | El compose mapea a `5433` para evitarlo |
| `Email already exists` inesperado | Datos previos en la BD | `docker compose down -v` y vuelve a levantar |
| 409 al eliminar proveedor | Tiene productos/pedidos | Inactívalo (`activo: false`) o borra antes sus dependencias |
| El pedido no acepta detalles en PUT | Diseño intencional | Usa `POST /api/pedidos/<id>/detalles` o recrea el pedido |
| Tarda mucho el primer request en Render | Plan free duerme el servicio | Espera a que despierte (10-30 s) |

---

## 13. Verificación de objetivos (checklist del laboratorio)

- [ ] API REST funcional con almacenamiento en PostgreSQL (`docker compose up --build -d`).
- [ ] `Dockerfile` escrito y construido (`docker build -t api-edi .`).
- [ ] Orquestación de app + BD con `docker-compose.yml`.
- [ ] Despliegue local funcionando en `http://localhost:5000`.
- [ ] Despliegue en Render funcionando en `https://<tu-app>.onrender.com`.
- [ ] Documentación completada (este README).