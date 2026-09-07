def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "api-edi"


def test_listar_proveedores_vacio(client):
    response = client.get("/api/proveedores")
    assert response.status_code == 200
    assert response.get_json() == []


def test_crear_proveedor(client, proveedor_payload):
    response = client.post("/api/proveedores", json=proveedor_payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["nombre"] == "Proveedor Test"
    assert data["email"] == "juan@proveedor.com"
    assert data["id"] is not None


def test_crear_proveedor_email_duplicado(client, proveedor_payload):
    client.post("/api/proveedores", json=proveedor_payload)
    response = client.post("/api/proveedores", json=proveedor_payload)
    assert response.status_code == 409


def test_crear_proveedor_email_invalido(client, proveedor_payload):
    proveedor_payload["email"] = "correo-invalido"
    response = client.post("/api/proveedores", json=proveedor_payload)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_obtener_proveedor(client, proveedor_payload):
    creado = client.post("/api/proveedores", json=proveedor_payload).get_json()
    response = client.get(f"/api/proveedores/{creado['id']}")
    assert response.status_code == 200
    assert response.get_json()["id"] == creado["id"]


def test_obtener_proveedor_no_existe(client):
    response = client.get("/api/proveedores/9999")
    assert response.status_code == 404


def test_actualizar_proveedor(client, proveedor_payload):
    creado = client.post("/api/proveedores", json=proveedor_payload).get_json()
    response = client.put(
        f"/api/proveedores/{creado['id']}", json={"contacto": "Nuevo Contacto"}
    )
    assert response.status_code == 200
    assert response.get_json()["contacto"] == "Nuevo Contacto"


def test_eliminar_proveedor(client, proveedor_payload):
    creado = client.post("/api/proveedores", json=proveedor_payload).get_json()
    response = client.delete(f"/api/proveedores/{creado['id']}")
    assert response.status_code == 200
    eliminado = client.get(f"/api/proveedores/{creado['id']}")
    assert eliminado.status_code == 404


def test_crear_producto_requiere_proveedor_valido(client, proveedor_payload):
    response = client.post(
        "/api/productos",
        json={
            "nombre": "Martillo",
            "precio": 9.99,
            "proveedor_id": 999,
        },
    )
    assert response.status_code == 400


def test_flujo_completo_pedido(client, proveedor_payload):
    proveedor = client.post("/api/proveedores", json=proveedor_payload).get_json()

    producto = client.post(
        "/api/productos",
        json={
            "nombre": "Martillo",
            "descripcion": "Martillo de acero",
            "precio": 9.99,
            "stock": 50,
            "categoria": "Herramientas",
            "proveedor_id": proveedor["id"],
        },
    ).get_json()
    assert producto["precio"] == 9.99

    pedido = client.post(
        "/api/pedidos",
        json={
            "numero_edi": "ORD-001",
            "estado": "pendiente",
            "observaciones": "Pedido de prueba",
            "proveedor_id": proveedor["id"],
            "detalles": [
                {"producto_id": producto["id"], "cantidad": 3, "precio_unitario": 9.99}
            ],
        },
    ).get_json()
    assert pedido["numero_edi"] == "ORD-001"
    assert pedido["total"] == 29.97
    assert len(pedido["detalles"]) == 1

    detalle = client.get(f"/api/pedidos/{pedido['id']}/detalles").get_json()
    assert detalle[0]["subtotal"] == 29.97

    stock = client.get(f"/api/productos/{producto['id']}").get_json()
    assert stock["stock"] == 47


def test_pedido_con_numero_edi_duplicado(client, proveedor_payload):
    proveedor = client.post("/api/proveedores", json=proveedor_payload).get_json()
    producto = client.post(
        "/api/productos",
        json={
            "nombre": "Tornillos",
            "precio": 1.50,
            "stock": 100,
            "proveedor_id": proveedor["id"],
        },
    ).get_json()

    payload = {
        "numero_edi": "ORD-002",
        "proveedor_id": proveedor["id"],
        "detalles": [
            {"producto_id": producto["id"], "cantidad": 5, "precio_unitario": 1.50}
        ],
    }
    assert client.post("/api/pedidos", json=payload).status_code == 201
    response = client.post("/api/pedidos", json=payload)
    assert response.status_code == 409