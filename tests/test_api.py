def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "api-edi"


def test_paso2_crear_nueva_tarea_201(client):
    payload = {
        "title": "Aprender Postman y Docker",
        "description": "Prueba de creación de tarea para la evidencia",
        "completed": False,
    }
    response = client.post("/api/tasks", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Aprender Postman y Docker"
    assert data["description"] == "Prueba de creación de tarea para la evidencia"
    assert data["completed"] is False
    assert data["id"] is not None


def test_paso3_listar_todas_las_tareas_200(client):
    client.post("/api/tasks", json={"title": "Tarea 1", "completed": False})
    response = client.get("/api/tasks")
    assert response.status_code == 200
    tareas = response.get_json()
    assert isinstance(tareas, list)
    assert len(tareas) >= 1


def test_paso4_consultar_tarea_por_id_200(client):
    creado = client.post(
        "/api/tasks", json={"title": "Tarea Consulta", "description": "Detalle"}
    ).get_json()
    response = client.get(f"/api/tasks/{creado['id']}")
    assert response.status_code == 200
    assert response.get_json()["id"] == creado["id"]
    assert response.get_json()["title"] == "Tarea Consulta"


def test_paso5_actualizar_estado_patch_200(client):
    creado = client.post(
        "/api/tasks", json={"title": "Tarea a Completar", "completed": False}
    ).get_json()
    
    # PATCH completed: true
    response = client.patch(f"/api/tasks/{creado['id']}", json={"completed": True})
    assert response.status_code == 200
    data = response.get_json()
    assert data["completed"] is True
    assert data["estado"] == "completado"


def test_paso6_modificar_tarea_put_200(client):
    creado = client.post(
        "/api/tasks", json={"title": "Tarea Inicial", "completed": False}
    ).get_json()
    
    payload = {
        "title": "Tarea 100% Finalizada y Documentada",
        "description": "Desplegada en Render con PostgreSQL administrado",
        "completed": True,
    }
    response = client.put(f"/api/tasks/{creado['id']}", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Tarea 100% Finalizada y Documentada"
    assert data["description"] == "Desplegada en Render con PostgreSQL administrado"
    assert data["completed"] is True


def test_paso7_filtrar_tareas_completadas_query_param_200(client):
    client.post("/api/tasks", json={"title": "Tarea Incompleta", "completed": False})
    client.post("/api/tasks", json={"title": "Tarea Lista", "completed": True})

    response = client.get("/api/tasks?completed=true")
    assert response.status_code == 200
    tareas = response.get_json()
    assert all(t["completed"] is True for t in tareas)


def test_paso8_eliminar_tarea_delete_200(client):
    creado = client.post(
        "/api/tasks", json={"title": "Tarea a Eliminar", "completed": False}
    ).get_json()
    
    response = client.delete(f"/api/tasks/{creado['id']}")
    assert response.status_code == 200
    
    # Confirmar 404
    assert client.get(f"/api/tasks/{creado['id']}").status_code == 404